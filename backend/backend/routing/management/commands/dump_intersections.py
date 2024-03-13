import gzip
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from routing.models import LSACrossing


class Command(BaseCommand):
    """
    Dump all bike SGs in DB to a gzipped file in the static directory.
    """

    def handle(self, *args, **options):
        intersection_centers = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [crossing.point.x, crossing.point.y],
                    },
                }
                for crossing in LSACrossing.objects.filter(connected=True)
            ],
        }
        
        json_output = json.dumps(intersection_centers, indent=None, ensure_ascii=False)

        with gzip.open(os.path.join(settings.BASE_DIR, 'static/intersections.json.gz'), 'wb') as f:
            f.write(str.encode(json_output))
