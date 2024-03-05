import json
import gzip
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from routing.models import LSA


class Command(BaseCommand):
    """
    Dump all bike SGs in DB to a gzipped file in the static directory.
    """

    def handle(self, *args, **options):
        sgs = LSA.objects.filter(lsametadata__lane_type__icontains="Radfahrer")
        intersections = {}

        for sg in sgs:
            key = sg.lsametadata.connection_id.split("_").first()
            if key in intersections:
                intersections[key].append(sg)
            else:
                intersections[key] = [sg]
        
        # In Geojson format.
        intersection_centers = {
            "type": "FeatureCollection",
            "features": [],
            }

        for key, sgs in intersections.items():
            x = 0
            y = 0
            for sg in sgs:
                x += sg.start_point.x
                y += sg.start_point.y
            intersection_centers["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [x / len(sgs), y / len(sgs)],
                },
            })
        
        json_output = json.dumps(intersection_centers, indent=None, ensure_ascii=False)

        with gzip.open(os.path.join(settings.BASE_DIR, 'static/intersections.json.gz'), 'wb') as f:
            f.write(str.encode(json_output))
