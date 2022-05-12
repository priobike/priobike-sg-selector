import json
import logging
from collections import namedtuple
from typing import Iterable, List

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
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
    "snapped_point", # The snapped point, in WGS84
    "route_distance", # The projected distance on the route, in meters
])


def snap(sgs: Iterable[SG], route: LineString) -> List[Snap]:
    """
    Snap the SGs to the route. Returns the snapped SGs in the order of the route.
    """
    metrical_route = route.transform(settings.METRICAL, clone=True)

    snapped_points = []
    route_distances = []
    for sg in sgs:
        start_point = sg.start_point.transform(settings.METRICAL, clone=True)
        route_distance = metrical_route.project(start_point)
        snapped_point = metrical_route.interpolate(route_distance)
        snapped_point_wgs84 = snapped_point.transform(settings.LONLAT, clone=True)

        snapped_points.append(snapped_point_wgs84)
        route_distances.append(route_distance)

    return [
        Snap(sg, snapped_point, route_distance) for sg, snapped_point, route_distance in
        sorted(zip(sgs, snapped_points, route_distances), key=lambda x: x[2])
    ]


def make_waypoints(snaps: Iterable[Snap], route: LineString) -> List[dict]:
    if snaps:
        sgs, sg_points, sg_distances = map(list, (zip(*snaps)))
    else:
        sgs, sg_points, sg_distances = [], [], []
    route_m = route.transform(settings.METRICAL, clone=True)
    route_lonlat = route.transform(settings.LONLAT, clone=True)

    waypoints = []
    for (lon, lat, alt), (x, y, z) in zip(route_lonlat, route_m):
        # Check how far the point is from the start of the route, in meters
        point = Point(x, y, z, srid=route_m.srid)
        distance = route_m.project(point)

        # If we surpassed SGs, we need to add them as matches
        # and remove them from the list of upcoming sgs
        while sgs and sg_points and sg_distances and distance > sg_distances[0]:
            surpassed_sg, surpassed_sg_point, _ = sgs.pop(0), sg_points.pop(0), sg_distances.pop(0)
            waypoints.append({
                "lon": surpassed_sg_point[0],
                "lat": surpassed_sg_point[1],
                "alt": surpassed_sg_point[2],
                "distanceToNextSignal": 0,
                "nextSignal": surpassed_sg.id,
            })

        if not sgs or not sg_points or not sg_distances:
            # If there is no next SG, we can't match the point to any SG
            waypoints.append({
                "lon": lon,
                "lat": lat,
                "alt": alt,
                "distanceToNextSignal": None,
                "nextSignal": None,
            })
        else:
            waypoints.append({
                "lon": lon,
                "lat": lat,
                "alt": alt,
                "distanceToNextSignal": sg_distances[0] - distance,
                "nextSignal": sgs[0].id,
            })

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
