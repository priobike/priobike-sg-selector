import time
from typing import List

import numpy as np
from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from ml_evaluation.utils_meta import get_filename


def calc_points_distances(l1: LineString, l2: LineString) -> List[float]:
    """
    Calculates the distances between each points of two linestrings. (linestrings must have the same amount of points)
    """

    if len(l1.coords) != len(l2.coords):
        raise Exception("Linestrings must have the same amount of points!")

    system = settings.METRICAL

    system_l1 = l1.transform(system, clone=True)
    system_l2 = l2.transform(system, clone=True)

    diffs = []
    for (p1, p2) in zip(system_l1.coords, system_l2.coords):
        distance = Point(p1, srid=system_l1.srid).distance(
            Point(p2, srid=system_l1.srid))
        diffs.append(distance)

    return diffs


class PointDistances(FeatureExtractor):
    FEATURE_NAMES = [
        "mean",
        "max",
        "min",
        "last",
        "first"
    ]

    FEATURE_TYPES = [
        FeatureType.NUMERICAL,
        FeatureType.NUMERICAL,
        FeatureType.NUMERICAL,
        FeatureType.NUMERICAL,
        FeatureType.NUMERICAL
    ]

    FEATURE_TYPES_DC = [
        FeatureType.CONTINUOUS,
        FeatureType.CONTINUOUS,
        FeatureType.CONTINUOUS,
        FeatureType.CONTINUOUS,
        FeatureType.CONTINUOUS
    ]

    SUPPORTS_EXTENDED_PROJECTION = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the bearing diffs extractor.
        """
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_name_of_file():
        return get_filename()

    @staticmethod
    def get_statistic_for_one_class(feature_bindings, indices):
        return {
            "overall_mean": np.mean(feature_bindings[:, indices.index(0)]) if 0 in indices else None,
            "overall_mean_max": np.max(feature_bindings[:, indices.index(0)]) if 0 in indices else None,
            "overall_mean_min": np.min(feature_bindings[:, indices.index(0)]) if 0 in indices else None,
            "overall_max": np.max(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "overall_max_mean": np.mean(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "overall_min": np.min(feature_bindings[:, indices.index(2)]) if 2 in indices else None,
            "overall_min_mean": np.mean(feature_bindings[:, indices.index(2)]) if 2 in indices else None,
            "last_bearing_diff_mean": np.mean(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "last_bearing_diff_max": np.max(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "last_bearing_diff_min": np.min(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "first_bearing_diff_mean": np.mean(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
            "first_bearing_diff_max": np.max(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
            "first_bearing_diff_min": np.min(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
        }

    @staticmethod
    def get_statistics(features: List[List], labels: List[int], feature_indices: List[int]):
        """
        Used for the logs
        """

        features_binding_selected = np.array(
            [features[i] for i in range(len(features)) if labels[i] == 1])
        features_binding_not_selected = np.array(
            [features[i] for i in range(len(features)) if labels[i] == 0])

        statistic = {
            "binding_selected": PointDistances.get_statistic_for_one_class(features_binding_selected, feature_indices),
            "binding_not_selected": PointDistances.get_statistic_for_one_class(features_binding_not_selected, feature_indices)
        }
        return statistic

    def get_feature(self, point_distances, index):
        if index == 0:
            # Mean distance
            return np.mean(point_distances),
        elif index == 1:
            # Max distance
            return np.max(point_distances),
        elif index == 2:
            # Min distance
            return np.min(point_distances),
        elif index == 3:
            # Last distance
            return point_distances[-1],
        elif index == 4:
            # First distance
            return point_distances[0],
        else:
            raise Exception("Chosen feature index not existent.")

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:

        if PointDistances not in featureExtractionState.config or len(featureExtractionState.config[PointDistances]) < 1:
            return featureExtractionState

        start = time.time()
        # Features related to the distance differences between the points of the original map topology and the projected map topology
        point_distances = calc_points_distances(
            featureExtractionState.lsa_system_linestring, featureExtractionState.lsa_projected_linestring)
        end = time.time()
        base_time = end - start

        if point_distances:
            for feature in featureExtractionState.config[PointDistances]:
                start = time.time()
                featureExtractionState.features = np.append(featureExtractionState.features, [
                    self.get_feature(point_distances, feature)
                ])
                end = time.time()
                featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                    Timing(base=base_time, extra=end - start)
                ])
        else:
            featureExtractionState.features = np.append(featureExtractionState.features, [
                0.0 for _ in featureExtractionState.config[PointDistances]
            ])
            featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                Timing(base=base_time, extra=None) for _ in featureExtractionState.config[PointDistances]
            ])

        return featureExtractionState
