import json
from os import lseek

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

from routing.matching.projection import project_onto_route, project_onto_route_new
from routing.matching.projection import get_extended_projected_linestring
from routing.matching.ml.utils import remove_duplicate_coordinates
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


class ExtendedProjectionVisResource(View):
    """ 
    Used to visualize the extended projection
    """

    def get(self, request, route_id, lsa_id):
        route = get_object_or_404(Route, pk=route_id)
        bindings = RouteLSABinding.objects.filter(route=route)

        connectionGeoJson = {
            "type": "FeatureCollection",
            "features": []
        }

        if lsa_id != "None":
            lsa = get_object_or_404(LSA, pk=lsa_id)
            lsa.geometry = remove_duplicate_coordinates(lsa.geometry)

            # Transform into projection system
            system_lsa_linestring = lsa.geometry.transform(
                settings.METRICAL, clone=True)
            system_route_linestring = route.geometry.transform(
                settings.METRICAL, clone=True)

            # Project the point (the center of the MAP topology linestring) to the route
            center_point_lsa = system_lsa_linestring.interpolate_normalized(
                0.5)
            distance_point_route = system_route_linestring.project(
                center_point_lsa)
            center_projected_point_on_route = system_route_linestring.interpolate(
                distance_point_route)

            linestring = LineString([center_point_lsa, center_projected_point_on_route],
                                    srid=system_lsa_linestring.srid).transform(settings.LONLAT, clone=True)
            connectionGeoJson["features"].append({
                "type": "Feature",
                "geometry": json.loads(linestring.json)
            })

            return cross_origin(JsonResponse(connectionGeoJson, safe=False))

        if bindings:
            for b in bindings:
                lsa = get_object_or_404(LSA, pk=b.lsa_id)
                lsa.geometry = remove_duplicate_coordinates(lsa.geometry)

                # Transform into projection system
                system_lsa_linestring = lsa.geometry.transform(
                    settings.METRICAL, clone=True)
                system_route_linestring = route.geometry.transform(
                    settings.METRICAL, clone=True)

                # Project the point (the center of the MAP topology linestring) to the route
                center_point_lsa = system_lsa_linestring.interpolate_normalized(
                    0.5)
                distance_point_route = system_route_linestring.project(
                    center_point_lsa)
                center_projected_point_on_route = system_route_linestring.interpolate(
                    distance_point_route)

                linestring = LineString([center_point_lsa, center_projected_point_on_route],
                                        srid=system_lsa_linestring.srid).transform(settings.LONLAT, clone=True)
                connectionGeoJson["features"].append({
                    "type": "Feature",
                    "geometry": json.loads(linestring.json)
                })
            return cross_origin(JsonResponse(connectionGeoJson, safe=False))

        matchers = [get_best_hypermodel()]
        matches = get_matches(route.geometry, matchers)

        for m in matches:
            lsa = get_object_or_404(LSA, pk=m.lsa_id)
            lsa.geometry = remove_duplicate_coordinates(lsa.geometry)

            # Transform into projection system
            system_lsa_linestring = lsa.geometry.transform(
                settings.METRICAL, clone=True)
            system_route_linestring = route.geometry.transform(
                settings.METRICAL, clone=True)

            # Project the point (the center of the MAP topology linestring) to the route
            center_point_lsa = system_lsa_linestring.interpolate_normalized(
                0.5)
            distance_point_route = system_route_linestring.project(
                center_point_lsa)
            center_projected_point_on_route = system_route_linestring.interpolate(
                distance_point_route)

            linestring = LineString([center_point_lsa, center_projected_point_on_route],
                                    srid=system_lsa_linestring.srid).transform(settings.LONLAT, clone=True)
            connectionGeoJson["features"].append({
                "type": "Feature",
                "geometry": json.loads(linestring.json)
            })

        return cross_origin(JsonResponse(connectionGeoJson, safe=False))


class BindingsConnectionsResource(View):
    def get(self, request, route_id, lsa_id):
        route = get_object_or_404(Route, pk=route_id)
        bindings = RouteLSABinding.objects.filter(route=route)

        params = request.GET

        method = params.get("method", "new")

        lsa_bindings = []

        if lsa_id != "None":
            lsa = get_object_or_404(LSA, pk=lsa_id)
            lsa.geometry = remove_duplicate_coordinates(lsa.geometry)

            lsa_projection = deepcopy(lsa)

            if method == "extended":
                lsa_projection.geometry = get_extended_projected_linestring(
                    lsa_projection.geometry, route.geometry)
            elif method == "old":
                lsa_projection.geometry = project_onto_route(
                    lsa_projection.geometry, route.geometry)
            elif method == "new":
                lsa_projection.geometry, lsa.geometry = project_onto_route_new(
                    lsa_projection.geometry, route.geometry)

            lsa_projection.id = "-" + lsa_projection.id
            lsa_bindings.append(lsa)

            lsa_bindings.append(lsa_projection)
            geojson = serialize("geojson", lsa_bindings,
                                geometry_field="geometry")
            return cross_origin(HttpResponse(geojson, content_type="application/json"))

        if bindings:
            for b in bindings:
                lsa = get_object_or_404(LSA, pk=b.lsa_id)
                lsa.geometry = remove_duplicate_coordinates(lsa.geometry)

                lsa_projection = deepcopy(lsa)

                if method == "extended":
                    lsa_projection.geometry = get_extended_projected_linestring(
                        lsa_projection.geometry, route.geometry)
                elif method == "old":
                    lsa_projection.geometry = project_onto_route(
                        lsa_projection.geometry, route.geometry)
                elif method == "new":
                    lsa_projection.geometry, lsa.geometry = project_onto_route_new(
                        lsa_projection.geometry, route.geometry)
                lsa_projection.id = "-" + lsa_projection.id
                lsa_bindings.append(lsa)
                lsa_bindings.append(lsa_projection)
            geojson = serialize("geojson", lsa_bindings,
                                geometry_field="geometry")
            return cross_origin(HttpResponse(geojson, content_type="application/json"))

        matchers = [get_best_hypermodel()]
        matches = get_matches(route.geometry, matchers)

        for m in matches:
            lsa = get_object_or_404(LSA, pk=m.lsa_id)
            lsa.geometry = remove_duplicate_coordinates(lsa.geometry)
            lsa_projection = deepcopy(lsa)

            if method == "extended":
                lsa_projection.geometry = get_extended_projected_linestring(
                    lsa_projection.geometry, route.geometry)
            elif method == "old":
                lsa_projection.geometry = project_onto_route(
                    lsa_projection.geometry, route.geometry)
            elif method == "new":
                lsa_projection.geometry, lsa.geometry = project_onto_route_new(
                    lsa_projection.geometry, route.geometry)
            lsa_projection.id = "-" + lsa_projection.id
            lsa_bindings.append(lsa)
            lsa_bindings.append(lsa_projection)
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
