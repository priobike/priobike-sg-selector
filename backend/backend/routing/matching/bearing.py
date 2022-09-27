from typing import List

import numpy as np
from django.conf import settings
from django.contrib.gis.geos import LineString
from routing.matching import ElementwiseRouteMatcher
from routing.matching.length import calc_segment_lengths, normalize_sum
from routing.matching.projection import project_onto_route
from routing.models import SG


def get_linestring_bearing(linestring: LineString) -> float:
    """
    Returns the bearing of a linestring.

    The bearing is the direction the linestring is pointing in.
    The bearing is in the interval [0, 360].
    """
    linestring_transformed = linestring.transform(settings.LONLAT, clone=True)
    if len(linestring_transformed.coords) < 2:
        raise ValueError("LineString must have at least 2 coordinates")

    return get_bearing(*linestring_transformed.coords[0][:2], *linestring_transformed.coords[1][:2])


def get_bearing(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Returns the bearing of a line between two points in the interval [0, 360].

    If the line goes to the north, the bearing is 0.
    If the line goes to the east, the bearing is 90.
    If the line goes to the south, the bearing is 180.
    If the line goes to the west, the bearing is 270.

    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2), cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))

    Source: https://gist.github.com/jeromer/2005586
    """
    lat1r = np.radians(lat1)
    lat2r = np.radians(lat2)

    diffLong = np.radians(lon2 - lon1)

    x = np.sin(diffLong) * np.cos(lat2r)
    y = np.cos(lat1r) * np.sin(lat2r) - (np.sin(lat1r)
            * np.cos(lat2r) * np.cos(diffLong))

    initial_bearing = np.arctan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def calc_bearing_diffs(l1: LineString, l2: LineString) -> List[float]:
    """
    Calculates the bearing differences between two linestrings.

    The bearing differences will be in the interval [0, 360].
    """

    system = settings.LONLAT
    system_l1 = l1.transform(system, clone=True)
    system_l2 = l2.transform(system, clone=True)

    last_p1, last_p2 = None, None
    diffs = []
    for (p1, p2) in zip(system_l1.coords, system_l2.coords):
        if last_p1 is not None and last_p2 is not None:
            bearing_1 = get_bearing(*last_p1[:2], *p1[:2])
            bearing_2 = get_bearing(*last_p2[:2], *p2[:2])
            bearing_diff = np.abs(bearing_1 - bearing_2)
            diffs.append(bearing_diff)
        last_p1, last_p2 = p1, p2

    return diffs


def calc_side(l1: LineString, l2: LineString) -> str:
    """
    Determine if `l2` is on the right or left hand side of `l1`.

    Returns "left" or "right". The calculation is done in the given projection system.

    If `l1` is the route, return if `l2` is on the left or right hand side of the route.
    The decision point is the first point of `l1`. The nearest point on `l2` to the 
    decision point is used to determine the side.

    A visualization of the calculation process:
    
    s--->------>--- l1
    | transition
    n---<------<--- l2

    Where s is the first point of l1 and n is the nearest point on l2 to s.
    The bearing of the transition is used to determine the side, with regards
    to the bearing of l1 itself. Note that l2 can be in the inverted direction of l1.
    """
    if len(l1.coords) <= 1 or len(l2.coords) <= 1:
        raise ValueError("LineStrings must have at least 2 points.")

    system = settings.LONLAT
    system_l1 = l1.transform(system, clone=True)
    system_l2 = l2.transform(system, clone=True)
    nearest_point_on_l2 = system_l2.interpolate(system_l2.project(system_l1.interpolate_normalized(0)))

    transition_bearing = get_bearing(*system_l1.coords[0][:2], *nearest_point_on_l2[:2])
    own_bearing = get_bearing(*system_l1.coords[0][:2], *system_l1.coords[1][:2])

    bearing_diff = round(transition_bearing) - round(own_bearing)

    # Determine the side of the route the linestring is on
    if bearing_diff > 0 and bearing_diff < 180:
        return "right"
    elif bearing_diff > 180 and bearing_diff < 360:
        return "left"
    elif bearing_diff < 0 and bearing_diff > -180:
        return "left"
    elif bearing_diff < -180 and bearing_diff > -360:
        return "right"
    else:
        return "no_side"


class BearingMatcher(ElementwiseRouteMatcher):
    def __init__(
        self,
        bearing_threshold=0.8, # 80% of the linestring must be matched
        bearing_diff_threshold=45, # in degrees
        match_inverted_bearings=False, # dont match sgs in opposite direction of route
        *args, **kwargs
    ):
        """
        Initialize the bearing matcher.

        :param bearing_threshold: Percentage of the connection geometry that must match the route by bearing
        :param bearing_diff_threshold: Degrees difference until a line segment is no longer considered a match
        :param match_inverted_bearings: Match line segments that are 180 degrees inverted from the route
        """
        super().__init__(*args, **kwargs)
        self.bearing_threshold = bearing_threshold
        self.bearing_diff_threshold = bearing_diff_threshold
        self.match_inverted_bearings = match_inverted_bearings

    def bearing_diff_is_match(self, diff: float) -> bool:
        """
        Check if the bearing diff lies within the threshold.

        Only bearing diffs in the interval [0, 360] are considered. Please make sure
        that the bearing diffs are computed in this interval and not e.g. [-180, 180].

        That is, whether it lies in the following intervals:
        - [0, threshold) or (360 - threshold, 360]
        - (180 - threshold, 180 + threshold) but only if inverted bearings are matched
        """

        assert diff >= 0
        assert diff <= 360

        if (diff < self.bearing_diff_threshold) or (diff > (360 - self.bearing_diff_threshold)):
            return True

        if self.match_inverted_bearings:
            if (diff > (180 - self.bearing_diff_threshold)) and (diff < (180 + self.bearing_diff_threshold)):
                return True

        return False

    def match(self, sg: SG, route: LineString) -> bool:
        segment_lengths = []
        bearing_diffs = []

        original_linestring = sg.geometry.transform(self.system, clone=True)
        projected_linestring = project_onto_route(original_linestring, route)
        segment_lengths += calc_segment_lengths(original_linestring)
        bearing_diffs += calc_bearing_diffs(original_linestring, projected_linestring)

        relative_segment_lengths = normalize_sum(segment_lengths)
        matched_bearing_diff_fraction = 0
        for (bearing_diff, pct) in zip(bearing_diffs, relative_segment_lengths):
            if self.bearing_diff_is_match(bearing_diff):
                matched_bearing_diff_fraction += pct

        return matched_bearing_diff_fraction > self.bearing_threshold
