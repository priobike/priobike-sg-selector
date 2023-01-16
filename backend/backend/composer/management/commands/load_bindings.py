import json
import os

from composer.models import Route, RouteLSABinding, Constellation, RouteError
from django.core.management.base import BaseCommand
from routing.models import LSA
from tqdm import tqdm


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies the path to the file to load
        parser.add_argument('bindings_dir', type=str)

    def handle(self, *args, **options):
        # Check if the path argument is valid
        if not options["bindings_dir"]:
            raise Exception("Please specify a path to the files to load.")

        if not Constellation.objects.exists():
            raise Exception("Constellations need to be loaded first!")

        if not RouteError.objects.exists():
            raise Exception("Route errors need to be loaded first!")

        if not LSA.objects.exists():
            raise Exception("LSAs need to be loaded first!")

        if not Route.objects.exists():
            raise Exception("Routes need to be loaded first!")

        # Get all files in the bindings dir
        bindings_dir = options["bindings_dir"]
        files = [f for f in os.listdir(bindings_dir) if os.path.isfile(
            os.path.join(bindings_dir, f))]

        bindings = []
        # Load each file
        for file in tqdm(files, desc="Loading bindings"):
            with open(os.path.join(bindings_dir, file)) as f:
                data = json.load(f)

            # Load the bindings
            for binding_json in data:
                # Only add the binding if the corresponding lsa and route exists
                if LSA.objects.filter(pk = binding_json["fields"]["lsa"]).exists():
                    bindings.append(self.load_binding(binding_json))

        # Save the bindings
        RouteLSABinding.objects.bulk_create(bindings)
        print(f"{RouteLSABinding.objects.count()} bindings in database.")

    def load_binding(self, binding_json):
        lsa_id = binding_json["fields"]["lsa"]
        route_id = binding_json["fields"]["route"]
        confirmed = binding_json["fields"]["confirmed"]
        corresponding_constellation_id = binding_json["fields"][
            "corresponding_constellation"] if "corresponding_constellation" in binding_json["fields"] else None
        corresponding_route_error_id = binding_json["fields"][
            "corresponding_route_error"] if "corresponding_route_error" in binding_json["fields"] else None

        return RouteLSABinding(
            lsa_id=lsa_id,
            route_id=route_id,
            corresponding_constellation_id=corresponding_constellation_id,
            corresponding_route_error_id=corresponding_route_error_id,
            confirmed=confirmed
        )
