import time
from typing import List

import numpy as np
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from routing.matching.bearing import calc_bearing_diffs
from ml_evaluation.utils_meta import get_filename


class BearingDiffs(FeatureExtractor):
    FEATURE_NAMES = [
        "mean",
        "mean_first_last",
        "max",
        "max_first_last",
        "min",
        "min_first_last",
        "last",
        "first"
    ]

    FEATURE_TYPES = [
        FeatureType.NUMERICAL,
        FeatureType.NUMERICAL,
        FeatureType.NUMERICAL,
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
            "overall_first_last_mean": np.mean(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "overall_first_last_mean_max": np.max(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "overall_first_last_mean_min": np.min(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "overall_max": np.max(feature_bindings[:, indices.index(2)]) if 2 in indices else None,
            "overall_max_mean": np.mean(feature_bindings[:, indices.index(2)]) if 2 in indices else None,
            "overall_first_last_max": np.max(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "overall_first_last_max_mean": np.mean(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "overall_min": np.min(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
            "overall_min_mean": np.mean(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
            "overall_first_last_min": np.min(feature_bindings[:, indices.index(5)]) if 5 in indices else None,
            "overall_first_last_min_mean": np.mean(feature_bindings[:, indices.index(5)]) if 5 in indices else None,
            "last_bearing_diff_mean": np.mean(feature_bindings[:, indices.index(6)]) if 6 in indices else None,
            "last_bearing_diff_max": np.max(feature_bindings[:, indices.index(6)]) if 6 in indices else None,
            "last_bearing_diff_min": np.min(feature_bindings[:, indices.index(6)]) if 6 in indices else None,
            "first_bearing_diff_mean": np.mean(feature_bindings[:, indices.index(7)]) if 7 in indices else None,
            "first_bearing_diff_max": np.max(feature_bindings[:, indices.index(7)]) if 7 in indices else None,
            "first_bearing_diff_min": np.min(feature_bindings[:, indices.index(7)]) if 7 in indices else None,
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
            "binding_selected": BearingDiffs.get_statistic_for_one_class(features_binding_selected, feature_indices),
            "binding_not_selected": BearingDiffs.get_statistic_for_one_class(features_binding_not_selected, feature_indices)
        }

        return statistic

    def get_feature(self, bearing_diffs, index):
        if index == 0:
            # Mean bearing diff
            return np.mean(bearing_diffs)
        elif index == 1:
            # Mean bearing diff between first and last segment
            return ((bearing_diffs[-1] + bearing_diffs[0]) / 2)
        elif index == 2:
            # Max bearing diff
            return np.max(bearing_diffs)
        elif index == 3:
            # Max bearing diff between first and last segment
            return (bearing_diffs[-1] if bearing_diffs[-1] > bearing_diffs[0] else bearing_diffs[0])
        elif index == 4:
            # Min bearing diff
            return np.min(bearing_diffs)
        elif index == 5:
            # Min bearing diff between first and last segment
            return (bearing_diffs[-1] if bearing_diffs[-1] < bearing_diffs[0] else bearing_diffs[0])
        elif index == 6:
            # Last bearing diff
            return bearing_diffs[-1]
        elif index == 7:
            # First bearing diff
            return bearing_diffs[0]
        else:
            raise Exception("Chosen feature index not existent.")

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()
        # Features related to the bearing of the linestring
        bearing_diffs = calc_bearing_diffs(
            featureExtractionState.lsa_system_linestring, featureExtractionState.lsa_projected_linestring)
        end = time.time()
        base_time = end - start

        if BearingDiffs not in featureExtractionState.config or len(featureExtractionState.config[BearingDiffs]) < 1:
            return featureExtractionState

        if bearing_diffs:
            for feature in featureExtractionState.config[BearingDiffs]:
                start = time.time()
                featureExtractionState.features = np.append(featureExtractionState.features, [
                    self.get_feature(bearing_diffs, feature)
                ])
                end = time.time()
                featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                    Timing(base=base_time, extra=end - start)
                ])
        else:
            featureExtractionState.features = np.append(featureExtractionState.features, [
                0.0 for _ in featureExtractionState.config[BearingDiffs]
            ])
            featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                Timing(base=base_time, extra=None) for _ in featureExtractionState.config[BearingDiffs]
            ])

        return featureExtractionState
