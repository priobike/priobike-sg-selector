import json
import os

from django.contrib.gis.geos import LineString
from django.core.management.base import BaseCommand
from routing.models import SG, SGMetadata
from tqdm import tqdm


def sync_sgs_from_file(sg_file_path):
    """
    Syncs the SGs from a local file containing all SGs.
    """
    with open(sg_file_path) as f:
        sgs_json = json.load(f)

    load_sgs(sgs_json)


def load_sgs(sgs_json):
    n_sgs = len(sgs_json)

    # Remove all SGs that are not in the directory
    sgs_to_delete = SG.objects.exclude(id__in=[sg["id"] for sg in sgs_json])
    sgs_to_delete.delete()

    for sg_json in tqdm(sgs_json, desc="Loading SGs"):
        sg_id = sg_json["id"]
        
        # Check if there is already an SG with this ID
        existing_sg = SG.objects.filter(id=sg_id).first()
        if existing_sg:
            # SG already exists
            continue

        try:
            sg, sg_metadata = load_sg(sg_id, sg_json)
        except ValueError:
            print(f"Could not load SG {sg_id}")
            continue
        sg.save()
        sg_metadata.save()


def load_sg(sg_id, sg_json):
    """
    Load the given SG. The JSON is inherited from a Fraunhofer SensorThings API.
    """
    sg = SG(id=sg_id)

    # Unwrap the geometries from the SG
    geometries = []
    for location in sg_json["thing"]["locations"]:
        geometry = location["location"]["geometry"]
        geometry_type = geometry["type"]
        if geometry_type != "MultiLineString":
            raise ValueError(f"Unsupported geometry type: {geometry_type}")
        geometries.append(geometry)
    if not geometries:
        raise ValueError(f"No geometries found for SG {sg_id}")

    for geometry in geometries:
        paths = geometry["coordinates"]
        if len(paths) != 3:
            raise ValueError("SG geometry needs an ingress, connection and egress line!")
        sg.ingress_geometry = LineString(paths[0])
        sg.geometry = LineString(paths[1])
        sg.egress_geometry = LineString(paths[2])

    json_metadata = sg_json["thing"]["properties"]
    sg_metadata = SGMetadata(
        sg_id=sg_id,
        topic=json_metadata["topic"],
        asset_id=json_metadata["assetID"],
        lane_type=json_metadata["laneType"],
        language=json_metadata["language"],
        owner_thing=json_metadata["ownerThing"],
        info_last_update=json_metadata["infoLastUpdate"],
        connection_id=json_metadata["connectionID"],
        egress_lane_id=json_metadata["egressLaneID"],
        ingress_lane_id=json_metadata["ingressLaneID"],
        traffic_lights_id=json_metadata["trafficLightsID"],
        signal_group_id=f"hamburg/{sg_json['thing']['name']}"
    )
    sg.metadata = sg_metadata

    return sg, sg_metadata


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
            raise FileNotFoundError(f"Could not find SG file at {sg_file_path}")

        sync_sgs_from_file(sg_file_path)
