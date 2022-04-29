import json
import logging
import os

from django.contrib.gis.geos import LineString
from django.core.management.base import BaseCommand
from routing.models import SignalGroup
from tqdm import tqdm


def sync_sgs_from_file(sg_file_path):
    """
    Syncs the SignalGroups from a local file containing all SignalGroups.
    """
    with open(sg_file_path) as f:
        sgs_json = json.load(f)

    load_sgs(sgs_json)


def load_sgs(sgs_json):
    n_sgs = len(sgs_json)
    print(f"Processing {n_sgs} SignalGroups...")

    # Remove all SignalGroups that are not in the directory
    sgs_to_delete = SignalGroup.objects.exclude(id__in=[sg["id"] for sg in sgs_json])
    print(f"Deleting {sgs_to_delete.count()} SignalGroups")
    sgs_to_delete.delete()

    for sg_json in tqdm(sgs_json, desc="Loading SignalGroups"):
        sg_id = sg_json["id"]
        
        # Check if there is already an SignalGroup with this ID
        existing_sg = SignalGroup.objects.filter(id=sg_id).first()
        if existing_sg:
            # SignalGroup already exists
            continue

        try:
            sg = load_sg(sg_id, sg_json)
        except ValueError:
            print(f"Could not load SignalGroup {sg_id}")
            continue
        sg.save()


def load_sg(sg_id, sg_json):
    """
    Load the given SignalGroup. The JSON is inherited from a Fraunhofer SensorThings API.
    """
    sg = SignalGroup(id=sg_id)

    # Unwrap the geometries from the SignalGroup
    geometries = []
    for location in sg_json["thing"]["locations"]:
        geometry = location["location"]["geometry"]
        geometry_type = geometry["type"]
        if geometry_type != "MultiLineString":
            raise ValueError(f"Unsupported geometry type: {geometry_type}")
        geometries.append(geometry)
    if not geometries:
        raise ValueError(f"No geometries found for SignalGroup {sg_id}")

    for geometry in geometries:
        paths = geometry["coordinates"]
        if len(paths) != 3:
            raise ValueError("SignalGroup geometry needs an ingress, connection and egress line!")
        sg.geometry = LineString(paths[1])

    return sg


class Command(BaseCommand):
    help = """Use hyperparameter tuning to find the best matching configuration."""

    # Add an arg for the file path
    def add_arguments(self, parser):
        parser.add_argument("sg_file_path", type=str)

    def handle(self, *args, **options):
        # Get the file path from the command line
        sg_file_path = options["sg_file_path"]

        # Check if the file exists
        if not os.path.isfile(sg_file_path):
            raise FileNotFoundError(f"Could not find SignalGroup file at {sg_file_path}")

        sync_sgs_from_file(sg_file_path)
