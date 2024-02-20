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
            
        # Serialize the data
        sgs_info = [
            {
                "id": sg.lsametadata.signal_group_id,
                "position": {
                    "lon": sg.start_point.x,
                    "lat": sg.start_point.y,
                },
            }
            for sg in sgs
        ]

        json_output = json.dumps(list(sgs_info), indent=None, ensure_ascii=False)

        with gzip.open(os.path.join(settings.BASE_DIR, 'static/sgs_min.json.gz'), 'wb') as f:
            f.write(str.encode(json_output))

        # Serialize the data
        sgs_geo = [
            {
                "id": sg.lsametadata.signal_group_id,
                "geometry": sg.geometry.json,
            }
            for sg in sgs
        ]

        json_output = json.dumps(list(sgs_geo), indent=None, ensure_ascii=False)

        with gzip.open(os.path.join(settings.BASE_DIR, 'static/sgs_geo.json.gz'), 'wb') as f:
            f.write(str.encode(json_output))
