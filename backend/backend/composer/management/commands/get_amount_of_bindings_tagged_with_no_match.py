from composer.models import RouteLSABinding, Route
from routing.models import LSA
from django.core.management.base import BaseCommand
from django.contrib.gis.measure import D
from composer.utils import get_routes_with_bindings
from django.conf import settings


class Command(BaseCommand):
    help = """
        We only save bindings between routes and SGs if they are matches (the SG needs to be passed when driving along the route).
        Therefore we can only count the matches.
        The amount of bindings tagged with no_match gets determined implicitly by subtracting the amount of bindings (matches) from the amount of all SGs within a certain distance to the route.
        """ 
        
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
            
        if route_data != "osm" and route_data != "drn":
            raise Exception(
                "Please provide a valid value for the route_data option ('osm' or 'drn').")
        
        matchesCount = RouteLSABinding.objects.count()

        # Determination of routes via binding .json files:
        # routes = get_routes_with_bindings(route_data)
        
        # Determination of routes via RouteLSABinding objects:
        routes = Route.objects \
            .filter(bound_lsas__isnull=False) \
            .distinct()
        
        totalNearbySGsCount = 0
        
        for route in routes:
            binding = RouteLSABinding.objects.filter(route=route).first()
            if binding is None:
                raise Exception("Binding is none. This shouldn't happen.")
            sgCount = LSA.objects.filter(geometry__dwithin=(route.geometry, D(m=settings.SEARCH_RADIUS_M))).count()
            totalNearbySGsCount += sgCount
            
        print(f"Amount of matches: {matchesCount}")
        print(f"Amount of all SGs within {settings.SEARCH_RADIUS_M}m to the routes: {totalNearbySGsCount}")
        print(f"Amount of no_match bindings: {totalNearbySGsCount - matchesCount}")
            