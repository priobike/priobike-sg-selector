import time
from typing import List

import numpy as np
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from ml_evaluation.utils_meta import get_filename


class Distance(FeatureExtractor):
    FEATURE_NAMES = [
        "_"
    ]

    FEATURE_TYPES = [
        FeatureType.NUMERICAL,
    ]

    FEATURE_TYPES_DC = [
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
                "distance_mean": np.mean(features_binding_selected[:, 0]),
                "distance_max": np.max(features_binding_selected[:, 0]),
                "distance_min": np.min(features_binding_selected[:, 0]),
                "distance_standard_deviation": np.std(features_binding_selected[:, 0]),
            },
            "binding_not_selected": {
                "distance_mean": np.mean(features_binding_not_selected[:, 0]),
                "distance_max": np.max(features_binding_not_selected[:, 0]),
                "distance_min": np.min(features_binding_not_selected[:, 0]),
                "distance_standard_deviation": np.std(features_binding_not_selected[:, 0]),
            }
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()
        # Distance of the linestring from the route
        featureExtractionState.features = np.append(featureExtractionState.features, [
                                                    featureExtractionState.lsa_system_linestring.distance(featureExtractionState.route_system_linestring)])
        end = time.time()
        featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
            Timing(base=end - start, extra=None)
        ])

        return featureExtractionState
