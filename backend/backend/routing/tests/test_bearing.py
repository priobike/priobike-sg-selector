from django.contrib.gis.geos import LineString
from django.test import TestCase
from routing.matching.bearing import (BearingMatcher, calc_bearing_diffs,
                                      calc_side, get_bearing,
                                      get_linestring_bearing)


class BearingCalculationTest(TestCase):
    def test_get_bearing(self):
        lat1, lon1 = 0, 10
        lat2, lon2 = 0, 20
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(bearing, 90) # east

        lat1, lon1 = 0, 10
        lat2, lon2 = 0, -20
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(bearing, 270) # west

        lat1, lon1 = 0, 0
        lat2, lon2 = -10, 0
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(bearing, 180) # south

        lat1, lon1 = -10, 0
        lat2, lon2 = 0, 0
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(bearing, 0) # north
        
        lat1, lon1 = 0, 0
        lat2, lon2 = 10, 10
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(round(bearing), 45) # north east
        
        lat1, lon1 = 0, 0
        lat2, lon2 = -10, 10
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(round(bearing), 135) # south east

        lat1, lon1 = 0, 0
        lat2, lon2 = -10, -10
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(round(bearing), 225) # south west
        
        lat1, lon1 = 0, 0
        lat2, lon2 = 10, -10
        bearing = get_bearing(lon1, lat1, lon2, lat2)
        self.assertEqual(round(bearing), 315) # north west


    def test_calc_bearing_diffs(self):
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        l2 = LineString([(0, 0), (0, -10), (0, -20)], srid=4326)
        diffs = calc_bearing_diffs(l1, l2)
        self.assertEqual(diffs, [180, 180])
        
        l1 = LineString([(0, 0), (0, 10)], srid=4326)
        l2 = LineString([(0, 0), (10, 10)], srid=4326)
        diffs = calc_bearing_diffs(l1, l2)
        self.assertEqual(round(diffs[0]), 45)
        
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        l2 = LineString([(0, 0), (10, 10), (10, 20)], srid=4326)
        diffs = calc_bearing_diffs(l1, l2)
        self.assertEqual(round(diffs[0]), 45)
        self.assertEqual(round(diffs[1]), 0)
        
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        l2 = LineString([(0, 0), (-10, -10), (-20, 0)], srid=4326)
        diffs = calc_bearing_diffs(l1, l2)
        self.assertEqual(round(diffs[0]), 225)
        self.assertEqual(round(diffs[1]), 315)
        
        self.assertRaises(TypeError, calc_bearing_diffs, l1, l2, 3857)


    def test_calc_side(self):
        l1 = LineString([(10, 0), (10, 10), (10, 20)], srid=4326)
        l2 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'left')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'right')
        
        l1 = LineString([(0, 0), (-10, 0), (-20, 0)], srid=4326)
        l2 = LineString([(10, 0), (10, 10), (10, 20)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'no_side')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'left')
        
        l1 = LineString([(0, 0), (-10, 0), (-20, 0)], srid=4326)
        l2 = LineString([(0, 10), (0, 20), (0, 30)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'right')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'no_side')
        
        l1 = LineString([(0, 0), (-10, 0), (-20, 0)], srid=4326)
        l2 = LineString([(-5, 5), (-15, 20)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'right')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'left')        
        
        l1 = LineString([(0, 0), (2, -2), (4, -4)], srid=4326)
        l2 = LineString([(0, -2), (-2, -4), (-4,-6)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'right')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'no_side')     
        
        l1 = LineString([(0, 0), (0, -5), (0, -10)], srid=4326)
        l2 = LineString([(5, -5), (10, -10), (15,-15)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'left')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'right')     
        
        l1 = LineString([(0, 0), (0, -5), (0, -10)], srid=4326)
        l2 = LineString([(0, 5), (-5, 5), (-10,5)], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'no_side')
        side = calc_side(l2, l1)
        self.assertEqual(side, 'left') 
        

    def test_calc_side_inverted(self):
        """
        Test if the side is computed correctly when the 
        two linestrings are in opposite directions.
        """
        l1 = LineString([(0, 0), (0, 10), (0, 20)], srid=4326)
        l2 = LineString([(10, 0), (10, 10), (10, 20)][::-1], srid=4326)
        side = calc_side(l1, l2)
        self.assertEqual(side, 'right')
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

    def test_get_linestring_bearing(self):
        linestring = LineString([(10, 0), (20, 0)], srid=4326).transform(3857, clone=True)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(bearing, 90) # east

        linestring = LineString([(10, 0), (-20, 0)], srid=4326)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(bearing, 270) # west

        linestring = LineString([(0, 0), (0, -10)], srid=4326).transform(3857, clone=True)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(bearing, 180) # south

        linestring = LineString([(0, -10), (0, 0)], srid=4326)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(bearing, 0) # north
        
        linestring = LineString([(0, 0), (10, 10)], srid=4326).transform(3857, clone=True)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(round(bearing), 45) # north east
        
        linestring = LineString([(0, 0), (10, -10)], srid=4326)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(round(bearing), 135) # south east

        linestring = LineString([(0, 0), (-10, -10)], srid=4326).transform(3857, clone=True)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(round(bearing), 225) # south west
        
        linestring = LineString([(0, 0), (-10, 10)], srid=4326)
        bearing = get_linestring_bearing(linestring)
        self.assertEqual(round(bearing), 315) # north west
