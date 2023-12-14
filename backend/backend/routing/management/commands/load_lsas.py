import requests
from django.contrib.gis.geos import LineString
from django.core.management.base import BaseCommand
from routing.matching.bearing import get_bearing
from routing.models import LSA, LSAMetadata


class Command(BaseCommand):
    """
    Sync from a SensorThings API.
    """

    def add_arguments(self, parser):
        parser.add_argument("--api", type=str)
        parser.add_argument("--filter", type=str)

    def create_lsa(self, thing):
        lsa = LSA(id=thing["name"])

        # Unwrap the geometries from the LSA
        geometries = []
        for location in thing["Locations"]:
            geometry = location["location"]["geometry"]
            geometry_type = geometry["type"]
            if geometry_type != "MultiLineString":
                raise ValueError(f"Unsupported geometry type: {geometry_type}")
            geometries.append(geometry)
        if not geometries:
            raise ValueError(f"No geometries found for LSA {thing['name']}")

        for geometry in geometries:
            paths = geometry["coordinates"]
            if len(paths) != 3:
                raise ValueError("LSA geometry needs an ingress, connection and egress line!")
            lsa.ingress_geometry = LineString(paths[0])
            lsa.geometry = LineString(paths[1])
            lsa.egress_geometry = LineString(paths[2])

        if len(lsa.geometry.coords) < 2:
            raise ValueError("LSA must have at least 2 coordinates")
        lon1, lat1 = lsa.geometry.coords[0][:2]
        lon2, lat2 = lsa.geometry.coords[1][:2]
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        lsa.bearing = bearing

        properties = thing["properties"]
        lsa_metadata = LSAMetadata(
            lsa_id=thing["name"],
            topic=properties["topic"],
            asset_id=properties["assetID"],
            lane_type=properties["laneType"],
            language=properties["language"],
            owner_thing=properties["ownerThing"],
            info_last_update=properties["infoLastUpdate"],
            connection_id=properties["connectionID"],
            egress_lane_id=properties["egressLaneID"],
            ingress_lane_id=properties["ingressLaneID"],
            traffic_lights_id=properties["trafficLightsID"],
            signal_group_id=f"hamburg/{thing['name']}"
        )

        # Unwrap the datastream ids.
        for datastream in thing["Datastreams"]:
            layer_type = datastream["properties"]["layerName"]
            datastream_id = datastream["@iot.id"]
            if layer_type == "detector_car":
                lsa_metadata.datastream_detector_car_id = datastream_id
            elif layer_type == "detector_cyclists":
                lsa_metadata.datastream_detector_cyclists_id = datastream_id
            elif layer_type == "cycle_second":
                lsa_metadata.datastream_cycle_second_id = datastream_id
            elif layer_type == "primary_signal":
                lsa_metadata.datastream_primary_signal_id = datastream_id
            elif layer_type == "signal_program":
                lsa_metadata.datastream_signal_program_id = datastream_id

        lsa.metadata = lsa_metadata

        lsa.save()
        lsa_metadata.save()

    def handle(self, *args, **options):
        if not options["api"]:
            raise ValueError("Missing required argument: --api")
        if not options["filter"]:
            raise ValueError("Missing required argument: --filter")

        # Delete all existing LSAs
        LSA.objects.all().delete()
        
        url = f"{options['api']}/Things?$filter={options['filter']}&$expand=Locations,Datastreams"
        while True:
            print("Fetching data from directory:", url)
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError(f"Could not fetch LSA data from {url}")
            response_json = response.json()

            for thing_json in response_json["value"]:
                try:
                    self.create_lsa(thing_json)
                except Exception as e:
                    print(f"Could not create LSA {thing_json['name']}: {e}")
            
            url = response_json.get("@iot.nextLink")
            if not url:
                break

        print(f"Done processing. {LSA.objects.count()} Things in DB.")
