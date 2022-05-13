import json
import logging
from collections import namedtuple
from typing import Iterable, List

import pyproj
from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from routing.matching import get_matches
from routing.matching.hypermodel import get_best_hypermodel
from routing.models import SG


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


Snap = namedtuple("Snap", [
    "sg", # The associated SG
    "point", # The snapped point, in WGS84
])


def snap(sgs: Iterable[SG], route: LineString) -> List[Snap]:
    """
    Snap the SGs to the route. Returns an unordered list of Snaps.
    """
    lonlat_route = route.transform(settings.LONLAT, clone=True)
    snapped_points = []
    for sg in sgs:
        start_point = sg.start_point.transform(settings.LONLAT, clone=True)
        snapped_point = lonlat_route.interpolate_normalized(lonlat_route.project_normalized(start_point))
        snapped_points.append(snapped_point)
    return [Snap(sg, point) for sg, point in zip(sgs, snapped_points)]


def make_waypoints(snaps: Iterable[Snap], route: LineString) -> List[dict]:
    """
    Make waypoints with the structure:
    {
        "lon": float,
        "lat": float,
        "alt": float,
        "distanceOnRoute": float,
        "distanceToNextSignal": float,
        "signalGroupId": str,
    }
    """
    if not snaps and not route:
        return []

    # Throw snapped SGs and route points into a list
    waypoints = [
        {"lon": s.point.x, "lat": s.point.y, "alt": s.point.z, "signalGroupId": s.sg.sgmetadata.signal_group_id} 
        for s in snaps
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
    
    return waypoints

@method_decorator(csrf_exempt, name='dispatch')
class SGSelectionView(View):
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
        logging.debug(f"Received sg selection request with body: {request.body}")

        try:
            route_linestring = RouteJsonValidator(request.body).validate(proj=settings.LONLAT)
        except ValidationError as e:
            return JsonResponse({"error": str(e)})

        matcher = get_best_hypermodel()
        unordered_sgs = get_matches(route_linestring, [matcher])

        # Snap the SG positions to the route as marked waypoints
        snaps = snap(unordered_sgs, route_linestring)

        # Insert the snapped waypoints into the route
        waypoints = make_waypoints(snaps, route_linestring)

        # Use the waypoint encoder to serialize the waypoints
        response_json = json.dumps({
            "waypoints": waypoints,
            "signals": [sg.serialize() for sg in unordered_sgs],
        }, indent=2 if settings.DEBUG else None)

        return HttpResponse(response_json, content_type="application/json")
