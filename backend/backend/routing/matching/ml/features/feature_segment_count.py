import time
from typing import List

import numpy as np

from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from ml_evaluation.utils_meta import get_filename


class SegmentCount(FeatureExtractor):
    FEATURE_NAMES = [
        "_"
    ]

    FEATURE_TYPES = [
        FeatureType.NUMERICAL
    ]

    FEATURE_TYPES_DC = [
        FeatureType.DISCRETE,
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
    def get_statistics(features: List[List], labels: List[int]):
        """
        Used for the logs
        """

        features_binding_selected = np.array(
            [features[i] for i in range(len(features)) if labels[i] == 1])
        features_binding_not_selected = np.array(
            [features[i] for i in range(len(features)) if labels[i] == 0])

        statistic = {
            "binding_selected": {
                "lsa_segment_count_mean": np.mean(features_binding_selected[:, 0]),
                "lsa_segment_count_max": np.max(features_binding_selected[:, 0]),
                "lsa_segment_count_min": np.min(features_binding_selected[:, 0]),
                "lsa_segment_count_standard_deviation": np.std(features_binding_selected[:, 0]),
            },
            "binding_not_selected": {
                "lsa_segment_count_mean": np.mean(features_binding_not_selected[:, 0]),
                "lsa_segment_count_max": np.max(features_binding_not_selected[:, 0]),
                "lsa_segment_count_min": np.min(features_binding_not_selected[:, 0]),
                "lsa_segment_count_standard_deviation": np.std(features_binding_not_selected[:, 0]),
            }
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()

        # Feature denoting the number of segments
        featureExtractionState.features = np.append(featureExtractionState.features, [
                                                    len(featureExtractionState.lsa_projected_linestring.coords) - 1])

        end = time.time()
        featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
            Timing(base=end - start, extra=None)
        ])
        return featureExtractionState
