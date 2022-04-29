from typing import List

import numpy as np
from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from routing.matching import ElementwiseRouteMatcher
from routing.matching.projection import project_onto_route
from routing.models import SignalGroup


def calc_segment_lengths(linestring: LineString, system=settings.METRICAL) -> List[float]:
    """
    Calculates the lengths of the line segments of a linestring.

    The output format will depend on the system. Use the Mercator projection
    to obtain the lengths in meters.
    """
    system_linestring = linestring.transform(system, clone=True)

    lengths = []
    last_point = None
    for coord in system_linestring.coords:
        point = Point(*coord[:2], srid=system)
        if last_point is not None:
            segment_length = point.distance(last_point)
            lengths.append(segment_length)
        last_point = point

    return lengths


def calc_length_diffs(l1: LineString, l2: LineString, system=settings.METRICAL) -> List[float]:
    """
    Calculates the segmentwise length differences between two linestrings.

    The length differences will be one of the following:
    - 0.0: Exclusively one of both linestrings has a length of 0
    - 1.0: Both linestrings have the same length or both have a length of 0
    - <float>: Otherwise
    """

    system_l1 = l1.transform(system, clone=True)
    system_l2 = l2.transform(system, clone=True)

    lengths_l1 = calc_segment_lengths(system_l1, system=system)
    lengths_l2 = calc_segment_lengths(system_l2, system=system)

    diffs = []
    for partial_length_1, partial_length_2 in zip(lengths_l1, lengths_l2):
        if partial_length_1 == partial_length_2:
            # Catch the case where both lines have length 0
            diffs.append(1.0)
        elif partial_length_1 == 0 or partial_length_2 == 0:
            # Prevent zero division consistently
            diffs.append(0.0)
        else:
            diffs.append(abs(partial_length_1 / partial_length_2))

    return diffs


def normalize_sum(vector: List[float]) -> List[float]:
    """
    Normalize a list of floats so that the sum of all values is 1.
    """
    norm = np.linalg.norm(vector, ord=1)
    if norm == 0:
        norm = np.finfo(vector.dtype).eps
    return vector / norm


class LengthMatcher(ElementwiseRouteMatcher):
    def __init__(
        self,
        length_threshold=0.5, # at least 50% of the segments must match
        length_diff_threshold=0.8, # 80% of the length must be matched
        *args, **kwargs
    ):
        """
        Initialize the LengthMatcher.

        :param length_threshold: The percentage of the connection geometry that must match the route by length
        :param length_diff_threshold: The maximum difference in length until segments are not considered matches
        """
        super().__init__(*args, **kwargs)
        self.length_threshold = length_threshold
        self.length_diff_threshold = length_diff_threshold

    def length_diff_is_match(self, diff: float) -> bool:
        """
        Check if the length diff lies within the threshold.

        That is, whether it lies in the interval [1 - threshold, 1 + threshold].
        """

        if diff < (1 - self.length_diff_threshold):
            return False
        if diff > (1 + self.length_diff_threshold):
            return False
        return True

    def match(self, sg: SignalGroup, route: LineString) -> bool:
        segment_lengths = []
        length_diffs = []

        original_linestring = sg.geometry.transform(self.system, clone=True)
        projected_linestring = project_onto_route(original_linestring, route)
        segment_lengths += calc_segment_lengths(original_linestring)
        length_diffs += calc_length_diffs(original_linestring, projected_linestring)

        relative_segment_lengths = normalize_sum(segment_lengths)
        matched_length_diff_fraction = 0
        for (length_diff, pct) in zip(length_diffs, relative_segment_lengths):
            if self.length_diff_is_match(length_diff):
                matched_length_diff_fraction += pct

        return matched_length_diff_fraction > self.length_threshold
