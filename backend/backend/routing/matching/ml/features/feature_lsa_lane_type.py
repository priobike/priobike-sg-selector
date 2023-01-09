import time
from typing import List
import numpy as np

from ml_evaluation.utils_meta import get_filename
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from routing.models import LSAMetadata


class LSALaneType(FeatureExtractor):
    FEATURE_NAMES = [
        "only_bike",
        "bike_pedestrian",
        "car_bike",
        "car_bus_bike",
        "bus_bike"
    ]

    FEATURE_TYPES = [
        FeatureType.CATEGORIAL,
        FeatureType.CATEGORIAL,
        FeatureType.CATEGORIAL,
        FeatureType.CATEGORIAL,
        FeatureType.CATEGORIAL
    ]

    FEATURE_TYPES_DC = [
        FeatureType.DISCRETE,
        FeatureType.DISCRETE,
        FeatureType.DISCRETE,
        FeatureType.DISCRETE,
        FeatureType.DISCRETE
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
                "radfahrer_count": int(np.sum(features_binding_selected[:, 0])),
                "radfahrer_fußgänger_count": int(np.sum(features_binding_selected[:, 1])),
                "radfahrer_kfz_count": int(np.sum(features_binding_selected[:, 2])),
                "radfahrer_kfz_busse_count": int(np.sum(features_binding_selected[:, 3])),
                "radfahrer_busse_count": int(np.sum(features_binding_selected[:, 4])),
                "ratio(radfahrer/rest)": f"{int((np.sum(features_binding_selected[:,0]) / (np.sum(features_binding_selected[:,1]) + np.sum(features_binding_selected[:,2]) + np.sum(features_binding_selected[:,3]) + np.sum(features_binding_selected[:,4]))) * 100)}%"
            },
            "binding_not_selected": {
                "radfahrer_count": int(np.sum(features_binding_not_selected[:, 0])),
                "radfahrer_fußgänger_count": int(np.sum(features_binding_not_selected[:, 1])),
                "radfahrer_kfz_count": int(np.sum(features_binding_not_selected[:, 2])),
                "radfahrer_kfz_busse_count": int(np.sum(features_binding_not_selected[:, 3])),
                "radfahrer_busse_count": int(np.sum(features_binding_not_selected[:, 4])),
                "ratio(radfahrer/rest)": f"{int((np.sum(features_binding_not_selected[:,0]) / (np.sum(features_binding_not_selected[:,1]) + np.sum(features_binding_not_selected[:,2]) + np.sum(features_binding_not_selected[:,3]) + np.sum(features_binding_not_selected[:,4]))) * 100)}%"
            }
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()

        lsa_metadata = LSAMetadata.objects.get(lsa=featureExtractionState.lsa)
        # Feature denoting the lane type of the map topology (one hot encoded)
        if lsa_metadata.lane_type == "Radfahrer":
            featureExtractionState.features = np.append(
                featureExtractionState.features, [1, 0, 0, 0, 0])
        elif lsa_metadata.lane_type == 'Fußgänger/Radfahrer':
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 1, 0, 0, 0])
        elif lsa_metadata.lane_type == 'KFZ/Radfahrer':
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 0, 1, 0, 0])
        elif lsa_metadata.lane_type == 'KFZ/Bus/Radfahrer':
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 0, 0, 1, 0])
        else:  # Bus/Radfahrer
            featureExtractionState.features = np.append(
                featureExtractionState.features, [0, 0, 0, 0, 1])

        end = time.time()
        featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
            Timing(base=(end - start), extra=None),
            Timing(base=-524, extra=None),
            Timing(base=-524, extra=None),
            Timing(base=-524, extra=None),
            Timing(base=-524, extra=None)
        ])

        return featureExtractionState
