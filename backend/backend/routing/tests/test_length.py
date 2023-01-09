from django.contrib.gis.geos import LineString
from django.test import TestCase
from routing.matching.length import (calc_length_diffs, calc_segment_lengths,
                                     normalize_sum)


class LengthCalculationTest(TestCase):
    def test_calc_segment_lengths(self):
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)
        lengths = calc_segment_lengths(l1)
        self.assertEqual(lengths, [10, 10])

        l2 = LineString([(0, 0), (10, 0), (10, 10)], srid=3857)
        lengths = calc_segment_lengths(l2)
        self.assertEqual(lengths, [10, 10])

    def test_calc_length_diffs(self):
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)
        l2 = LineString([(0, 0), (0, -10), (0, -20)], srid=3857)
        diffs = calc_length_diffs(l1, l2)
        self.assertEqual(diffs, [1.0, 1.0])

        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)
        l2 = LineString([(0, 0), (0, 20), (0, 40)], srid=3857)
        diffs = calc_length_diffs(l1, l2)
        self.assertEqual(diffs, [0.5, 0.5])

        l1 = LineString([(0, 0), (0, 10), (0, 50), (0, 50)], srid=3857)
        l2 = LineString([(0, 0), (0, 5), (0, 10), (0, 20)], srid=3857)
        diffs = calc_length_diffs(l1, l2)
        self.assertEqual(diffs, [2.0, 8.0, 0.0])

    def test_normalize_sum(self):
        vector = [0, 1, 2, 4]
        normalized = normalize_sum(vector)
        self.assertEqual(sum(normalized), 1)
