import json

from django.conf import settings
from django.core.serializers import serialize
from django.contrib.gis.geos import LineString, Point
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.gis.measure import D
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from routing.matching import get_matches
from routing.matching.hypermodel import get_best_hypermodel
from routing.models import LSA
from jiggle_vis.augmentation import jiggle_linestring

from copy import deepcopy

from composer.models import Connection, Route, RouteLSABinding


def cross_origin(response):
    response["Access-Control-Allow-Origin"] = "*"
    return response


class RouteResource(View):
    def get(self, request, route_id):
        obj = get_object_or_404(Route, pk=route_id)
        geojson = serialize("geojson", [obj], geometry_field="geometry")
        return cross_origin(HttpResponse(geojson, content_type="application/json"))


@method_decorator(csrf_exempt, name='dispatch')
class RouteBindingResource(View):
    def get(self, request, route_id, *args, **kwargs):
        route = get_object_or_404(Route, pk=route_id)
        bindings = RouteLSABinding.objects.filter(route=route)

        if bindings:
            return cross_origin(JsonResponse({
                "lsaIds": [b.lsa_id for b in bindings],
                "confirmed": [b.lsa_id for b in bindings if b.confirmed],
            }, safe=False))

        matchers = [get_best_hypermodel()]
        matches = get_matches(route.geometry, matchers)

        return cross_origin(JsonResponse({
            "lsaIds": [lsa.id for lsa in matches],
            "confirmed": [],
        }, safe=False))


class BindingsConnectionsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        bindings = RouteLSABinding.objects.filter(route=route)

        params = request.GET
        number_of_jiggled_lsas = int(params.get("numberOfJiggledLSAs", "1"))
        rotation_lower_bound = int(params.get("rotationLowerBound", "-3"))
        rotation_upper_bound = int(params.get("rotationUpperBound", "3"))
        scale_lower_bound = float(params.get("scaleLowerBound", "0.975"))
        scale_upper_bound = float(params.get("scaleUpperBound", "1.025"))
        translation_x_lower_bound = int(
            params.get("translationXLowerBound", "-5"))
        translation_x_upper_bound = int(
            params.get("translationXUpperBound", "5"))
        translation_y_lower_bound = int(
            params.get("translationYLowerBound", "-5"))
        translation_y_upper_bound = int(
            params.get("translationYUpperBound", "5"))

        lsa_bindings = []

        if bindings:
            for b in bindings:
                if b.confirmed:
                    lsa = get_object_or_404(LSA, pk=b.lsa_id)
                    lsa_bindings.append(lsa)
                    for i in range(number_of_jiggled_lsas):
                        lsa_jiggle = deepcopy(lsa)
                        lsa_jiggle.geometry = jiggle_linestring(geos_linestring=lsa_jiggle.geometry,
                                                                rotation_lower_bound=rotation_lower_bound, rotation_upper_bound=rotation_upper_bound,
                                                                scale_lower_bound=scale_lower_bound, scale_upper_bound=scale_upper_bound,
                                                                translation_x_lower_bound=translation_x_lower_bound, translation_x_upper_bound=translation_x_upper_bound,
                                                                translation_y_lower_bound=translation_y_lower_bound, translation_y_upper_bound=translation_y_upper_bound)
                        lsa_jiggle.id = "-" + lsa_jiggle.id
                        lsa_bindings.append(lsa_jiggle)
            geojson = serialize("geojson", lsa_bindings,
                                geometry_field="geometry")
            return cross_origin(HttpResponse(geojson, content_type="application/json"))

        matchers = [get_best_hypermodel()]
        matches = get_matches(route.geometry, matchers)

        for m in matches:
            lsa = get_object_or_404(LSA, pk=m.lsa_id)
            lsa_bindings.append(lsa)
            for i in range(number_of_jiggled_lsas):
                lsa_jiggle = deepcopy(lsa)
                lsa_jiggle.geometry = jiggle_linestring(geos_linestring=lsa_jiggle.geometry,
                                                        rotation_lower_bound=rotation_lower_bound, rotations_upper_bound=rotations_upper_bound,
                                                        scale_lower_bound=scale_lower_bound, scale_upper_bound=scale_upper_bound,
                                                        translation_x_lower_bound=translation_x_lower_bound, translation_x_upper_bound=translation_x_upper_bound,
                                                        translation_y_lower_bound=translation_y_lower_bound, translation_y_upper_bound=translation_y_upper_bound)
                lsa_jiggle.id = "-" + lsa_jiggle.id
                lsa_bindings.append(lsa_jiggle)
        geojson = serialize("geojson", lsa_bindings, geometry_field="geometry")
        return cross_origin(HttpResponse(geojson, content_type="application/json"))


class BindingsConnectionsSegmentsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        bindings = RouteLSABinding.objects.filter(route=route)

        lsa_bindings = []

        if bindings:
            for b in bindings:
                if b.confirmed:
                    lsa = get_object_or_404(LSA, pk=b.lsa_id)
                    lsa_bindings.append(lsa)

            trips = []
            prev_waypoint = None
            for lsa in lsa_bindings:

                for waypoint in lsa.geometry:
                    if prev_waypoint is not None:
                        trips.append({
                            "waypoints": [{
                                "progress": 0,
                                "coordinates": prev_waypoint
                            }, {
                                "progress": 100,
                                "coordinates": waypoint
                            }]
                        })
                    prev_waypoint = waypoint
                prev_waypoint = None
            trips_json = json.dumps(
                trips, indent=2 if settings.DEBUG else None)
            response = HttpResponse(
                trips_json, content_type="application/json")
            return cross_origin(response)

        matchers = [get_best_hypermodel()]
        matches = get_matches(route.geometry, matchers)

        for m in matches:
            lsa = get_object_or_404(LSA, pk=m.lsa_id)
            lsa_bindings.append(lsa)

        trips = []
        prev_waypoint = None
        for lsa in lsa_bindings:

            for waypoint in lsa.geometry:
                if prev_waypoint is not None:
                    trips.append({
                        "waypoints": [{
                            "progress": 0,
                            "coordinates": prev_waypoint
                        }, {
                            "progress": 0,
                            "coordinates": waypoint
                        }]
                    })
                prev_waypoint = waypoint
            prev_waypoint = None
        trips_json = json.dumps(trips, indent=2 if settings.DEBUG else None)
        response = HttpResponse(trips_json, content_type="application/json")
        return cross_origin(response)


class ConnectionsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        connections = Connection.objects \
            .filter(lsa__geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M)))
        geojson = serialize("geojson", connections,
                            geometry_field="elevated_geometry")
        return cross_origin(HttpResponse(geojson, content_type="application/json"))


class ConnectionSegmentsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        connections = Connection.objects \
            .filter(lsa__geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M)))
        trips = [{
            "waypoints": [{
                "progress": waypoint.progress,
                "coordinates": waypoint.elevated_geometry.coords
            } for waypoint in connection.waypoints.all()]
        } for connection in connections]
        trips_json = json.dumps(trips, indent=2 if settings.DEBUG else None)
        response = HttpResponse(trips_json, content_type="application/json")
        return cross_origin(response)


class RouteSegmentsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)

        # Split the route into subsegments
        subsegments = []
        last_point = None
        for coord in route.geometry.coords:
            point = Point(*coord, srid=route.geometry.srid)
            if last_point is not None:
                subsegment = LineString(
                    [last_point, point], srid=route.geometry.srid)
                subsegments.append(subsegment)
            last_point = point

        trips = []
        for segment in subsegments:
            waypoints = []
            last_point = None
            current_distance = 0
            total_distance = segment.length
            for coord in segment.coords:
                point = Point(*coord, srid=route.geometry.srid)
                current_distance += last_point.distance(
                    point) if last_point is not None else 0
                progress = int((current_distance / total_distance) * 100)
                waypoints.append({
                    "coordinates": [*coord],
                    "progress": progress
                })
                last_point = point
            trips.append({"waypoints": waypoints})

        response = HttpResponse(json.dumps(
            trips), content_type="application/json")
        return cross_origin(response)


class RouteRegionResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        # Map the extent of the route to an object dict
        extent = route.geometry.extent
        object_dict = {
            "min_x": extent[0],
            "min_y": extent[1],
            "max_x": extent[2],
            "max_y": extent[3],
        }
        return cross_origin(JsonResponse(object_dict))
