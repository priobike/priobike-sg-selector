import os
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.gis.measure import D
from itertools import chain
from composer.models import Route
from routing.models import LSA


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies whether bindings based on OSM or DRN routes should be used.
        parser.add_argument("--route_data", type=str)

    def handle(self, *args, **options):
        # Check if the path argument is valid
        if not options["route_data"]:
            raise Exception(
                "Please provide a route_data to specify which bindings should be used.")

        route_data = options["route_data"]
        
        unique_bindings_from_route_on = 0 # 117 for osm bindings

        relevant_routes_1 = Route.objects.filter(
            id__range=(0, unique_bindings_from_route_on - 1))
        
        if route_data != "osm" and route_data != "drn":
            raise Exception(
                "Please provide a valid value for the route_data option ('osm' or 'drn').")
            
        if route_data == "osm":
            bindings_dir = "../data/bindings_osm/"
        elif route_data == "drn":
            bindings_dir = "../data/bindings_drn/"

        files = [int(f.replace(".json", "")) for f in os.listdir(
            bindings_dir) if os.path.isfile(os.path.join(bindings_dir, f))]

        relevant_routes_2_ids = [
            id for id in files if id >= unique_bindings_from_route_on]

        relevant_routes_2 = Route.objects.filter(id__in=relevant_routes_2_ids)

        relevant_routes = list(chain(relevant_routes_1, relevant_routes_2))

        lsas_in_range = []

        for route in relevant_routes:
            lsas_in_range.append(len(LSA.objects.filter(
                geometry__dwithin=(route.geometry, D(m=20)))))

        print(np.mean(np.array(lsas_in_range)))
