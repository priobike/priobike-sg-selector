from composer.models import RouteLSABinding
from django.core.management.base import BaseCommand
from routing.matching.projection import project_onto_route
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        bindings = RouteLSABinding.objects.all()

        print(f"{len(bindings)} Bindings found.")
        
        original_bindings = []
        duplicate_bindings = []
        
        for binding in bindings:
            binding_system = binding.lsa.geometry.transform(
                settings.LONLAT, clone=True)
            binding_system_projected = project_onto_route(
                binding_system, binding.route.geometry, system=settings.LONLAT)

            duplicate = False
            
            for binding in original_bindings:
                if binding_system_projected.equals(binding):
                    duplicate = True
                    duplicate_bindings.append(binding_system_projected)
                    break
                
            if not duplicate:
                original_bindings.append(binding_system_projected)
                
        print(f"{len(original_bindings)} Original Bindings found.")
        print(f"{len(duplicate_bindings)} Duplicate Bindings found.")
            