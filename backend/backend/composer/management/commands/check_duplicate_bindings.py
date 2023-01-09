from typing import List

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

            # Check whether the binding type is already in the duplicate list
            test = 0
            if duplicate_bindings:
                for index, duplicate_bindings_list in enumerate(duplicate_bindings):

                    duplicate_binding_system = duplicate_bindings_list[0].lsa.geometry.transform(
                        settings.LONLAT, clone=True)
                    duplicate_binding_system_projected = project_onto_route(
                        duplicate_binding_system, binding.route.geometry, system=settings.LONLAT)

                    if duplicate_binding_system_projected.equals(binding_system_projected):
                        duplicate_bindings[index].append(binding)
                        duplicate = True
                        test += 1

            # Check whether the binding is a duplicate to a previous original binding
            if not duplicate and original_bindings:
                test = 0
                for original_binding in original_bindings:

                    original_binding_system = original_binding.lsa.geometry.transform(
                        settings.LONLAT, clone=True)
                    original_binding_system_projected = project_onto_route(
                        original_binding_system, binding.route.geometry, system=settings.LONLAT)

                    if original_binding_system_projected.equals(binding_system_projected):
                        duplicate_bindings.append([binding])
                        duplicate = True
                        test += 1

                if test > 1:
                    print("This shouldn't happen but is a print for debug reasions.")

            # If it is no duplicate add it as a original binding
            if not duplicate:
                original_bindings.append(binding)

        print("\n")
        print(f"{len(original_bindings)} original bindings found.")

        duplicate_count = 0
        for binding_list in duplicate_bindings:
            for binding in binding_list:
                duplicate_count += 1
        print(f"{duplicate_count} duplicates found.")

        print(f"{len(duplicate_bindings)} duplicate types found.")
