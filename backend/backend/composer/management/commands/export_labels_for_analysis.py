import json
import os

from composer.models import Constellation, Route, RouteError, RouteLSABinding
from django.core.management.base import BaseCommand
from routing.models import LSA
from tqdm import tqdm


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = []
        for binding in tqdm(RouteLSABinding.objects.all(), desc="Exporting labels"):
            data.append({
                'lsa': {
                    'id': binding.lsa.id,
                    'geometry': [
                        [list(c) for c in binding.lsa.ingress_geometry.coords],
                        [list(c) for c in binding.lsa.geometry.coords],
                        [list(c) for c in binding.lsa.egress_geometry.coords],
                    ]
                },
                'route': {
                    'id': binding.route.id,
                    'geometry': [list(c) for c in binding.route.geometry.coords],
                },
            })
        # Write the data to a file
        with open('matching-labels.json', 'w') as f:
            json.dump(data, f)
