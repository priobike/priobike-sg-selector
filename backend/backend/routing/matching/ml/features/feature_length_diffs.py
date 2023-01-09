import time
from typing import List
from ml_evaluation.utils_meta import get_filename

import numpy as np
from django.conf import settings
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from routing.matching.length import calc_length_diffs


class LengthDiffs(FeatureExtractor):
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
        FeatureType.CONTINUOUS,
    ]

    SUPPORTS_EXTENDED_PROJECTION = False

    def __init__(self, *args, **kwargs):
        """
        Initialize the length diffs extractor.
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
            "last_length_diff_mean": np.mean(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "last_length_diff_max": np.max(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "last_length_diff_min": np.min(feature_bindings[:, indices.index(3)]) if 3 in indices else None,
            "first_length_diff_mean": np.mean(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
            "first_length_diff_max": np.max(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
            "first_length_diff_min": np.min(feature_bindings[:, indices.index(4)]) if 4 in indices else None,
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
            "binding_selected": LengthDiffs.get_statistic_for_one_class(features_binding_selected, feature_indices),
            "binding_not_selected": LengthDiffs.get_statistic_for_one_class(features_binding_not_selected, feature_indices),
        }
        return statistic

    def get_feature(self, length_diffs, index):
        if index == 0:
            # Mean length diff
            return np.mean(length_diffs)
        elif index == 1:
            # Max length diff
            return np.max(length_diffs),
        elif index == 2:
            # Min length diff
            return np.min(length_diffs),
        elif index == 3:
            # Last length diff
            return length_diffs[-1],
        elif index == 4:
            # First length diff
            return length_diffs[0],
        else:
            raise Exception("Chosen feature index not existent.")

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        if LengthDiffs not in featureExtractionState.config or len(featureExtractionState.config[LengthDiffs]) < 1:
            return featureExtractionState

        start = time.time()
        system = settings.METRICAL
        # Features related to the length of the linestring
        length_diffs = calc_length_diffs(featureExtractionState.lsa_system_linestring,
                                         featureExtractionState.lsa_projected_linestring, system=system)
        end = time.time()
        base_time = end - start

        if length_diffs:
            for feature in featureExtractionState.config[LengthDiffs]:
                start = time.time()
                featureExtractionState.features = np.append(featureExtractionState.features, [
                    self.get_feature(length_diffs, feature)
                ])
                end = time.time()
                featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                    Timing(base=base_time, extra=end - start)
                ])
        else:
            featureExtractionState.features = np.append(featureExtractionState.features, [
                0.0 for _ in featureExtractionState.config[LengthDiffs]
            ])
            featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                Timing(base=base_time, extra=None) for _ in featureExtractionState.config[LengthDiffs]
            ])

        return featureExtractionState
