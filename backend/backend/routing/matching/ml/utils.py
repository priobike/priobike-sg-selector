from django.contrib.gis.geos import LineString


def remove_duplicate_coordinates(linestring: LineString) -> LineString:
    """
    Removes duplicate coordinates in a linestring
    """
    unique_coordinates = []
    last_coordinate = None
    for coordinate in linestring.coords:
        if last_coordinate != coordinate:
            unique_coordinates.append(coordinate)

        last_coordinate = coordinate

    return LineString(unique_coordinates, srid=linestring.srid)
