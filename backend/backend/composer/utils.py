import os
from itertools import chain
from typing import List

from composer.models import Route, RouteLSABinding
from django.conf import settings
from django.contrib.gis.geos.linestring import LineString
from routing.matching.projection import project_onto_route


def get_routes_with_bindings(route_data):
    """
    This function return a list with all routes that have bindings (between routes and signalgroups).
    Not only routes that have matches but also the routes that got looked at and that don't have matches.
    Thus not only routes get returned where a .json-file (at backend/data/bindings) exists but also where no
    .json-file exists but if it got looked at (needs to be remembered).

    Returns:
        list: list with all routes that were looked at in the composer and that got matched with signalgroups
    """

    # This specifies until which route every route got looked at. Therefore every route until this ID can be returned.
    # Above this number not every route got looked at and therefore another mechanism needs to be used to get the remaining routes.
    every_route_looked_up_to = 0 # 117 for osm bindings
    relevant_routes_1 = Route.objects.filter(
        id__range=(0, every_route_looked_up_to - 1))
    
    if route_data != "osm" and route_data != "drn" and route_data != "osm_old":
            raise Exception(
                "Please provide a valid value for the route_data option ('osm' or 'drn' or 'osm_old').")
        
    # To get the remaining routes we look at the .json-files in the bindings-directory.
    if route_data == "osm":
        bindings_dir = "../data/bindings_osm/"
    elif route_data == "drn":
        bindings_dir = "../data/bindings_drn/"
    elif route_data == "osm_old":
        bindings_dir = "../data/bindings_old/"

    files = [int(f.replace(".json", "")) for f in os.listdir(
        bindings_dir) if os.path.isfile(os.path.join(bindings_dir, f))]
    relevant_routes_2_ids = [
        id for id in files if id >= every_route_looked_up_to]
    relevant_routes_2 = Route.objects.filter(id__in=relevant_routes_2_ids)

    return list(chain(relevant_routes_1, relevant_routes_2))

def check_binding_exists(projected_lsa_linestring: LineString, projected_lsa_linestring_id: str, existing_bindings: List[RouteLSABinding]) -> bool:
    """Checks if the given projected lsa linestring already exists in the existing bindings
    Args:
        projected_lsa_linestring (LineString): linestring that should be checked
        existing_bindings (List[RouteLSABinding]): all existing bindings
    Returns:
        bool: true -> it already exists and vice versa
    """

    system_projected_lsa_linestring = projected_lsa_linestring.transform(
        settings.LONLAT, clone=True)

    for binding in existing_bindings:
        if projected_lsa_linestring_id != binding.lsa.id:
            continue
        
        projected_binding_lsa_linestring = project_onto_route(
            binding.lsa.geometry.transform(settings.LONLAT, clone=True),
            binding.route.geometry.transform(settings.LONLAT, clone=True))

        system_projected_binding_lsa_linestring = projected_binding_lsa_linestring.transform(
            settings.LONLAT, clone=True)

        if system_projected_lsa_linestring.equals(system_projected_binding_lsa_linestring):
            print("\nDuplicate ID:")
            print(binding.lsa.id)
            return True

    return False
