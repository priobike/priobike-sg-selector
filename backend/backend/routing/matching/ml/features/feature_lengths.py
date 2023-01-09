import time
from typing import List
from ml_evaluation.utils_meta import get_filename

import numpy as np
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState


class Lengths(FeatureExtractor):
    FEATURE_NAMES = [
        "map_topology",
        "projected_map_topology"
    ]

    FEATURE_TYPES = [
        FeatureType.NUMERICAL,
        FeatureType.NUMERICAL
    ]

    FEATURE_TYPES_DC = [
        FeatureType.CONTINUOUS,
        FeatureType.CONTINUOUS
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
            "lsa_length_mean": np.mean(feature_bindings[:, indices.index(0)]) if 0 in indices else None,
            "lsa_length_max": np.max(feature_bindings[:, indices.index(0)]) if 0 in indices else None,
            "lsa_length_min": np.min(feature_bindings[:, indices.index(0)]) if 0 in indices else None,
            "lsa_length_standard_deviation": np.std(feature_bindings[:, indices.index(0)]) if 0 in indices else None,
            "projected_lsa_length_mean": np.mean(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "projected_lsa_length_max": np.max(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "projected_lsa_length_min": np.min(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
            "projected_lsa_length_standard_deviation": np.std(feature_bindings[:, indices.index(1)]) if 1 in indices else None,
        },

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
            "binding_selected": Lengths.get_statistic_for_one_class(features_binding_selected, feature_indices),
            "binding_not_selected": Lengths.get_statistic_for_one_class(features_binding_not_selected, feature_indices)
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:

        if Lengths not in featureExtractionState.config or len(featureExtractionState.config[Lengths]) < 1:
            return featureExtractionState

        for feature in featureExtractionState.config[Lengths]:
            if feature == 0:
                start = time.time()
                # Features denoting the length of the linestrings
                featureExtractionState.features = np.append(featureExtractionState.features, [
                    featureExtractionState.lsa_system_linestring.length,
                ])
                end = time.time()
                featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                    Timing(base=end - start, extra=None)
                ])
            elif feature == 1:
                start = time.time()
                # Features denoting the length of the linestrings
                featureExtractionState.features = np.append(featureExtractionState.features, [
                    featureExtractionState.lsa_projected_linestring.length,
                ])
                end = time.time()
                featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
                    Timing(base=end - start, extra=None)
                ])
            else:
                raise Exception("Chosen feature index not existent.")

        return featureExtractionState
