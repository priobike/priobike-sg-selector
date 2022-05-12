from collections import defaultdict

from composer.models import Connection, Waypoint
from django.contrib.gis.geos import LineString, Point
from django.core.management.base import BaseCommand
from routing.models import SG
from tqdm import tqdm


def elevate_line_string(linestring, elevation):
    """
    Elevate the given line string by the given elevation.
    """
    return LineString([
        Point(*coord, elevation, srid=linestring.srid)
        for coord in linestring.coords
    ])


class Command(BaseCommand):
    height_difference = 1

    def handle(self, *args, **options):
        if not SG.objects.exists():
            raise Exception("SGs need to be loaded first!")

        if not Connection.objects.exists():
            connections = []
            waypoints = []

            crossings = defaultdict(float)
            for sg in tqdm(SG.objects.all(), desc="Loading visualization models"):
                crossing_id = sg.sgmetadata.traffic_lights_id
                crossing_height = crossings[crossing_id]
                crossings[crossing_id] += self.height_difference
                elevated_geometry = elevate_line_string(sg.geometry, crossing_height)

                connection_object = Connection(sg=sg, elevated_geometry=elevated_geometry)
                connections.append(connection_object)
                connection_length = elevated_geometry.length

                current_length = 0
                last_point = None

                for coord in elevated_geometry.coords:
                    point = Point(*coord, srid=sg.geometry.srid)
                    dist = last_point.distance(point) if last_point is not None else 0
                    current_length += dist
                    last_point = point
                    progress = int((current_length / connection_length) * 100)

                    waypoint_object = Waypoint(
                        connection=connection_object,
                        progress=progress,
                        elevated_geometry=point
                    )
                    waypoints.append(waypoint_object)

            Connection.objects.bulk_create(connections)
            Waypoint.objects.bulk_create(waypoints)

        print(f"{Connection.objects.count()} connections in database.")
        print(f"{Waypoint.objects.count()} waypoints in database.")
