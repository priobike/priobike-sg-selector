import json
import logging
from collections import namedtuple
from typing import Iterable, List
import time

import pyproj
from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from routing.matching import get_matches
from routing.matching.hypermodel import get_best_hypermodel
from routing.models import LSA, LSACrossing
from routing.matching.ml.matcher import MLMatcher
from routing.matching.proximity import ProximityMatcher


# The used ML-matcher when the endpoint for matching is called with the appropriate argument.
ml_matcher = MLMatcher()

class RouteJsonValidator:
    def __init__(self, route_json):
        self.route_json = route_json

    def validate(self, proj=settings.LONLAT) -> LineString:
        try:
            route_data = json.loads(self.route_json)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON")

        route = route_data.get("route")
        if not route:
            raise ValidationError("No route data")

        try:
            route_points = [(point["lon"], point["lat"], point["alt"]) for point in route]
        except KeyError:
            raise ValidationError("Invalid route data")

        try:
            route_linestring = LineString(route_points, srid=proj)
        except ValueError:
            raise ValidationError("Invalid route points")

        return route_linestring


LSASnap = namedtuple("LSASnap", [
    "lsa", # The associated LSA
    "point", # The snapped point, in WGS84
])


def snap_lsas(lsas: Iterable[LSA], route: LineString) -> List[LSASnap]:
    """
    Snap the LSAs to the route. Returns an unordered list of Snaps.
    """
    lonlat_route = route.transform(settings.LONLAT, clone=True)
    snapped_points = []
    for lsa in lsas:
        start_point = lsa.start_point.transform(settings.LONLAT, clone=True)
        snapped_point = lonlat_route.interpolate_normalized(lonlat_route.project_normalized(start_point))
        snapped_points.append(snapped_point)
    return [LSASnap(lsa, point) for lsa, point in zip(lsas, snapped_points)]


LSACrossingSnap = namedtuple("LSACrossingSnap", [
    "crossing", # The name of the crossing
    "point", # The snapped point, in WGS84
])


def snap_crossings(crossings: Iterable[LSACrossing], route: LineString) -> List[LSACrossingSnap]:
    """
    Snap the crossings to the route. Returns an unordered list of Snaps.
    """
    lonlat_route = route.transform(settings.LONLAT, clone=True)
    snapped_points = []
    for crossing in crossings:
        snapped_point = lonlat_route.interpolate_normalized(lonlat_route.project_normalized(crossing.point))
        snapped_points.append(snapped_point)
    return [LSACrossingSnap(crossing, point) for crossing, point in zip(crossings, snapped_points)]


def make_waypoints(
    lsa_snaps: Iterable[LSASnap], 
    crossing_snaps: Iterable[LSACrossingSnap], 
    route: LineString,
) -> List[dict]:
    """
    Make waypoints with the structure:
    {
        "lon": float,
        "lat": float,
        "alt": float,
        "distanceOnRoute": float,
        "distanceToNextSignal": float,
        "signalGroupId": str, (only if there is an upcoming signal and no disconnected crossing ahead)
    }
    """
    if not lsa_snaps and not route:
        return []

    # Throw snapped LSAs, disconnected crossings and route points into a list
    waypoints = [
        {"lon": s.point.x, "lat": s.point.y, "alt": s.point.z, "signalGroupId": s.lsa.lsametadata.signal_group_id} 
        for s in lsa_snaps
    ] + [
        # Mark disconnected crossings for post processing
        {"lon": s.point.x, "lat": s.point.y, "alt": s.point.z, "signalGroupId": "DISCONNECTED"}
        for s in crossing_snaps if not s.crossing.connected
    ] + [
        {"lon": x, "lat": y, "alt": z, "signalGroupId": None} 
        for x, y, z in route.coords
    ]
    
    # Order all waypoints by the direction of the route
    waypoints.sort(key=lambda w: route.project_normalized(Point(w["lon"], w["lat"], srid=settings.LONLAT)))
    
    # Use the WGS84 projection to calculate the distance between waypoints
    geod = pyproj.Geod(ellps="WGS84")

    # Accumulate distances along the route
    distance = 0
    prev = None
    for waypoint in waypoints:
        if prev:
            _, _, segment_distance = geod.inv(prev["lon"], prev["lat"], waypoint["lon"], waypoint["lat"])
            distance += segment_distance
        waypoint["distanceOnRoute"] = distance
        prev = waypoint
    
    # Accumulate distances to the next signal. For example:
    #     0,  10, 20, signal at 25, 30,   signal at 50, 60
    # --> 25, 15, 5,  0,            20,   0,            None 
    signal_waypoints = [w for w in waypoints if w["signalGroupId"]]
    n_signals = len(signal_waypoints)
    if signal_waypoints:
        signal_idx = 0
        for waypoint in waypoints:
            if waypoint["signalGroupId"]:
                # If we come across a signal waypoint, set the distance to 0 and switch to the next signal
                waypoint["distanceToNextSignal"] = 0
                signal_idx += 1
            elif n_signals > signal_idx:
                # When we have an upcoming signal, calculate the distance to the next signal
                waypoint["distanceToNextSignal"] = signal_waypoints[signal_idx]["distanceOnRoute"] - waypoint["distanceOnRoute"]
                # Annotate the waypoint with the signal group ID
                waypoint["signalGroupId"] = signal_waypoints[signal_idx]["signalGroupId"]
            else:
                # Otherwise, set the distance to None
                waypoint["distanceToNextSignal"] = None
                # Annotate the waypoint with the signal group ID
                waypoint["signalGroupId"] = None

    # Post process the waypoints. If there is a disconnected crossing ahead, set the signal group ID to None.
    # In this way we hide recommendations from the user until they are actually needed.
    for i, waypoint in enumerate(waypoints):
        if waypoint["signalGroupId"] == "DISCONNECTED":
            waypoints[i]["signalGroupId"] = None
    
    return waypoints


@method_decorator(csrf_exempt, name='dispatch')
class LSASelectionView(View):
    """
    View to find signal groups along a given route.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request.

        The body of the POST request should contain a route as follows:
        {
            "route": [
                { "lon": <longitude>, "lat": <latitude>, "alt": <altitude> },
                ...
            ]
        }
        """

        # Start time for the measurment of the time needed for the matching endpoint.
        startT = time.time()
        logging.debug(f"Received sg selection request with body: {request.body}")

        try:
            route_linestring = RouteJsonValidator(request.body).validate(proj=settings.LONLAT)
        except ValidationError as e:
            return JsonResponse({"error": str(e)})
        
        params = request.GET
        matcher = str(params.get("matcher", "legacy"))
        if matcher == "ml":
            unordered_lsas = get_matches(route_linestring, [ ProximityMatcher(search_radius_m=20), ml_matcher ]) 
        elif matcher == "legacy":
            unordered_lsas = get_matches(route_linestring, [get_best_hypermodel()])
        else:
            return JsonResponse({"error": "Unsupported value provided for the parameter 'matcher'. Choose between 'ml' or 'legacy'."})

        # Snap the LSA positions to the route as marked waypoints
        lsa_snaps = snap_lsas(unordered_lsas, route_linestring)

        # Get the disconnected crossings along the route
        crossings = LSACrossing.objects.filter(point__dwithin=(route_linestring, D(m=50)))
        crossing_snaps = snap_crossings(crossings, route_linestring)

        # Insert the snapped waypoints into the route
        waypoints = make_waypoints(lsa_snaps, crossing_snaps, route_linestring)

        # Create some signal group data
        signal_groups_json = {}
        for lsa in unordered_lsas:
            signal_groups_json[lsa.lsametadata.signal_group_id] = {
                "label": lsa.lsametadata.signal_group_id,
                "position": {
                    "lon": lsa.start_point.x,
                    "lat": lsa.start_point.y,
                },
                # Used to subscribe to the signal group
                "id": lsa.lsametadata.signal_group_id,
                "lsaId": lsa.id,
                "connectionId": lsa.lsametadata.connection_id,
                "laneType": lsa.lsametadata.lane_type,
                # Used by the app to subscribe to live data streams
                "datastreamDetectorCar": lsa.lsametadata.datastream_detector_car_id,
                "datastreamDetectorCyclists": lsa.lsametadata.datastream_detector_cyclists_id,
                "datastreamCycleSecond": lsa.lsametadata.datastream_cycle_second_id,
                "datastreamPrimarySignal": lsa.lsametadata.datastream_primary_signal_id,
                "datastreamSignalProgram": lsa.lsametadata.datastream_signal_program_id,
            }
        
        # Create some crossings data
        crossings_json = [
            {
                "name": s.crossing.name,
                "position": {
                    "lon": s.point.x,
                    "lat": s.point.y,
                },
                "connected": s.crossing.connected,
            } for s in crossing_snaps
        ]

        # Use the waypoint encoder to serialize the waypoints
        response_json = json.dumps({
            "route": waypoints,
            "signalGroups": signal_groups_json,
            "crossings": crossings_json,
        }, indent=2 if settings.DEBUG else None, ensure_ascii=False)
        
        print(f'Matching time: {time.time() - startT}ms')
        return HttpResponse(response_json, content_type="application/json")
