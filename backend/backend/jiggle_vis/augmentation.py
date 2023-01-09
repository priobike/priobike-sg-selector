from django.contrib.gis.geos.linestring import LineString as GEOSLineString
from shapely.geometry import LineString as ShapelyLineString
from shapely import affinity, wkt
import numpy as np
from django.contrib.gis.geos import fromstr

def jiggle_linestring(  geos_linestring: GEOSLineString, \
                        rotation_lower_bound: int = -3, rotation_upper_bound: int = 3, \
                        scale_lower_bound: float = 0.975, scale_upper_bound: float = 1.025, \
                        translation_x_lower_bound: int = -5, translation_x_upper_bound: int = 5, \
                        translation_y_lower_bound: int = -5, translation_y_upper_bound: int = 5):
    shapely_linestring: ShapelyLineString = wkt.loads(geos_linestring.wkt)

    rotation = np.random.uniform(rotation_lower_bound, rotation_upper_bound)
    shapely_linestring = affinity.rotate(shapely_linestring, rotation, origin='centroid')

    scale = np.random.uniform(scale_lower_bound, scale_upper_bound)
    shapely_linestring = affinity.scale(shapely_linestring, scale, origin='centroid')

    translation_x_m = np.random.uniform(translation_x_lower_bound, translation_x_upper_bound)
    translation_y_m = np.random.uniform(translation_y_lower_bound, translation_y_upper_bound)
    # 111_111 m per degree is only a rough estimate but enough for small offsets
    translation_lat = translation_x_m / 111_111
    translation_lon = translation_y_m / 111_111
    shapely_linestring = affinity.translate(
        shapely_linestring,
        xoff=translation_lon,
        yoff=translation_lat,
    )

    return fromstr(shapely_linestring.wkt, srid=geos_linestring.srid)