from django.contrib.gis.geos import LineString
from django.test import TestCase
from routing.matching.ml.utils import remove_duplicate_coordinates


class DuplicatesTest(TestCase):
    def test_remove_duplicate_coordinates(self):
        l = LineString([(0, 0), (0, 10), (0, 10), (0, 20)], srid=4326)
        l_corrected = remove_duplicate_coordinates(l)
        self.assertEqual(l_corrected, LineString(
            [(0, 0), (0, 10), (0, 20)], srid=4326))

        l = LineString([(0.5, 13.3), (0.4, 10.32), (13.2, 10.2),
                       (13.2, 10.2), (24.5, 4)], srid=4326)
        l_corrected = remove_duplicate_coordinates(l)
        self.assertEqual(l_corrected, LineString(
            [(0.5, 13.3), (0.4, 10.32), (13.2, 10.2), (24.5, 4)], srid=4326))

        l = LineString([(9.9699252, 53.5460158), (9.9698613, 53.546032), (9.9698613, 53.546032), (9.9697971, 53.5460475), (9.9697971, 53.5460475), (9.969797, 53.5460476), (9.9696434, 53.5460828), (9.9696434, 53.5460828), (9.9696434, 53.5460828), (9.9696048, 53.5460912), (9.9695659, 53.5460991), (9.9695266, 53.5461062), (9.969487, 53.5461126), (9.969487, 53.5461126),
                       (9.9694869, 53.5461127), (9.9692517, 53.5461491), (9.9692517, 53.5461491), (9.9692291, 53.5461518), (9.9692058, 53.5461533), (9.9692058, 53.5461533), (9.9692058, 53.5461533), (9.9691834, 53.546154), (9.9691834, 53.546154), (9.9691715, 53.5461541), (9.9691596, 53.5461535), (9.9691477, 53.5461524), (9.969136, 53.5461508), (9.9691288, 53.5461495)], srid=4326)
        l_corrected = remove_duplicate_coordinates(l)
        self.assertEqual(l_corrected, LineString(
            [(9.9699252, 53.5460158), (9.9698613, 53.546032), (9.9697971, 53.5460475), (9.969797, 53.5460476), (9.9696434, 53.5460828), (9.9696048, 53.5460912), (9.9695659, 53.5460991), (9.9695266, 53.5461062), (9.969487, 53.5461126),
             (9.9694869, 53.5461127), (9.9692517, 53.5461491), (9.9692291, 53.5461518), (9.9692058, 53.5461533), (9.9691834, 53.546154), (9.9691715, 53.5461541), (9.9691596, 53.5461535), (9.9691477, 53.5461524), (9.969136, 53.5461508), (9.9691288, 53.5461495)], srid=4326))

        l = LineString([(0, 0), (0, 10), (0, 10), (0, 20)], srid=3857)
        l_corrected = remove_duplicate_coordinates(l)
        self.assertEqual(l_corrected, LineString(
            [(0, 0), (0, 10), (0, 20)], srid=3857))

        l = LineString([(0.5, 13.3), (0.4, 10.32), (13.2, 10.2),
                       (13.2, 10.2), (24.5, 4)], srid=3857)
        l_corrected = remove_duplicate_coordinates(l)
        self.assertEqual(l_corrected, LineString(
            [(0.5, 13.3), (0.4, 10.32), (13.2, 10.2), (24.5, 4)], srid=3857))

        l = LineString([(9.9699252, 53.5460158), (9.9698613, 53.546032), (9.9698613, 53.546032), (9.9697971, 53.5460475), (9.9697971, 53.5460475), (9.969797, 53.5460476), (9.9696434, 53.5460828), (9.9696434, 53.5460828), (9.9696434, 53.5460828), (9.9696048, 53.5460912), (9.9695659, 53.5460991), (9.9695266, 53.5461062), (9.969487, 53.5461126), (9.969487, 53.5461126),
                       (9.9694869, 53.5461127), (9.9692517, 53.5461491), (9.9692517, 53.5461491), (9.9692291, 53.5461518), (9.9692058, 53.5461533), (9.9692058, 53.5461533), (9.9692058, 53.5461533), (9.9691834, 53.546154), (9.9691834, 53.546154), (9.9691715, 53.5461541), (9.9691596, 53.5461535), (9.9691477, 53.5461524), (9.969136, 53.5461508), (9.9691288, 53.5461495)], srid=3857)
        l_corrected = remove_duplicate_coordinates(l)
        self.assertEqual(l_corrected, LineString(
            [(9.9699252, 53.5460158), (9.9698613, 53.546032), (9.9697971, 53.5460475), (9.969797, 53.5460476), (9.9696434, 53.5460828), (9.9696048, 53.5460912), (9.9695659, 53.5460991), (9.9695266, 53.5461062), (9.969487, 53.5461126),
             (9.9694869, 53.5461127), (9.9692517, 53.5461491), (9.9692291, 53.5461518), (9.9692058, 53.5461533), (9.9691834, 53.546154), (9.9691715, 53.5461541), (9.9691596, 53.5461535), (9.9691477, 53.5461524), (9.969136, 53.5461508), (9.9691288, 53.5461495)], srid=3857))
