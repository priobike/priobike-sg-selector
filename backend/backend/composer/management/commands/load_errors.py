import json
import os

from composer.models import RouteError
from django.core.management.base import BaseCommand
from tqdm import tqdm


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get all files in the errors dir
        errors_dir = "../data/errors/"
        files = [f for f in os.listdir(errors_dir) if os.path.isfile(
            os.path.join(errors_dir, f))]

        errors = []
        # Load each file
        for file in tqdm(files, desc="Loading errors"):
            with open(os.path.join(errors_dir, file)) as f:
                data = json.load(f)

            # Load the errors
            for errors_json in data:
                errors.append(self.load_errors(errors_json))

        # Save the errors
        RouteError.objects.bulk_create(errors)
        print(f"{RouteError.objects.count()} route error types in database.")

    def load_errors(self, errors_json):
        id = errors_json["fields"]["id"]
        name = errors_json["fields"]["name"]
        description = errors_json["fields"]["description"]
        custom_id = errors_json["fields"]["custom_id"]

        return RouteError(
            id=id,
            name=name,
            description=description,
            custom_id=custom_id
        )
