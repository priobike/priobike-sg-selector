from collections import namedtuple
from typing import Dict, Iterable, Set, Tuple

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.db.models.query import QuerySet
from routing.matching import RouteMatcher
from routing.matching.bearing import calc_side
from routing.models import SG

RouteSection = namedtuple("RouteSection", ["min_fraction", "max_fraction"])


def calc_sections(sgs: Iterable[SG], route: LineString, system=settings.LONLAT) -> Dict[str, RouteSection]:
    """
    Calculate the sections of the route that are covered by the SGs.

    Returns a dict with the section for each SG id,
    where the fractions are in the interval [0, 1].

    Example: if the SG covers the first 100m of a 400m route, the section will be (0, 0.25).
    """

    system_route = route.transform(system, clone=True)

    section_dict = {}
    for sg in sgs:
        min_fraction = 1
        max_fraction = 0
        linestring = sg.geometry.transform(system, clone=True)
        for coord in linestring.coords:
            point_geometry = Point(*coord, srid=system)
            # Get the fraction of the route that the point is closest to
            fraction = system_route.project_normalized(point_geometry)
            min_fraction = min(min_fraction, fraction)
            max_fraction = max(max_fraction, fraction)
        section_dict[sg.id] = RouteSection(min_fraction, max_fraction)

    return section_dict


def calc_distances(sgs: Iterable[SG], route: LineString, system=settings.METRICAL) -> Dict[str, float]:
    """
    Calculate the distances of the SGs to the route.

    The measurement unit of the distances is given by the projection system.
    Use the Mercator projection system for distances in meters.
    """

    system_route = route.transform(system, clone=True)

    distance_dict = {}
    for sg in sgs:
        linestring = sg.geometry.transform(system, clone=True)
        distance_dict[sg.id] = linestring.distance(system_route)

    return distance_dict


def calc_sides(sgs: Iterable[SG], route: LineString) -> Dict[str, str]:
    """
    Calculate the sides of the SGs with regards to the route direction.
    """

    side_dict = {}
    for sg in sgs:
        side_dict[sg.id] = calc_side(route, sg.geometry)
    return side_dict


Overlap = namedtuple("Overlap", ["sg_1_id", "sg_2_id"])


class OverlapMatcher(RouteMatcher):
    def __init__(
        self,
        road_side_threshold=90, # 90 meters
        perfect_match_threshold=5, # 5 meters
        overlap_pct_threshold=0.1, # 10%
        *args, **kwargs
    ):
        """
        Initialize the OverlapMatcher.

        :param road_side_threshold: The maximum difference in distance of meters that
        two SGs can have to be chosen by road side primarily
        :param perfect_match_threshold: The maximum distance of an SG to the route
        to be considereda perfect match to the route
        :param overlap_pct_threshold: The minimum percentage of an overlap between
        two lines to be considered as one
        """
        super().__init__(*args, **kwargs)
        self.road_side_threshold = road_side_threshold
        self.perfect_match_threshold = perfect_match_threshold
        self.overlap_pct_threshold = overlap_pct_threshold

    def calc_overlaps(self, sections: Dict[str, RouteSection]) -> Set[Overlap]:
        """
        Calculate the overlaps between the sections of the route.

        Returns a list of overlaps. To further understand the overlap, see the example below:

            0.2        0.6
            --------------
        -------------
        0.1       0.5

        The overlap is between 0.2 and 0.5, i.e. 0.3 and therefore 0.3/0.5 = 0.6 -> 60%
        Now, if the overlap is above a given threshold, the two SGs are considered to be overlapping.
        """

        overlaps = set()
        considered_sg_ids = set()
        for sg_1_id, s1 in sections.items():
            considered_sg_ids.add(sg_1_id)
            for sg_2_id, s2 in sections.items():
                if sg_2_id in considered_sg_ids:
                    continue

                start_of_overlap = max(s1.min_fraction, s2.min_fraction)
                end_of_overlap = min(s1.max_fraction, s2.max_fraction)
                max_dist = max(s1.max_fraction, s2.max_fraction) - min(s1.min_fraction, s2.min_fraction)
                overlap_pct = (end_of_overlap - start_of_overlap) / max_dist if max_dist > 0 else 0

                if overlap_pct < self.overlap_pct_threshold:
                    continue

                overlaps.add(Overlap(sg_1_id, sg_2_id))

        return overlaps

    def matches(self, sgs: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        """
        Remove SGs that have overlaps with other SGs with regards to the route,
        but have a worse match to the route.
        """
        sgs, route = super().matches(sgs, route)

        sections = calc_sections(sgs, route)
        distances = calc_distances(sgs, route)
        sides = calc_sides(sgs, route)
        overlaps = self.calc_overlaps(sections)

        excluded_sgs = set()
        for sg_id_1, sg_id_2 in overlaps:
            dist_1, dist_2 = distances[sg_id_1], distances[sg_id_2]
            side_1, side_2 = sides[sg_id_1], sides[sg_id_2]

            # If there is at least one perfect match, decide purely by the distance
            if dist_1 <= self.perfect_match_threshold or dist_2 <= self.perfect_match_threshold:
                if dist_1 > dist_2:
                    excluded_sgs.add(sg_id_1)
                else:
                    excluded_sgs.add(sg_id_2)

            # If the distances are within a certain threshold,
            # decide by the side of the route (prefer right hand side)
            elif abs(dist_1 - dist_2) < self.road_side_threshold and side_1 != side_2:
                if side_1 == "left":
                    excluded_sgs.add(sg_id_1)
                if side_2 == "left":
                    excluded_sgs.add(sg_id_2)

            # Otherwise, decide by the distance
            elif dist_1 > dist_2:
                excluded_sgs.add(sg_id_1)
            else:
                excluded_sgs.add(sg_id_2)

        sgs = sgs.exclude(id__in=excluded_sgs)
        return sgs, route
