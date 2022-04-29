from unittest.mock import MagicMock

from django.contrib.gis.geos import LineString
from django.test import TestCase
from routing.matching.overlap import (OverlapMatcher, RouteSection,
                                      calc_distances, calc_sections,
                                      calc_sides)


class OverlapCalculationTest(TestCase):
    mocked_sgs = [
        MagicMock(id="SignalGroup1", geometry=LineString([(0, 0), (0, 10), (0, 20)], srid=3857)),
        MagicMock(id="SignalGroup2", geometry=LineString([(0, 0), (10, 0), (10, 10)], srid=3857)),
    ]
    route = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)

    def test_calc_sections(self):
        sections = calc_sections(self.mocked_sgs, self.route)
        self.assertEqual(len(sections), 2)

        section = sections["SignalGroup1"]
        self.assertEqual(section.min_fraction, 0.0)
        # Projection covers the whole route
        self.assertEqual(section.max_fraction, 1.0)

        section = sections["SignalGroup2"]
        self.assertEqual(section.min_fraction, 0.0)
        # Projection only covers 50% of the route
        self.assertEqual(section.max_fraction, 0.5)

    def test_calc_distances(self):
        """
        Validate that the distances are calculated correctly.

        The distance should be defined as the distance between the start of the
        route and the start of the SignalGroups.
        """
        distance_dict = calc_distances(self.mocked_sgs, self.route)
        self.assertEqual(len(distance_dict), 2)
        for _, distance in distance_dict.items():
            self.assertEqual(distance, 0)

    def test_calc_sides(self):
        side_dict = calc_sides(self.mocked_sgs, self.route)
        self.assertEqual(len(side_dict), 2)
        for _, side in side_dict.items():
            self.assertEqual(side, "left")

    def test_calc_overlaps(self):
        matcher = OverlapMatcher(overlap_pct_threshold=0.5)
        sections = {
            "SignalGroup1": RouteSection(0.2, 0.6),
            "SignalGroup2": RouteSection(0.1, 0.5),
        }
        overlaps = matcher.calc_overlaps(sections)
        self.assertEqual(len(overlaps), 1)
        overlap = next(iter(overlaps))
        self.assertTrue("SignalGroup1" in [overlap.sg_1_id, overlap.sg_2_id])
        self.assertTrue("SignalGroup2" in [overlap.sg_1_id, overlap.sg_2_id])
