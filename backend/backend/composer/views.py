import json
import os

from django.conf import settings
from django.contrib.gis.db.models import Extent, LineStringField
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.measure import D
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.db import transaction
from django.db.models import F
from django.db.models.aggregates import Count
from django.db.models.functions import Cast
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from composer.utils import check_binding_exists
from routing.matching.projection import project_onto_route
from routing.matching import get_matches
from routing.matching.hypermodel import get_best_hypermodel
from routing.models import LSA, LSAMetadata

from composer.models import Connection, Route, RouteLSABinding, Constellation, RouteError


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
        bindings = RouteLSABinding.objects.filter(route=route)

        if bindings:
            response = {}
            for b in bindings:
                response[b.lsa_id] = {
                    "confirmed": b.confirmed,
                    "corresponding_constellation": b.corresponding_constellation.id if b.corresponding_constellation is not None else None,
                    "corresponding_route_error": b.corresponding_route_error.id if b.corresponding_route_error is not None else None
                }
            return cross_origin(JsonResponse(response, safe=False))

        matchers = [get_best_hypermodel()]
        matches = get_matches(route.geometry, matchers)

        params = request.GET

        # param that determines whether only matches should be returned, if there are no duplicates among them
        show_duplicates = True
        if params.get("show_duplicates", "true") == u'false':
            show_duplicates = False

        all_bindings = RouteLSABinding.objects.all()
        duplicates = False
        response = {}
        for m in matches:

            lsa_linestring = m.geometry.transform(settings.LONLAT, clone=True)
            route_linestring = route.geometry.transform(
                settings.LONLAT, clone=True)
            lsa_linestring_projected = project_onto_route(
                lsa_linestring, route_linestring)

            if not show_duplicates and check_binding_exists(lsa_linestring_projected, m.id, all_bindings):
                duplicates = True
            response[m.id] = {
                "confirmed": False,
                "corresponding_constellation": None,
                "corresponding_route_error": None
            }

        # Return empty dict, if no duplicates should be shown (show_duplicates == false) and at least one duplicate got found found (duplicates == true).
        # Returning an empty dict indicates in that case that we don't want to use this route for further bindings because we decided that we don't want duplicates and
        # therefore we can save the work to create bindings for that route that in the ende wouldn't get used anyway.
        return cross_origin(JsonResponse(response if show_duplicates or not duplicates else {}, safe=False))

    def post(self, request, route_id, *args, **kwargs):
        route = get_object_or_404(Route, pk=route_id)
        
        # Depending on this Query parameters the directory to save the bindings gets chosen. 
        params = request.GET
        map_data = str(params.get("map_data", "osm"))

        payload = json.loads(request.body)
        print(payload)
        bindings = [RouteLSABinding(route_id=route.id,
                                    lsa_id=lsa_id,
                                    confirmed=values["confirmed"],
                                    corresponding_constellation_id=values[
                                        "corresponding_constellation"] if "corresponding_constellation" in values else None,
                                    corresponding_route_error_id=values["corresponding_route_error"] if "corresponding_route_error" in values else None) for lsa_id, values in payload.items()]
        
        # Dump the bindings    
        if map_data == "osm":
            with open(f"../data/bindings/{route.id}.json", "w") as f:
                f.write(serialize("json", bindings, indent=2))
        elif map_data == "drn":
            with open(f"../data/bindings_drn/{route.id}.json", "w") as f:
                f.write(serialize("json", bindings, indent=2))
        else:
            return JsonResponse({"error": "Unsupported value provided for the parameter 'map_data'. Choose between 'osm' or 'drn'."})

        # Update the bindings in the database
        with transaction.atomic():
            RouteLSABinding.objects.filter(route=route).delete()
            RouteLSABinding.objects.bulk_create(bindings)

        return cross_origin(JsonResponse({"success": True}))


class ConnectionsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)

        params = request.GET

        # param that determines whether only connections should be returned, if there are no duplicates among them
        show_duplicates = True
        if params.get("show_duplicates", "true") == u'false':
            show_duplicates = False

        connections = Connection.objects \
            .filter(lsa__geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M)))

        # just return all connections
        if show_duplicates:
            geojson = serialize("geojson", connections,
                                geometry_field="elevated_geometry")
            return cross_origin(HttpResponse(geojson, content_type="application/json"))

        # check for duplicates
        all_bindings = RouteLSABinding.objects.all()
        duplicates = False
        for connection in connections:
            lsa_linestring = connection.lsa.geometry.transform(
                settings.LONLAT, clone=True)
            route_linestring = route.geometry.transform(
                settings.LONLAT, clone=True)
            lsa_linestring_projected = project_onto_route(
                lsa_linestring, route_linestring)
            if check_binding_exists(lsa_linestring_projected, connection.lsa.id, all_bindings):
                duplicates = True
                break

        # if a duplicate was found, don't return any connections
        if duplicates:
            return cross_origin(JsonResponse({}, safe=False))

        # if no duplicate was found, return all connections
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
                progress = int((current_distance / total_distance) * 100) if total_distance > 0 else 0
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


class RouteCrossingsResource(View):
    def get(self, request, route_id):
        route = get_object_or_404(Route, pk=route_id)
        # Get all lsas within reach of the route
        lsas = LSA.objects \
            .filter(geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M)))

        # Group by the associated crossing
        crossings = lsas \
            .select_related("lsametadata") \
            .annotate(crossing_id=F("lsametadata__traffic_lights_id")) \
            .values("crossing_id") \
            .annotate(count=Count("crossing_id")) \
            .order_by("crossing_id")

        results = []
        for crossing in crossings:
            # Use the Extent query to annotate the extent of each crossing
            # Note: the cast is necessary because the geometry is a geography type
            extent = lsas \
                .filter(lsametadata__traffic_lights_id=crossing["crossing_id"]) \
                .annotate(cast_geometry=Cast("geometry", LineStringField())) \
                .aggregate(extent=Extent("cast_geometry"))
            results.append({
                "id": crossing["crossing_id"],
                "lsas": crossing["count"],
                "extent": extent["extent"]
            })

        return cross_origin(JsonResponse(results, safe=False))


class LSARegionResource(View):
    def get(self, request, lsa_id):
        lsa = get_object_or_404(LSA, pk=lsa_id)
        # Map the extent of the LSA to an object dict
        extent = lsa.geometry.extent
        object_dict = {
            "min_x": extent[0],
            "min_y": extent[1],
            "max_x": extent[2],
            "max_y": extent[3],
        }
        return cross_origin(JsonResponse(object_dict))


class LSAMetadataResource(View):
    def get(self, request, lsa_id):
        metadata = get_object_or_404(LSAMetadata, lsa_id=lsa_id)
        # Cannot use model_to_dict due to datetime field
        object_dict = json.loads(serialize('json', [metadata]))[0]
        return cross_origin(JsonResponse(object_dict))


class ConstellationResource(View):
    def get(self, request, constellation_id):
        constellation = get_object_or_404(Constellation, pk=constellation_id)
        return cross_origin(JsonResponse(model_to_dict(constellation), safe=False))


class ConstellationStatsResource(View):
    def get(self, request, constellation_id):
        constellation = get_object_or_404(Constellation, pk=constellation_id)
        bindings = RouteLSABinding.objects.filter(
            corresponding_constellation=constellation)
        bindings_json = serialize('json', bindings)
        return cross_origin(HttpResponse(bindings_json, content_type='application/json'))


class ConstellationAllResource(View):
    def get(self, request):
        constellations = Constellation.objects.all()
        constellations_json = serialize('json', constellations)
        return cross_origin(HttpResponse(constellations_json, content_type='application/json'))


class RouteErrorResource(View):
    def get(self, request, error_id):
        route_error = get_object_or_404(RouteError, pk=error_id)
        return cross_origin(JsonResponse(model_to_dict(route_error), safe=False))


class RouteErrorStatsResource(View):
    def get(self, request, error_id):
        route_error = get_object_or_404(RouteError, pk=error_id)
        bindings = RouteLSABinding.objects.filter(
            corresponding_route_error=route_error)
        bindings_json = serialize('json', bindings)
        return cross_origin(HttpResponse(bindings_json, content_type='application/json'))


class RouteErrorAllResource(View):
    def get(self, request):
        route_errors = RouteError.objects.all()
        route_errors_json = serialize('json', route_errors)
        return cross_origin(HttpResponse(route_errors_json, content_type='application/json'))


class HealthCheckBindingFiles(View):
    def get(self, request):
        bindings_database = RouteLSABinding.objects.all()
        
        params = request.GET
        map_data = str(params.get("map_data", "osm"))

        error_bindings = []
        
        if map_data == "osm":
            bindings_dir = "../data/bindings/"
        elif map_data == "drn":
            bindings_dir = "../data/bindings_drn/"
        else:
            return JsonResponse({"error": "Unsupported value provided for the parameter 'map_data'. Choose between 'osm' or 'drn'."})

        files = [f for f in os.listdir(bindings_dir) if os.path.isfile(
            os.path.join(bindings_dir, f))]

        bindings_files = []
        # Load each file
        for file in files:
            with open(os.path.join(bindings_dir, file)) as f:
                data = json.load(f)

            # Load the bindings
            for binding_json in data:
                bindings_files.append(load_binding(binding_json))

        for binding_file in bindings_files:
            matches = bindings_database.filter(
                route=binding_file.route, lsa=binding_file.lsa)
            if len(matches) != 1:
                error_bindings.append(
                    {"present": False, "binding": model_to_dict(binding_file)})
                continue
            corresponding_binding = matches[0]
            if corresponding_binding.confirmed != binding_file.confirmed or\
                corresponding_binding.corresponding_constellation != binding_file.corresponding_constellation or\
                    corresponding_binding.corresponding_route_error != binding_file.corresponding_route_error:
                error_bindings.append(
                    {"present": True, "binding": model_to_dict(binding_file)})

        return cross_origin(JsonResponse(error_bindings, safe=False))


class HealthCheckBindingsDatabase(View):
    def get(self, request):
        bindings_database = RouteLSABinding.objects.all()
        
        params = request.GET
        map_data = str(params.get("map_data", "osm"))

        error_bindings = []

        if map_data == "osm":
            bindings_dir = "../data/bindings/"
        elif map_data == "drn":
            bindings_dir = "../data/bindings_drn/"
        else:
            return JsonResponse({"error": "Unsupported value provided for the parameter 'map_data'. Choose between 'osm' or 'drn'."})

        files = [f for f in os.listdir(bindings_dir) if os.path.isfile(
            os.path.join(bindings_dir, f))]

        bindings_files = []
        # Load each file
        for file in files:
            with open(os.path.join(bindings_dir, file)) as f:
                data = json.load(f)

            # Load the bindings
            for binding_json in data:
                bindings_files.append(load_binding(binding_json))

        for database_binding in bindings_database:
            matches = [binding_file for binding_file in bindings_files if binding_file.lsa ==
                       database_binding.lsa and binding_file.route == database_binding.route]
            if len(matches) != 1:
                error_bindings.append(
                    {"present": False, "binding": model_to_dict(database_binding)})
                continue
            corresponding_binding = matches[0]
            if corresponding_binding.confirmed != database_binding.confirmed or\
                corresponding_binding.corresponding_constellation != database_binding.corresponding_constellation or\
                    corresponding_binding.corresponding_route_error != database_binding.corresponding_route_error:
                error_bindings.append(
                    {"present": True, "binding": model_to_dict(database_binding)})

        return cross_origin(JsonResponse(error_bindings, safe=False))


def load_binding(binding_json):
    lsa_id = binding_json["fields"]["lsa"]
    route_id = binding_json["fields"]["route"]
    confirmed = binding_json["fields"]["confirmed"]
    corresponding_constellation_id = binding_json["fields"][
        "corresponding_constellation"] if "corresponding_constellation" in binding_json["fields"] else None
    corresponding_route_error_id = binding_json["fields"][
        "corresponding_route_error"] if "corresponding_route_error" in binding_json["fields"] else None

    return RouteLSABinding(
        lsa_id=lsa_id,
        route_id=route_id,
        corresponding_constellation_id=corresponding_constellation_id,
        corresponding_route_error_id=corresponding_route_error_id,
        confirmed=confirmed
    )
