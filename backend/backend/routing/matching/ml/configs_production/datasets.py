from routing.matching.ml.features.feature_point_distances import PointDistances
from routing.matching.ml.features.feature_route_bearing_change import RouteBearingChange
from routing.matching.ml.features.feature_lsa_lane_type import LSALaneType
from routing.matching.ml.features.feature_lengths import Lengths
from routing.matching.ml.features.feature_side import Side
from routing.matching.ml.features.feature_distance import Distance
from routing.matching.ml.features.feature_length_diffs import LengthDiffs
from routing.matching.ml.features.feature_bearing_diffs import BearingDiffs

"""
Copy the config from ml_evaluation.configs.datasets to this file that should be used in production.

Note: Don't forget to also copy the required (trained) models from ml_evaluation.models to routing.matching.ml.models
(the classifier model and if needed the feature transformer model) and the config from ml_evaluation.configs.trainings to 
routing.matching.ml.configs.trainings
"""
config_data_and_features = {
    8603: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation_only_numerical": True,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": True,
        },
        BearingDiffs: [2, 4],
        PointDistances: [3, 4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    }
}
