from unittest.mock import MagicMock

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase
from routing.views import make_waypoints, snap


class WaypointTest(TestCase):
    def test_waypoints(self):
        # See: https://www.google.de/maps/place/51%C2%B001'50.2%22N+13%C2%B043'39.7%22E
        sg = MagicMock()
        sg.start_point = Point(13.727694, 51.030611, 0, srid=settings.LONLAT)
        sg.sgmetadata = MagicMock()
        sg.sgmetadata.signal_group_id = "test-sg"
        route = LineString([
            # See: https://www.google.de/maps/place/51%C2%B001'50.3%22N+13%C2%B043'41.1%22E
            Point(13.728079, 51.030626, 0, srid=settings.LONLAT),
            # See: https://www.google.de/maps/place/51%C2%B001'50.2%22N+13%C2%B043'40.3%22E
            Point(13.727861, 51.030611, 0, srid=settings.LONLAT),
            # See: https://www.google.de/maps/place/51%C2%B001'50.1%22N+13%C2%B043'38.6%22E
            Point(13.727389, 51.030583, 0, srid=settings.LONLAT),
        ], srid=settings.LONLAT)

        snaps = snap([sg], route)
        
        # Snaps should be one SG "test-sg" snapped to the route, at a distance of roughly 28 meters
        # See: https://www.google.de/maps/dir/51.0306279,13.7280887/51.0306111,13.7276944/@51.0306388,13.7277089,20.35z/data=!4m2!4m1!3e2
        self.assertEqual(len(snaps), 1)
        s = snaps[0]
        self.assertEqual(s.sg.sgmetadata.signal_group_id, "test-sg")

        waypoints = make_waypoints(snaps, route)

        # Waypoints should be: 
        # - The start point of the route
        # - The second point of the route, which is near the SG
        # - The snapped point of the SG on the route
        # - The third point of the route
        self.assertEqual(len(waypoints), 4)
        start_waypoint, second_waypoint, sg_waypoint, end_waypoint = waypoints

        # The distance of the first waypoint should be roughly 28 meters
        # See: https://www.google.de/maps/dir/51.0306279,13.7280887/51.0306111,13.7276944/@51.0306388,13.7277089,20.35z/data=!4m2!4m1!3e2
        self.assertAlmostEqual(start_waypoint["distanceToNextSignal"], 28, delta=1)

        # The distance of the second waypoint should be roughly 12 meters
        # See: https://www.google.de/maps/dir/51.030611,+13.727861/51.0306111,13.7276944/@51.0305977,13.7276593,21z/data=!4m7!4m6!1m3!2m2!1d13.727861!2d51.030611!1m0!3e2
        self.assertAlmostEqual(second_waypoint["distanceToNextSignal"], 12, delta=1)

        # The distance of the snapped SG point should be 0 meters
        self.assertEqual(sg_waypoint["distanceToNextSignal"], 0)

        # The distance of the end waypoint should be unset, since no more sgs are along the route
        self.assertIsNone(end_waypoint["distanceToNextSignal"])

