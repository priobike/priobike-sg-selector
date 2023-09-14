from composer.models import RouteLSABinding
from django.core.management.base import BaseCommand
from routing.matching.projection import project_onto_route
from django.conf import settings

def addToBindings(bindings_dict, binding_lsa_projected, binding_route_id):
    if binding_route_id in bindings_dict:
        bindings_dict[binding_route_id].append(binding_lsa_projected)
        return bindings_dict
    
    bindings_dict[binding_route_id] = [binding_lsa_projected]
    return bindings_dict


class Command(BaseCommand):
    def handle(self, *args, **options):
        bindings = RouteLSABinding.objects.all()

        print(f"{len(bindings)} Bindings found.")
        
        original_bindings = {}
        duplicate_bindings = {} 
        
        for binding in bindings:
            binding_system = binding.lsa.geometry.transform(
                settings.LONLAT, clone=True)
            binding_system_projected = project_onto_route(
                binding_system, binding.route.geometry, system=settings.LONLAT)

            duplicate = False
            
            for route_id, original_bindings_linestrings in original_bindings.items():
                for original_binding_linestring in original_bindings_linestrings:
                    if binding_system_projected.equals(original_binding_linestring):
                        duplicate = True
                        addToBindings(duplicate_bindings, binding_system_projected, route_id)
                        break
                
            if not duplicate:
                addToBindings(original_bindings, binding_system_projected, binding.route.id)
                
        routes_with_only_duplicates = []
        
        for route_id, duplicate_bindings_linestrings in duplicate_bindings.items():
            if route_id not in original_bindings:
                routes_with_only_duplicates.append(route_id)

        print(f"Routes with only duplicate bindings: {routes_with_only_duplicates}")
        
        routes_with_only_one_original_binding = []
        
        for route_id, original_binding_linestring in original_bindings.items():
            if len(original_binding_linestring) == 1:
                routes_with_only_one_original_binding.append(route_id)
                
        print(f"Routes with only one original binding: {routes_with_only_one_original_binding}")
        
        routes_with_bad_original_duplicate_ratio = []
        
        for route_id, original_binding_linestrings in original_bindings.items():
            if route_id not in duplicate_bindings:
                continue
            if route_id not in original_bindings:
                continue
            if len(original_binding_linestrings) / len(duplicate_bindings[route_id]) < 1:
                routes_with_bad_original_duplicate_ratio.append(route_id)
                
        print(f"Routes with bad original duplicate ratio: {routes_with_bad_original_duplicate_ratio}")
        
        