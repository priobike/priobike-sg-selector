from django.contrib.gis.geos import LineString
from django.test import TestCase
from routing.matching.bearing import (BearingMatcher, calc_bearing_diffs,
                                      calc_side, get_bearing)


class BearingCalculationTest(TestCase):
    def test_get_bearing(self):
        lat1, lon1 = 0, 10
        lat2, lon2 = 0, 20
        bearing = get_bearing(lat1, lon1, lat2, lon2)
        self.assertEqual(bearing, 90) # east

        lat1, lon1 = 0, 10
        lat2, lon2 = 0, -20
        bearing = get_bearing(lat1, lon1, lat2, lon2)
        self.assertEqual(bearing, 270) # west

        lat1, lon1 = 0, 0
        lat2, lon2 = -10, 0
        bearing = get_bearing(lat1, lon1, lat2, lon2)
        self.assertEqual(bearing, 180) # north

        lat1, lon1 = -10, 0
        lat2, lon2 = 0, 0
        bearing = get_bearing(lat1, lon1, lat2, lon2)
        self.assertEqual(bearing, 0) # south

    def test_calc_bearing_diffs(self):
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        l2 = LineString([(0, 0), (0, -10), (0, -20)], srid=4326)
        diffs = calc_bearing_diffs(l1, l2)
        self.assertEqual(diffs, [180, 180])

    def test_calc_side(self):
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        l2 = LineString([(10, 0), (10, 10), (10, 20)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'left')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'right')

    def test_calc_side_inverted(self):
        """
        Test if the side is computed correctly when the 
        two linestrings are in opposite directions.
        """
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        l2 = LineString([(10, 0), (10, 10), (10, 20)][::-1], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'left')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'right')

    def test_bearing_diff_is_match(self):
        matcher = BearingMatcher(bearing_diff_threshold=45, match_inverted_bearings=False)
        self.assertTrue(matcher.bearing_diff_is_match(0))
        self.assertTrue(matcher.bearing_diff_is_match(44))
        self.assertFalse(matcher.bearing_diff_is_match(90))
        self.assertFalse(matcher.bearing_diff_is_match(136))
        self.assertFalse(matcher.bearing_diff_is_match(180))
        self.assertFalse(matcher.bearing_diff_is_match(224))
        self.assertFalse(matcher.bearing_diff_is_match(270))
        self.assertTrue(matcher.bearing_diff_is_match(316))
        self.assertTrue(matcher.bearing_diff_is_match(360))

        matcher = BearingMatcher(bearing_diff_threshold=45, match_inverted_bearings=True)
        self.assertTrue(matcher.bearing_diff_is_match(0))
        self.assertTrue(matcher.bearing_diff_is_match(44))
        self.assertFalse(matcher.bearing_diff_is_match(90))
        self.assertTrue(matcher.bearing_diff_is_match(136))
        self.assertTrue(matcher.bearing_diff_is_match(180))
        self.assertTrue(matcher.bearing_diff_is_match(224))
        self.assertFalse(matcher.bearing_diff_is_match(270))
        self.assertTrue(matcher.bearing_diff_is_match(316))
        self.assertTrue(matcher.bearing_diff_is_match(360))


        