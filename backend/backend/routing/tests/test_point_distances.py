from django.contrib.gis.geos import LineString
from django.test import TestCase

from routing.matching.ml.features.feature_point_distances import calc_points_distances


class PointDistancesTest(TestCase):
    def test_calc_points_distances(self):
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)
        l2 = LineString([(0, 0), (0, -10), (0, -20)], srid=3857)
        diffs = calc_points_distances(l1, l2)
        self.assertEqual(diffs, [0, 20, 40])

        l1 = LineString([(0, 0), (0, 10)], srid=3857)
        l2 = LineString([(0, 0), (10, 10)], srid=3857)
        diffs = calc_points_distances(l1, l2)
        self.assertEqual(diffs, [0, 10])

        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)
        l2 = LineString([(0, 0), (10, 10), (10, 20)], srid=3857)
        diffs = calc_points_distances(l1, l2)
        self.assertEqual(diffs, [0, 10, 10])

        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)
        l2 = LineString([(0, 0), (-10, -10), (-20, 0)], srid=3857)
        diffs = calc_points_distances(l1, l2)
        self.assertEqual(round(diffs[1], 2), 22.36)
        self.assertEqual(round(diffs[2], 2), 28.28)
