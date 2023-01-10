import json
import os

from composer.models import Route, RouteLSABinding
from django.core.management.base import BaseCommand
from django.contrib.gis.measure import D
from routing.matching.projection import project_onto_route
from django.conf import settings
from routing.models import LSA
from composer.models import RouteLSABinding, Route
from composer.utils import check_binding_exists
from tqdm import tqdm


class Command(BaseCommand):
    logs_path = "routing/composer/logs/"

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies which route is the first one that should be looked at
        parser.add_argument('first_route_id', type=str)

    def handle(self, *args, **options):
        if not options["first_route_id"]:
            raise Exception(
                "Please specify a route id for the first route that should be looked at.")

        first_route_id = options["first_route_id"]

        all_bindings = RouteLSABinding.objects.all()

        routes = Route.objects.filter(id__gte=first_route_id)

        routes_with_no_duplicates = []

        for route in tqdm(routes, desc="Checking routes"):
            route_linestring = route.geometry.transform(
                settings.LONLAT, clone=True)

            duplicates = False

            nearby_lsas = LSA.objects.filter(geometry__dwithin=(
                route.geometry, D(m=settings.SEARCH_RADIUS_M)))

            for lsa in nearby_lsas:
                lsa_linestring = lsa.geometry.transform(
                    settings.LONLAT, clone=True)
                lsa_linestring_projected = project_onto_route(
                    lsa_linestring, route_linestring)

                if check_binding_exists(lsa_linestring_projected, lsa.id, all_bindings):
                    duplicates = True
                    break

            if not duplicates:
                routes_with_no_duplicates.append(route)
                with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}/routes_with_no_duplicates_in_bindings_of_routes_before_{first_route_id}/{str(route.id)}.json"), 'w') as fp:
                    json.dump({"route_id": route.id}, fp, indent=4)

        print(routes_with_no_duplicates)
