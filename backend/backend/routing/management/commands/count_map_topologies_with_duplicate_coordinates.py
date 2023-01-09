from django.core.management.base import BaseCommand

from routing.models import LSA


class Command(BaseCommand):
    def handle(self, *args, **options):
        lsas = LSA.objects.all()
        lsa_count = 0

        # Analyse how many MAP-Topologies have duplicate coordinates
        for lsa in lsas:
            map_topology_duplicate_coordinates = False
            for coordinate in lsa.geometry.coords:
                count = 0
                for coordinate2 in lsa.geometry.coords:
                    if coordinate == coordinate2:
                        count += 1
                        if count > 2:
                            map_topology_duplicate_coordinates = True
                            break
                if map_topology_duplicate_coordinates:
                    lsa_count += 1
                    break

        print(f"{lsa_count} map topologies with duplicate coordinates found.")
        print(
            f"{len(lsas)-lsa_count} map topologies with no duplicate coordinates found.")
        print(f"{len(lsas)} map topologies in total found")
