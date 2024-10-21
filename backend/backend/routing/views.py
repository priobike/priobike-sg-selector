import json
import logging
import time
from collections import namedtuple
from typing import Iterable, List

import pyproj
from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.measure import D
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError, JsonResponse
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from routing.matching import get_matches
from routing.matching.bearing import get_bearing
from routing.matching.hypermodel import TopologicHypermodelMatcher
from routing.matching.ml.matcher import MLMatcher
from routing.matching.projection import project_onto_route
from routing.matching.proximity import ProximityMatcher
from routing.matching_multi_lane.matcher import MultiLaneMatcher
from routing.models import LSA, LSACrossing


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

def get_sg_distances_on_route(sgs: Iterable[LSA], route: LineString) -> List[dict]:
    """
    Snap the SGs to the route. Returns an unordered list of SGs and their absolute distances on the route with the following structure:
    [{
        "id": string,
        "position": {
            "lon": float,
            "lat": float,
        },
        "projectedLenghtOnRoute": float,
        "bearingStart": float,
        "bearingEnd": float,
        "distanceOnRoute": float,
        "laneType": string,
    }]
    """
    meter_route = route.transform(settings.METRICAL, clone=True)
    sg_distances_on_route = []
    sg_projected_lengths_on_route = []
    for sg in sgs:
        start_point = sg.start_point.transform(settings.METRICAL, clone=True)
        distance_on_route = meter_route.project_normalized(start_point)
        sg_distances_on_route.append(distance_on_route)
        
        sg = sg.geometry.transform(settings.METRICAL, clone=True)
        sg_projected = project_onto_route(sg, route)
        sg_projected_lengths_on_route.append(sg_projected.length)
    return [
        {
            "id": sg.lsametadata.signal_group_id, 
            "position": {
                "lon": sg.start_point.x,
                "lat": sg.start_point.y,
            },
            "projectedLengthOnRoute": sg_projected_length_on_route,
            "bearingStart": get_bearing(sg.geometry.coords[0][0], sg.geometry.coords[0][1], sg.geometry.coords[1][0], sg.geometry.coords[1][1]),
            "bearingEnd": get_bearing(sg.geometry.coords[-2][0], sg.geometry.coords[-2][1], sg.geometry.coords[-1][0], sg.geometry.coords[-1][1]),
            "distanceOnRoute": distance,
            "laneType": sg.lsametadata.lane_type,
        }
        for sg, distance, sg_projected_length_on_route in zip(sgs, sg_distances_on_route, sg_projected_lengths_on_route)]


def get_crossing_distances_on_route(crossings: Iterable[LSACrossing], route: LineString) -> List[dict]:
    """
    Snap the crossings to the route. Returns an unordered list of crossings and their absolute distances on the route with the following structure:
    [{
        "name": string,
        "position": {
            "lon": float,
            "lat": float,
        },
        "distanceOnRoute": float,
        "connected": boolean,
    }]
    """
    lonlat_route = route.transform(settings.METRICAL, clone=True)
    crossing_distances_on_route = []
    for crossing in crossings:
        start_point = crossing.point.transform(settings.METRICAL, clone=True)
        distance_on_route = lonlat_route.project(start_point)
        crossing_distances_on_route.append(distance_on_route)
    return [
        {
            "name": crossing.name,
            "position": {
                "lon": crossing.point.x,
                "lat": crossing.point.y,
            },
            "distanceOnRoute": distance,
            "connected": crossing.connected,
        }
        for crossing, distance in zip(crossings, crossing_distances_on_route)]


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
        usedRouting = str(params.get("routing", "osm"))
        
        if usedRouting != "osm" and usedRouting != "drn":
            return JsonResponse({"error": "Unsupported value provided for the parameter 'routing'. Choose between 'osm' or 'drn'."})

        if route_linestring.simple:
            route_parts = [route_linestring]
        else:
            # If the route crosses itself, we split it into parts and match each part separately.
            # Each part is buffered a bit to make sure the parts keep crossing the intersection fully.
            unary_union = route_linestring.unary_union # multilinestring
            route_parts = []
            buffer = 100 # distance in meter
            buffer_wgs84 = buffer / 40000000.0 * 360.0 # wgs84
            for part in unary_union:
                buffered = route_linestring.intersection(part.buffer(buffer_wgs84))
                route_parts.append(buffered)

        unordered_lsas = None # or queryset
        for route_part in route_parts: # one part if the route does not cross itself, otherwise multiple buffered parts
            if matcher == "ml":
                matches = get_matches(route_part, [ ProximityMatcher(search_radius_m=20), MLMatcher(usedRouting) ]) 
            elif matcher == "legacy":
                matches = get_matches(route_part, [ TopologicHypermodelMatcher.from_config_file(f'config/topologic.hypermodel.{usedRouting}.updated.json') ])
            else:
                return JsonResponse({"error": "Unsupported value provided for the parameter 'matcher'. Choose between 'ml' or 'legacy'."})
            if unordered_lsas is None:
                unordered_lsas = matches
            else:
                # Remove duplicates from the matches. This may happen when the route crosses itself.
                unordered_lsas = unordered_lsas.union(matches)

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
                "bearing": lsa.bearing,
                "geometry": lsa.geometry.coords,
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
    
@method_decorator(csrf_exempt, name='dispatch')
class MultiLaneSelectionView(View):
    """
    View to find signal groups along a given route (multiple lanes).
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request.
        
        The body of the POST request should contain the route as follows:
        {
            "route": [
                { "lon": <longitude>, "lat": <latitude>, "alt": <altitude> },
                ...
            ]
        }
        """
        
        logging.debug(f"Received multi lane sg selection request with body: {request.body}")

        try:
            route_linestring = RouteJsonValidator(request.body).validate(proj=settings.LONLAT)
        except ValidationError as e:
            return JsonResponse({"error": str(e)})
        
        params = request.GET
        bearing_diff = int(params.get("bearingDiff", 30))
        distance_to_route = int(params.get("distanceToRoute", 20))
        
        # If the route is too short, don't perform matching.
        if len(route_linestring.coords) < 2:
            return JsonResponse({"error": "Not enough waypoints in the route."})
        
        matched_unordered_sgs = MultiLaneMatcher(route_linestring).match(distance_to_route, bearing_diff)
                
        # Snap the SG positions to the route and get their distances on the route
        sg_distances_on_route = get_sg_distances_on_route(matched_unordered_sgs, route_linestring)
        sg_distances_on_route.sort(key=lambda x: x["distanceOnRoute"])
        
        # Snap the disconnected crossings to the route and get their distances on the route
        crossings = LSACrossing.objects.filter(point__dwithin=(route_linestring, D(m=distance_to_route)))
        crossings_distances_on_route = get_crossing_distances_on_route(crossings, route_linestring)
        crossings_distances_on_route.sort(key=lambda x: x["distanceOnRoute"])

         # Serialize the data
        response_json = json.dumps({
            "signalGroups": sg_distances_on_route,
            "crossings": crossings_distances_on_route,
        }, indent=2 if settings.DEBUG else None, ensure_ascii=False)
        
        return HttpResponse(response_json, content_type="application/json")
    
    
    
        
        
        
