from django.contrib.gis.geos import LineString
from django.test import TestCase
from routing.matching.projection import points_in_route_dir, project_onto_route


class ProjectionCalculationTest(TestCase):
    def test_project_onto_route(self):
        route = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)
        sg = LineString([(10, 0), (10, 10), (10, 20)], srid=3857)
        projected_sg = project_onto_route(sg, route)
        asserted_sg = LineString([(0, 0), (0, 10), (0, 20)], srid=3857)     

        self.assertEqual(len(projected_sg.coords), len(asserted_sg.coords))
        for (x_p, y_p), (x_a, y_a) in zip(projected_sg.coords, asserted_sg.coords):
            self.assertAlmostEqual(x_p, x_a)
            self.assertAlmostEqual(y_p, y_a)

    def test_points_in_route_dir(self):
        route_points = [(0, 0), (0, 10), (0, 20)]
        route = LineString(route_points, srid=3857)
        sg = LineString(route_points[::-1], srid=3857)
        points = points_in_route_dir(sg, route)

        self.assertEqual(len(points), 3)
        for (r_x, r_y), (x, y) in zip(route_points, points):
            self.assertAlmostEqual(r_x, x)
            self.assertAlmostEqual(r_y, y)        
