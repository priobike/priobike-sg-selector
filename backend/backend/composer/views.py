import json

from django.conf import settings
from django.contrib.gis.db.models import Extent, LineStringField
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.measure import D
from django.core.serializers import serialize
from django.db import transaction
from django.db.models import F
from django.db.models.aggregates import Count
from django.db.models.functions import Cast
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from routing.matching import get_matches
from routing.matching.hypermodel import get_best_hypermodel
from routing.models import SG, SGMetadata

from composer.models import Connection, Route, RouteSGBinding


def cross_origin(response):
    response["Access-Control-Allow-Origin"] = "*"
    return response


class RouteResource(View):
    def get(self, request, route_id):
        obj = get_object_or_404(Route, pk=route_id)
        geojson = serialize("geojson", [obj], geometry_field="geometry")
        return cross_origin(HttpResponse(geojson, content_type="application/json"))


class NextRouteResource(View):
    def get(self, request, route_id):
        next_route = Route.objects.filter(pk__gt=route_id).first()
        return cross_origin(JsonResponse({"next_route": next_route.pk if next_route else None}))


@method_decorator(csrf_exempt, name='dispatch')
class RouteBindingResource(View):
    def get(self, request, route_id, *args, **kwargs):
        route = get_object_or_404(Route, pk=route_id)
        bindings = RouteSGBinding.objects.filter(route=route)

        if bindings:
            return cross_origin(JsonResponse({
                "sgIds": [b.sg_id for b in bindings],
                "confirmed": [b.sg_id for b in bindings if b.confirmed],
            }, safe=False))

        matchers = [ get_best_hypermodel() ]
        matches = get_matches(route.geometry, matchers)

        return cross_origin(JsonResponse({
            "sgIds": [sg.id for sg in matches],
            "confirmed": [],
        }, safe=False))

    def post(self, request, route_id, *args, **kwargs):
        route = get_object_or_404(Route, pk=route_id)

        payload = json.loads(request.body)
        sg_ids = payload["sgIds"]
        confirmed_sg_ids = payload["confirmed"]

        bindings = [
            RouteSGBinding(route_id=route.id, sg_id=sg_id, confirmed=sg_id in confirmed_sg_ids)
            for sg_id in sg_ids
        ]

        # Update the bindings
        with transaction.atomic():
            RouteSGBinding.objects.filter(route=route).delete()
            RouteSGBinding.objects.bulk_create(bindings)

        # Dump the bindings
        with open(f"data/bindings/{route.id}.json", "w") as f:
            f.write(serialize("json", bindings, indent=2))

        return cross_origin(JsonResponse({"success": True}))

class ConnectionsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        connections = Connection.objects \
            .filter(sg__geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M)))
        geojson = serialize("geojson", connections, geometry_field="elevated_geometry")
        return cross_origin(HttpResponse(geojson, content_type="application/json"))


class ConnectionSegmentsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        connections = Connection.objects \
            .filter(sg__geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M)))
        trips = [ {
            "waypoints": [ {
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
                subsegment = LineString([last_point, point], srid=route.geometry.srid)
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
                current_distance += last_point.distance(point) if last_point is not None else 0
                progress = int((current_distance / total_distance) * 100)
                waypoints.append({
                    "coordinates": [*coord],
                    "progress": progress
                })
                last_point = point
            trips.append({"waypoints": waypoints})

        response = HttpResponse(json.dumps(trips), content_type="application/json")
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


class RouteCrossingsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        # Get all sgs within reach of the route
        sgs = SG.objects \
            .filter(geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M)))

        # Group by the associated crossing
        crossings = sgs \
            .select_related("sgmetadata") \
            .annotate(crossing_id=F("sgmetadata__traffic_lights_id")) \
            .values("crossing_id") \
            .annotate(count=Count("crossing_id")) \
            .order_by("crossing_id")

        results = []
        for crossing in crossings:
            # Use the Extent query to annotate the extent of each crossing
            # Note: the cast is necessary because the geometry is a geography type
            extent = sgs \
                .filter(sgmetadata__traffic_lights_id=crossing["crossing_id"]) \
                .annotate(cast_geometry=Cast("geometry", LineStringField())) \
                .aggregate(extent=Extent("cast_geometry"))
            results.append({
                "id": crossing["crossing_id"],
                "sgs": crossing["count"],
                "extent": extent["extent"]
            })

        return cross_origin(JsonResponse(results, safe=False))


class SGRegionResource(View):
    def get(self, request, sg_id):
        sg = get_object_or_404(SG, pk=sg_id)
        # Map the extent of the SG to an object dict
        extent = sg.geometry.extent
        object_dict = {
            "min_x": extent[0],
            "min_y": extent[1],
            "max_x": extent[2],
            "max_y": extent[3],
        }
        return cross_origin(JsonResponse(object_dict))


class SGMetadataResource(View):
    def get(self, request, sg_id):
        metadata = get_object_or_404(SGMetadata, sg_id=sg_id)
        # Cannot use model_to_dict due to datetime field
        object_dict = json.loads(serialize('json', [metadata]))[0]
        return cross_origin(JsonResponse(object_dict))
