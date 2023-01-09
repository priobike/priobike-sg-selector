from django.contrib.gis.measure import D
from django.core.management.base import BaseCommand
from routing.models import LSA, LSACrossing


class Command(BaseCommand):
    """
    Sync crossings. This performs the following steps:

    For each traffic light, check if there is a crossing in less than <distance>, set that 
    crossing as connected. If there is no crossing in less than <distance>, create a new crossing.

    Make sure to call load_crossings before.
    """

    search_radius_m = 50

    def handle(self, *args, **options):
        print("Syncing crossings...")
        lsas = LSA.objects.all()
        n_crossings_before = LSACrossing.objects.count()
        for lsa in lsas:
            # Check if there is a crossing in less than <distance>
            crossings = LSACrossing.objects.filter(point__dwithin=(lsa.geometry, D(m=self.search_radius_m)))
            if crossings.exists():
                crossing = sorted(crossings, key=lambda c: c.point.distance(lsa.geometry))[0]
                # Set that crossing as connected
                if not crossing.connected:
                    crossing.connected = True
                    crossing.save()
                    print(f"Setting crossing {crossing.name} as connected by LSA {lsa.id}")
            else:
                # Create a new crossing
                crossing = LSACrossing(point=lsa.start_point, connected=True, name=f"LSA {lsa.id}")
                crossing.save()
                print(f"Creating new crossing {crossing.name} by LSA {lsa.id} at {crossing.point}")
        
        # Print out some stats.
        n_crossings_after = LSACrossing.objects.count()
        n_crossings_created = n_crossings_after - n_crossings_before
        n_crossings_connected = LSACrossing.objects.filter(connected=True).count()
        print(f"Finished syncing {n_crossings_after} crossings.")
        print(f"Created {n_crossings_created} crossings.")
        print(f"{n_crossings_connected} Crossings are connected.")
        print(f"{n_crossings_after - n_crossings_connected} Crossings are not connected.")

