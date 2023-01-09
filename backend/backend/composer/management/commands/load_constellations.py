import json
import os

from composer.models import Constellation
from django.core.management.base import BaseCommand
from tqdm import tqdm


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get all files in the constellations dir
        constellations_dir = "../data/constellations/"
        files = [f for f in os.listdir(constellations_dir) if os.path.isfile(
            os.path.join(constellations_dir, f))]

        constellations = []
        # Load each file
        for file in tqdm(files, desc="Loading constellations"):
            with open(os.path.join(constellations_dir, file)) as f:
                data = json.load(f)

            # Load the constellations
            for constellations_json in data:
                constellations.append(
                    self.load_constellations(constellations_json))

        # Save the constellations
        Constellation.objects.bulk_create(constellations)
        print(f"{Constellation.objects.count()} constellations in database.")

    def load_constellations(self, constellations_json):
        id = constellations_json["fields"]["id"]
        name = constellations_json["fields"]["name"]
        description = constellations_json["fields"]["description"]
        custom_id = constellations_json["fields"]["custom_id"]

        return Constellation(
            id=id,
            name=name,
            description=description,
            custom_id=custom_id
        )
