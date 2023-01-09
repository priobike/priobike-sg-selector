from typing import List

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.geos import fromstr
from shapely.geometry import LineString as ShapelyLineString
from shapely import wkt
from shapely.ops import substring


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
        points = [Point(*coord, srid=system)
                  for coord in system_linestring.coords]

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


def project_onto_route_new(
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
        points = [Point(*coord, srid=system)
                  for coord in system_linestring.coords]

    # First part: projection from lsa to route
    projected_points = []
    fraction_start = None
    fraction_end = None
    for index, point_geometry in enumerate(points):
        # Get the fraction of the route that the point is closest to
        fraction = system_route.project_normalized(point_geometry)
        if fraction_start is None:
            fraction_start = fraction
        if index == len(points)-1:
            fraction_end = fraction
        # Interpolate the point along the route
        projected_points.append(system_route.interpolate_normalized(fraction))

    # Get route part that lies between the first and the last projected point
    shapely_route_linestring = wkt.loads(system_route.wkt)
    """ shapely_route_linestring_relevant = substring(shapely_route_linestring, start_dist=fraction_start, end_dist=fraction_end, normalized=True)  """

    # Second part: Adding of route waypoints to the projection that are not yet included
    # (important for eg corners that are without this maybe not included in the projection because there are not enough waypoints in the lsa
    # linestring to represent the route good enough)
    points_to_add = []

    offset = 0
    # First iterate over pairs of points in the projection
    for index, point_1 in enumerate(projected_points):
        point_2 = projected_points[index + 1]

        # Get where those point are on the route (distance from start)
        point_1_distance = system_route.project(point_1)
        point_2_distance = system_route.project(point_2)

        # This value holds the distance from the upcoming waypoints that are going to be added to the projection
        inserted_point_1_distance = None

        # Get route part that lies between the two points
        shapely_route_linestring_between_the_points = substring(
            shapely_route_linestring, start_dist=point_1_distance, end_dist=point_2_distance)
        # Add this tolerance because otherwise because of conversions and roundings there are false duplicate points
        shapely_route_linestring_between_the_points = shapely_route_linestring_between_the_points.simplify(
            tolerance=0.000000001)

        # Check if it has more points than two (if so there are more points that need to be added to the projection)
        if shapely_route_linestring_between_the_points.geom_type == 'LineString' and len(shapely_route_linestring_between_the_points.coords) > 2:
            for index_2, route_waypoint in enumerate(shapely_route_linestring_between_the_points.coords):
                # First this value is the distance of the first point because no other points got added yet
                if inserted_point_1_distance is None:
                    inserted_point_1_distance = point_1_distance
                # Don't add point at index 0, because this point is already in the projection
                if index_2 > 0:
                    # Get the fraction where between the two (already in the projection existent) points the new point is
                    # (important because at this fraction in the lsa line string there needs to be added a point later to,
                    # such that there is still a 1:1 mapping between points in the projection and lsa linestring)
                    #
                    # ----------|---------------------------------X-----------------------------|---------------
                    #  inserted_point_1_distance       route_waypoint_distance          point_2_distance
                    route_waypoint_distance = system_route.project(
                        Point(route_waypoint, srid=system))
                    distance_diff_outer = point_2_distance - inserted_point_1_distance
                    distance_diff_inner = point_2_distance - route_waypoint_distance
                    fraction_between_points = 1 - \
                        (distance_diff_inner / distance_diff_outer)

                    # Save the information and apply it later in an extra loop
                    points_to_add.append({"index": index + 1 + offset, "fraction": route_waypoint_distance,
                                         "fraction_lsa_linestring": fraction_between_points})

                    # Because the first point changes if a new point gets inserted it need to be saved such that the next fraction gets calculated correctly
                    inserted_point_1_distance = route_waypoint_distance
                    # The offset saves how many new points got added such that they can be inserted at the right index
                    offset += 1
                # If we are at the end of the projected points we end looking for new points (" - 2" because we are always looking in between the next two points)
                if index_2 >= len(shapely_route_linestring_between_the_points.coords) - 2:
                    break
        # If we are at the end of the projected points we end looking for new points (" - 2" because we are always looking in between the next two points)
        if index >= len(projected_points) - 2:
            break

    lsa_points = list(system_linestring.coords)

    # Add the found points to the projection
    for point_to_add in points_to_add:
        projected_points.insert(
            point_to_add["index"], system_route.interpolate(point_to_add["fraction"]))

        # Also add the corresponding counter part (a new point) to the lsa linestring such that the 1:1 mapping between points in the projection and lsa linestring is still true
        # For that the equations how we got the fraction previously (for loop before) need to be re arranged
        # outer_distance_2      -> point_2_distance
        # outer_distance_1      -> inserted_point_1_distance
        # inner_distance        -> route_waypoint_distance
        # distance_diff_outer   -> distance_diff_outer
        # distance_diff_inner   -> distance_diff_inner
        outer_distance_2 = system_linestring.project(
            Point(lsa_points[point_to_add["index"]], srid=system) if not hasattr(lsa_points[point_to_add["index"]], "coords")
            else lsa_points[point_to_add["index"]])
        outer_distance_1 = system_linestring.project(
            Point(lsa_points[point_to_add["index"]-1], srid=system) if not hasattr(lsa_points[point_to_add["index"] - 1], "coords")
            else lsa_points[point_to_add["index"]-1])
        distance_diff_outer = outer_distance_2 - outer_distance_1
        distance_diff_inner = (
            1 - point_to_add["fraction_lsa_linestring"]) * distance_diff_outer
        inner_distance = outer_distance_2 - distance_diff_inner
        lsa_points.insert(
            point_to_add["index"], system_linestring.interpolate(inner_distance))

    # Project back to the original coordinate system
    new_lsa_linestring = LineString(lsa_points, srid=system)
    new_lsa_linestring.transform(linestring.srid)
    projected_linestring = LineString(projected_points, srid=system)
    projected_linestring.transform(linestring.srid)
    return projected_linestring, new_lsa_linestring


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


def get_extended_projected_linestring(lsa_linestring: LineString, route_linestring: LineString) -> LineString:
    """Calculates an extended version of a simple to the route projected linestring,
    such that for some features a longer route section can be used (eg for feature_route_bearing_change.py).
    Args:
        lsa_linestring (LineString): original linestring of the MAP-topology
        route_linestring (LineString): linestring of the complete route
    Returns:
        LineString: extended projected linestring
    """

    # Transform into projection system
    system_lsa_linestring = lsa_linestring.transform(
        settings.LONLAT, clone=True)
    system_route_linestring = route_linestring.transform(
        settings.LONLAT, clone=True)

    # Project the point (the center of the MAP topology linestring) to the route
    center_point_lsa = system_lsa_linestring.interpolate_normalized(0.5)
    distance_point_route = system_route_linestring.project(center_point_lsa)
    center_projected_point_on_route = system_route_linestring.interpolate(
        distance_point_route)

    point_before = None
    point_before_index = None
    before_current_shortest_distance = None
    point_after = None
    point_after_index = None

    # Search for the closest waypoint on the route before the center projected point
    for index, waypoint in enumerate(system_route_linestring.coords):
        distance = system_route_linestring.project(
            Point(waypoint, srid=system_route_linestring.srid))

        # Before the center projected point
        if point_before is None and distance < distance_point_route:
            point_before = waypoint
            point_before_index = index
            before_current_shortest_distance = distance
        elif distance < distance_point_route and distance > before_current_shortest_distance:
            point_before = waypoint
            point_before_index = index
            before_current_shortest_distance = distance
        elif distance > distance_point_route:
            break

    point_after_index = point_before_index + 1
    point_after = system_route_linestring.coords[point_after_index]

    max_distance = 0.0004
    # Get route section before center:
    points_before = [point_before]
    index_before = point_before_index - 1
    if index_before >= 0:
        distance = distance_point_route - system_route_linestring.project(Point(
            system_route_linestring.coords[index_before], srid=system_route_linestring.srid))
    while distance < max_distance and index_before >= 0:
        points_before.append(system_route_linestring.coords[index_before])
        index_before -= 1
        if index_before >= 0:
            distance = distance_point_route - system_route_linestring.project(Point(
                system_route_linestring.coords[index_before], srid=system_route_linestring.srid))
    points_before.reverse()

    # Get route section before center:
    points_after = [point_after]
    index_after = point_after_index + 1
    if index_after < len(system_route_linestring.coords):
        distance = system_route_linestring.project(Point(
            system_route_linestring.coords[index_after], srid=system_route_linestring.srid)) - distance_point_route
    while distance < max_distance and index_after < len(system_route_linestring.coords):
        points_after.append(system_route_linestring.coords[index_after])
        index_after += 1
        if index_after < len(system_route_linestring.coords):
            distance = system_route_linestring.project(Point(
                system_route_linestring.coords[index_after], srid=system_route_linestring.srid)) - distance_point_route

    points = points_before
    points.append(center_projected_point_on_route.coords)
    points.extend(points_after)

    # fill up distance before and after with next virtual/not in route existent waypoint
    if index_before != 0 and distance_point_route - system_route_linestring.project(Point(points[0], srid=system_route_linestring.srid)) < max_distance:
        first_point = system_route_linestring.interpolate(
            distance_point_route - max_distance)
        points.insert(0, first_point.coords)

    if index_after < len(system_route_linestring.coords) and system_route_linestring.project(Point(points[len(points)-1], srid=system_route_linestring.srid)) - distance_point_route < max_distance:
        last_point = system_route_linestring.interpolate(
            distance_point_route + max_distance)

        points.insert(len(points), last_point.coords)

    return LineString(points, srid=system_route_linestring.srid).transform(route_linestring.srid, clone=True)
