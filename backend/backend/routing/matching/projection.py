from typing import List

from django.conf import settings
from django.contrib.gis.geos import LineString, Point


def project_onto_route(
    linestring: LineString,
    route: LineString,
    use_route_direction=True,
    system=settings.LONLAT
) -> LineString:
    """
    Projects a linestring onto a route linestring.

    Use the given projection system to perform the projection.
    If `use_route_direction` is True, the direction of the route is used.
    """

    system_linestring = linestring.transform(system, clone=True)
    system_route = route.transform(system, clone=True)

    if use_route_direction:
        points = points_in_route_dir(system_linestring, system_route, system)
    else:
        points = [Point(*coord, srid=system) for coord in system_linestring.coords]

    projected_points = []
    for point_geometry in points:
        # Get the fraction of the route that the point is closest to
        fraction = system_route.project_normalized(point_geometry)
        # Interpolate the point along the route
        projected_points.append(system_route.interpolate_normalized(fraction))

    # Project back to the original coordinate system
    projected_linestring = LineString(projected_points, srid=system)
    projected_linestring.transform(linestring.srid)
    return projected_linestring


def points_in_route_dir(linestring: LineString, route: LineString, system=settings.LONLAT) -> List[Point]:
    """
    Returns the points in the linestring in the order
    which is given by the direction of the route.

    The points are returned in the projection system of the linestring.
    """

    system_linestring = linestring.transform(system, clone=True)
    system_route = route.transform(system, clone=True)

    points = []
    fractions = []
    for coord in system_linestring.coords:
        point_geometry = Point(*coord, srid=system)
        points.append(point_geometry.transform(linestring.srid, clone=True))
        fraction = system_route.project_normalized(point_geometry)
        fractions.append(fraction)

    return [p for p, _ in sorted(zip(points, fractions), key=lambda x: x[1])]
