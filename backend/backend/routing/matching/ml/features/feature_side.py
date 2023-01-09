import time
from typing import List

import numpy as np
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from routing.matching.bearing import calc_side
from ml_evaluation.utils_meta import get_filename


class Side(FeatureExtractor):
    FEATURE_NAMES = [
        "left",
        "right",
        "no_side"
    ]

    FEATURE_TYPES = [
        FeatureType.CATEGORIAL,
        FeatureType.CATEGORIAL,
        FeatureType.CATEGORIAL
    ]

    FEATURE_TYPES_DC = [
        FeatureType.DISCRETE,
        FeatureType.DISCRETE,
        FeatureType.DISCRETE,
    ]

    SUPPORTS_EXTENDED_PROJECTION = True

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
                "left_count": int(np.sum(features_binding_selected[:, 0])),
                "right_count": int(np.sum(features_binding_selected[:, 1])),
                "no_side_count": int(np.sum(features_binding_selected[:, 2]))
            },
            "binding_not_selected": {
                "left_count": int(np.sum(features_binding_not_selected[:, 0])),
                "right_count": int(np.sum(features_binding_not_selected[:, 1])),
                "no_side_count": int(np.sum(features_binding_not_selected[:, 2]))
            }
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()

        lsa_projected_linestring = featureExtractionState.lsa_projected_linestring if not featureExtractionState.config["extended_projections"]\
            else featureExtractionState.lsa_extended_projected_linestring

        side = calc_side(lsa_projected_linestring,
                         featureExtractionState.lsa_system_linestring)

        # Feature denoting the side of the route the linestring is on (one hot encoded)
        if side == "left":
            featureExtractionState.features = np.append(
                featureExtractionState.features, [1, 0, 0])
        elif side == "right":
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 1, 0])
        else:
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 0, 1])

        end = time.time()
        featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
            Timing(base=(end - start), extra=None),
            Timing(base=-524, extra=None),
            Timing(base=-524, extra=None)
        ])
        return featureExtractionState
