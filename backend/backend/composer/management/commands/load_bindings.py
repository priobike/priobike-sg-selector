import json
import os
from tkinter import E

from composer.models import Route, RouteSGBinding
from django.core.management.base import BaseCommand
from routing.models import SG
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

        if not SG.objects.exists():
            raise Exception("SGs need to be loaded first!")

        if not Route.objects.exists():
            raise Exception("Routes need to be loaded first!")

        # Get all files in the bindings dir
        bindings_dir = options["bindings_dir"]
        files = [f for f in os.listdir(bindings_dir) if os.path.isfile(os.path.join(bindings_dir, f))]

        bindings = []
        # Load each file
        for file in tqdm(files, desc="Loading bindings"):
            if not ".json" in file:
                continue
            with open(os.path.join(bindings_dir, file)) as f:
                data = json.load(f)

            # Load the bindings
            for binding_json in data:
                try:
                    bindings.append(self.load_binding(binding_json))
                except ValueError as e:
                    pass

        # Save the bindings
        RouteSGBinding.objects.bulk_create(bindings)
        print(f"{RouteSGBinding.objects.count()} bindings in database.")

    def load_binding(self, binding_json):
        sg_id = binding_json["fields"]["sg"]
        if not SG.objects.filter(id=sg_id).exists():
            # Since the sgs are continuously updated, this may happen
            raise ValueError(f"SG with id {sg_id} does not exist in the current signal group dataset.")
        route_id = binding_json["fields"]["route"]
        if not Route.objects.filter(id=route_id).exists():
            raise Exception(f"Route with id {route_id} does not exist.")
        confirmed = binding_json["fields"]["confirmed"]

        return RouteSGBinding(
            sg_id=sg_id,
            route_id=route_id,
            confirmed=confirmed
        )
