import os
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.gis.measure import D
from itertools import chain
from composer.models import Route
from routing.models import LSA


class Command(BaseCommand):

    def handle(self, *args, **options):
        unique_bindings_from_route_on = 117

        relevant_routes_1 = Route.objects.filter(
            id__range=(0, unique_bindings_from_route_on - 1))

        bindings_dir = "../data/bindings/"
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
