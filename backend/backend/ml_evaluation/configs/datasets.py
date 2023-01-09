from routing.matching.ml.features.feature_point_distances import PointDistances
from routing.matching.ml.features.feature_street_crossings import StreetCrossings
from routing.matching.ml.features.feature_route_bearing_change import RouteBearingChange
from routing.matching.ml.features.feature_route_streets import RouteStreets
from routing.matching.ml.features.feature_lsa_lane_type import LSALaneType
from routing.matching.ml.features.feature_lengths import Lengths
from routing.matching.ml.features.feature_segment_count import SegmentCount
from routing.matching.ml.features.feature_side import Side
from routing.matching.ml.features.feature_distance import Distance
from routing.matching.ml.features.feature_length_diffs import LengthDiffs
from routing.matching.ml.features.feature_bearing_diffs import BearingDiffs

config_data_and_features = {
    4: {
        "extended_projections": False,
        "projection_method": "new",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, Distance, Lengths, SegmentCount, Side, LSALaneType, RouteBearingChange, StreetCrossings, RouteStreets, PointDistances]
    },
    # Ab hier mit sortierten Features und configs nicht mehr bearbeiten! Nur neue hinzufügen
    5: {
        "extended_projections": False,
        "projection_method": "new",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Ab hier categorials one hot encoded
    6: {
        "extended_projections": False,
        "projection_method": "new",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },


    # --------------- EVALUATION: ENTFERNEN DUPLIKATE ---------------
    7: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": True,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    8: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },


    # --------------- EVALUATION: PROJEKTIONSMETHODEN ---------------
    9: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    10: {
        "extended_projections": False,
        "projection_method": "new",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Ohne SegmentCount (falls das für die schlechteren Ergebnisse mit P3 verantwortlich ist)
    11: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    12: {
        "extended_projections": False,
        "projection_method": "new",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Purer Test mit P2
    13: {
        "extended_projections": True,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Trimmed Test mit P2 (nur Features die extended unterstützen)
    14: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [RouteBearingChange, Side, RouteStreets]
    },
    15: {
        "extended_projections": True,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [RouteBearingChange, Side, RouteStreets]
    },
    # Trimmed Test mit P3 (nur Features die extended unterstützen)
    16: {
        "extended_projections": False,
        "projection_method": "new",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [RouteBearingChange, Side, RouteStreets]
    },


    # --------------- EVALUATION: Features ---------------
    # Feature Zeitmessung
    17: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Collinear problem test
    18: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        # 1 und 5 raus, damit das nicht auftritt: "UserWarning: Variables are collinear" (nur für isolierte BearingDiffs Nutzung wirksam)
        BearingDiffs: [0, 2, 3, 4, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs]
    },
    # Alle Features getestet (Ausgangssituation)
    19: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Neue Transformation (bei train_all)
    1903: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Zählen der Duplikate gefixt
    1904: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Zählen der Duplikate gefixt
    1905: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": True,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # test des neuen lsa lane type features
    1902: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Entfernung stark korrelierender Features
    # 10 - Stärksten Korrelationen (absteigend):
    # [('RS8', 'RS4'), ('RS8', 'RS7'), ('RS8', 'RS1'), ('RS6', 'RS2'), ('RS4', 'RS1'), ('RS4', 'RS3'), ('RS4', 'RS2'), ('RS6', 'RS1'), ('RS8', 'RS2'), ('RS6', 'RS4')]
    # ? ('RS8', 'RS4'), ('RS8', 'RS7'), ('RS8', 'RS1'), ('RS6', 'RS2'), ('RS4', 'RS1'), ('RS4', 'RS2'), ('RS4', 'RS3'), ('RS6', 'RS1'), ('RS8', 'RS2'), ('RS6', 'RS4'),
    # --> RS4,              RS7,                RS1,        RS6,                                                                            RS2 entfernen
    20: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Entfernung stark korrelierender Features
    # 20 - Stärksten Korrelationen (absteigend, nur die nach den ersten 10 aufgelistet, Rest steht eine config drüber):
    # [..., ('SM', 'RR'), ('RS7', 'RS4'), ('RS8', 'RS3'), ('LU5', 'LU3'), ('RS7', 'RS3'), ('RS3', 'RS1'), ('RS7', 'RS1'), ('PE5', 'PE3'), ('RS3', 'RS2'), ('RS6', 'RS3')]
    # ?  ('SM', 'RR'), ('RS7', 'RS4'), ('RS8', 'RS3'), ('LU5', 'LU3'), ('RS7', 'RS1'), ('RS3', 'RS1'), ('RS3', 'RS2'), ('RS7', 'RS3'), ('PE5', 'PE3'), ('RS6', 'RS3'),
    # --> zusätzlich RR,                        RS8,            LU3,                                                            PE3 entfernen
    # --> zusätzlich RR,                        RS8,            LU5,                                                            PE3 entfernen (mit Berücksichtigung der Transinformation)
    21: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Entfernung stark korrelierender Features
    # 30 - Stärksten Korrelationen (absteigend, nur die nach den ersten 10 aufgelistet, Rest steht eine config drüber):
    # [..., ('LU3', 'LU1'), ('LU3', 'LU2'), ('RS7', 'RS2'), ('LU4', 'LU2'), ('RS8', 'RS6'), ('LU5', 'LU1'), ('PE5', 'PE1'), ('RS2', 'RS1'), ('PE5', 'PE2'), ('LU4', 'LU1')]
    # ? ('LU3', 'LU1'), ('RS7', 'RS2'), ('LU3', 'LU2'), ('RS8', 'RS6'), ('LU4', 'LU2'), ('LU5', 'LU1'), ('PE5', 'PE1'), ('PE5', 'PE2'), ('RS2', 'RS1'), ('LU4', 'LU1')
    # --> zusätzlich            LU2,                                                                LU1,        PE1,                              PE2
    # --> zusätzlich LU1,       LU2,                                                                            PE1,                              PE2 (mit Berücksichtigung der Transinformation)
    # !!! Training zu schlecht, deswegen mit Config 21 weiter (doch nicht schlecht mit neuer Methode)
    22: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [3, 4],
        LengthDiffs: [2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Entfernung stark korrelierender Features
    # 40 - Stärksten Korrelationen (absteigend, nur die nach den ersten 10 aufgelistet, Rest steht eine config drüber):
    # [..., ('PE3', 'PE2'), ('LU5', 'LU2'), ('PE3', 'PE1'), ('LU4', 'LU3'), ('RS6', 'RS5'), ('RS7', 'RS6'), ('SM', 'LM'), ('LU4', 'LR'), ('LM', 'RR'), ('LR', 'LM')]
    # -> zusätzlich                                               LU4,                                            LM,
    2200001: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [3, 4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Entfernung stark korrelierender Features
    # 50 - Stärksten Korrelationen (absteigend, nur die nach den ersten 10 aufgelistet, Rest steht eine config drüber):
    # [..., ('RS5', 'RS3'), ('SM', 'RS5'), ('SM', 'LR'), ('LU4', 'RR'), ('E', 'PE4'), ('LR', 'RR'), ('RS5', 'RS2'), ('LU2', 'LU1'), ('PE4', 'PE3'), ('SM', 'LU4')]
    # -> zusätzlich RS5,                        SM                          PE4
    2200002: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Entfernung stark korrelierender Features
    # 70 - Stärksten Korrelationen (absteigend, nur die nach den ersten 10 aufgelistet, Rest steht eine config drüber):
    # [..., ('RS5', 'RS1'), ('RS5', 'RS4'), ('RR', 'RS5'), ('PE4', 'PE2'), ('LU2', 'LR'), ('LR', 'RS5'), ('PE4', 'PE1'), ('SM', 'PE5'), ('LU5', 'LU4'), ('RS8', 'RS5')
    # ('PE5', 'LM'), ('PE5', 'RR'), ('PE2', 'PE1'), ('LM', 'RS5'), ('LU1', 'LR'), ('LU4', 'LM'), ('LU3', 'LR'), ('RS7', 'RS5'), ('E', 'PE3'), ('LU4', 'RS5')]
    # -> zusätzlich                                                                                    LU3
    2200003: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, PointDistances, Distance, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Config 2200002 + Transinformation, Entfernen von unnützen Features
    # Config 2200002 + Entfernen bis AQ (große Lücke), also SW, LM, AQ entfernen
    # Config 2200002 + also zusätzlich entfernt: SW, AQ
    2200004: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Mit neuer Transformation
    220000403: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Config 2200004 + Transinformation, Entfernen von unnützen Features
    # Config 2200004 + Entfernen bis TM (große Lücke), also TM, RR entfernen
    # Config 2200004 + also zusätzlich entfernt: TM
    2200005: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side]
    },
    # Config 21 + Transinformation, Entfernen von unnützen Features
    # Config 21 + Entfernen bis PE4 (große Lücke), also SW, LM, AQ, RR, TM, SM, PE4 entfernen
    # Config 21 + also zusätzlich entfernt: SW, LM, AQ, TM, SM, PE4
    23: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [0, 1, 4],
        LengthDiffs: [0, 1, 2, 3],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side]
    },
    # Transinformation, Entfernen von unnützen Features
    # Entfernen bis PE4 (große Lücke), also SW, LM, AQ, RR, TM, SM, PE4 entfernen
    24: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side]
    },
    # Transinformation, Entfernen von unnützen Features
    # Zusätzlich entfernen bis PE1 (große Lücke), also zusätzlich L,E,LR, PE2, PE1 entfernen
    25: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances]
    },
    # Massive Reduktion für alternativen Klassifikatoren
    26: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs]
    },
    27: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs]
    },
    # Spezialisierung der Features auf Modelle
    # RFE - AdaBoost
    28: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [4, 5, 6],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # RFE - Random Forest
    29: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # RFE - Decision Tree
    30: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [1, 6, 7],
        PointDistances: [2],
        LengthDiffs: [0],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Feature Importances - AdaBoost (bis PE3)
    31: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4, 6],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [1, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, LSALaneType]
    },
    # Feature Importances - Random Forest (bis TM)
    32: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 4],
        LengthDiffs: [0, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Feature Importances - Decision Tree (bis LU4)
    33: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [1, 5, 6, 7],
        PointDistances: [0, 2],
        LengthDiffs: [3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, SegmentCount, Side, LSALaneType]
    },
    # Experiment, nur Bearing Diffs
    34: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 3, 4, 5, 6, 7],
        PointDistances: [0, 2],
        LengthDiffs: [3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs]
    },








    # --------------- EVALUATION: Feature Skalierung ---------------
    # Ausgehend von Config 2200004 - norm
    22000041: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Ausgehend von Config 2200004 - standard
    22000042: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # test des neuen lsa lane type features
    2202000042: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Neue Transformation
    2203000042: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Ausgehend von Config 2200004 - power
    22000043: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [2],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Ausgehend von Config 21 (beste Kombination von Features)
    # Experiment: Normalisierung
    35: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Ausgehend von Config 21 (beste Kombination von Features)
    # Experiment: Standardisierung
    36: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Ausgehend von Config 21 (beste Kombination von Features)
    # Experiment: Power Transformation
    37: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": True,
        },
        BearingDiffs: [2, 4],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Ausgehend von Config 21 (beste Kombination von Features)
    # Experiment: Standardisierung (auf alle Features)
    38: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Ausgehend von Config 21 (beste Kombination von Features)
    # Experiment: Power Transformation (auf alle Features)
    39: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": True,
        },
        BearingDiffs: [2, 4],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Alle Features
    # Experiment: Normalisierung (nur numerische Features)
    40: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Alle Features
    # Experiment: Normalisierung (alle Features)
    41: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Alle Features
    # Experiment: Standardisierung (nur numerische Features)
    42: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Alle Features
    # Experiment: Standardisierung (alle Features)
    43: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Alle Features
    # Experiment: Power Trans (nur numerische Features)
    44: {
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
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Neue Transformation
    4403: {
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
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Alle Features
    # Experiment: Power Trans (alle Features)
    45: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": False,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": False,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": True,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Strategie 1 (Redundanz), WIEDERHOLUNG UNTER ANWENDUNG VON FEATURE TRANSFORMATIONEN
    # Config 22 ursprünglich
    # Anwendung Power Trans
    46: {
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
        LengthDiffs: [2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Config 22 ursprünglich
    # Anwendung Standardisierung
    47: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [3, 4],
        LengthDiffs: [2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Config 22 ursprünglich
    # Anwendung Normalisierung
    48: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [3, 4],
        LengthDiffs: [2, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType, RouteStreets]
    },
    # Strategie 2 (Transinformation), WIEDERHOLUNG UNTER ANWENDUNG VON FEATURE TRANSFORMATIONEN
    # Config 24 ursprünglich
    # Anwendung Normalisierung
    49: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side]
    },
    # Config 24 ursprünglich
    # Anwendung Standardisierung
    50: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side]
    },
    # Config 24 ursprünglich
    # Anwendung Power Transformation
    51: {
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
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side]
    },
    # Config 25 ursprünglich
    # Anwendung Normalisierung
    52: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances]
    },
    # Config 25 ursprünglich
    # Anwendung Standardisierung
    53: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances]
    },
    # Config 25 ursprünglich
    # Anwendung Power Transformation
    54: {
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
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [2, 4],
        LengthDiffs: [0, 1, 2, 3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances]
    },
    # Spezialisierung der Features auf Modelle
    # ursprünglich Config 28, RFE - AdaBoost
    # Anwendung Power Transformation
    55: {
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
        BearingDiffs: [4, 5, 6],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # ursprünglich Config 29, RFE - Random Forest
    # Anwendung Power Transformation
    56: {
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
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 30, RFE - Decision Tree
    # Anwendung Power Transformation
    57: {
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
        BearingDiffs: [1, 6, 7],
        PointDistances: [2],
        LengthDiffs: [0],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 31, Feature Importances - AdaBoost (bis PE3)
    # Anwendung Power Transformation
    58: {
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
        BearingDiffs: [2, 4, 6],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [1, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, LSALaneType]
    },
    # ursprünglich Config 32, Feature Importances - Random Forest (bis TM)
    # Anwendung Power Transformation
    59: {
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
        BearingDiffs: [0, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 4],
        LengthDiffs: [0, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 33, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Power Transformation
    60: {
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
        BearingDiffs: [1, 5, 6, 7],
        PointDistances: [0, 2],
        LengthDiffs: [3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, SegmentCount, Side, LSALaneType]
    },




    # ursprünglich Config 28, RFE - AdaBoost
    # Anwendung Standardisierung
    61: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [4, 5, 6],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # ursprünglich Config 29, RFE - Random Forest
    # Anwendung Standardisierung
    62: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 30, RFE - Decision Tree
    # Anwendung Standardisierung
    63: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [1, 6, 7],
        PointDistances: [2],
        LengthDiffs: [0],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 31, Feature Importances - AdaBoost (bis PE3)
    # Anwendung Standardisierung
    64: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4, 6],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [1, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, LSALaneType]
    },
    # ursprünglich Config 32, Feature Importances - Random Forest (bis TM)
    # Anwendung Standardisierung
    65: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [0, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 4],
        LengthDiffs: [0, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 33, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Standardisierung
    66: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [1, 5, 6, 7],
        PointDistances: [0, 2],
        LengthDiffs: [3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, SegmentCount, Side, LSALaneType]
    },




    # ursprünglich Config 28, RFE - AdaBoost
    # Anwendung Normalisierung
    67: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [4, 5, 6],
        PointDistances: [0, 1, 2, 3, 4],
        LengthDiffs: [0, 1, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # ursprünglich Config 29, RFE - Random Forest
    # Anwendung Normalisierung
    68: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 30, RFE - Decision Tree
    # Anwendung Normalisierung
    69: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [1, 6, 7],
        PointDistances: [2],
        LengthDiffs: [0],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 31, Feature Importances - AdaBoost (bis PE3)
    # Anwendung Normalisierung
    70: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4, 6],
        PointDistances: [0, 1, 2, 4],
        LengthDiffs: [1, 3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, LSALaneType]
    },
    # ursprünglich Config 32, Feature Importances - Random Forest (bis TM)
    # Anwendung Normalisierung
    71: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 2, 3, 4, 5, 6, 7],
        PointDistances: [1, 2, 4],
        LengthDiffs: [0, 3],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 33, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Normalisierung
    72: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [1, 5, 6, 7],
        PointDistances: [0, 2],
        LengthDiffs: [3, 4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, SegmentCount, Side, LSALaneType]
    },



    # WEITERE REDUKTION DER BESTEN KOMBINATIONEN AUS DER DRITTEN STRATEGIE
    # Spezialisierung der Features auf Modelle
    # ursprünglich Config 67, RFE - AdaBoost + Normalisierung
    # Anwendung Normalisierung
    # Reduktion der 20 stärksten Korrelation, also von Config 67 zusätzlich folgende Features entfernt: RR, PE3
    73: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [4, 5, 6],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # ursprünglich Config 55, RFE - AdaBoost + Yeo Power Trans
    # Anwendung Power Transformation
    # Reduktion der 20 stärksten Korrelation, also von Config 55 zusätzlich folgende Features entfernt: RR, PE3
    74: {
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
        BearingDiffs: [4, 5, 6],
        PointDistances: [0, 1, 3, 4],
        LengthDiffs: [0, 1, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # Anwendung Normalisierung
    # Reduktion der 40 stärksten Korrelation, also von Config 73 zusätzlich folgende Features entfernt: LU1, PE1, PE2, // LU2, RS5, RS6, SM
    75: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [6],
        PointDistances: [3, 4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # Anwendung Power Trans
    # Reduktion der 40 stärksten Korrelation, also von Config 74 zusätzlich folgende Features entfernt: LU1, PE1, PE2, // LU2, RS5, RS6, SM
    76: {
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
        BearingDiffs: [6],
        PointDistances: [3, 4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, SegmentCount, Side, StreetCrossings, LSALaneType]
    },
    # Anwendung Normalisierung
    # Reduktion der 50 stärksten Korrelation, also von Config 75 zusätzlich folgende Features entfernt: SM, PE4
    77: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [6],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, StreetCrossings, LSALaneType]
    },
    # Anwendung Standardisierung
    # Reduktion der 50 stärksten Korrelation, also von Config 75 zusätzlich folgende Features entfernt: SM, PE4
    7701: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [6],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, StreetCrossings, LSALaneType]
    },
    # Anwendung Power Trans
    # Reduktion der 50 stärksten Korrelation, also von Config 76 zusätzlich folgende Features entfernt: SM, PE4
    78: {
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
        BearingDiffs: [6],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, StreetCrossings, LSALaneType]
    },
    # Anwendung Power Trans
    # Reduktion der 50 stärksten Korrelation + Transinfo (Entfernen bis AQ), also von Config 78 zusätzlich folgende Features entfernt: AQ
    79: {
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
        BearingDiffs: [6],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Test des neuen lsa lane type feature
    7902: {
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
        BearingDiffs: [6],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Aufsplitten der Transformation (train_all)
    7903: {
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
        BearingDiffs: [6],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Power Trans
    # Reduktion der 50 stärksten Korrelation + Transinfo (Entfernen bis PE4), also von Config 79 zusätzlich folgende Features entfernt: TM
    # zu viel (Ergebnis abfall)
    80: {
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
        BearingDiffs: [6],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side]
    },


    # ursprünglich RFE - Random Forest
    # Anwendung Normalisierung
    # Reduktion der 10 stärksten Korrelation, also von Config 68 zusätzlich folgende Features entfernt: RS4, RS7, RS1, RS6, RS2
    81: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4, 7],
        PointDistances: [1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Standardisierung
    # Reduktion der 10 stärksten Korrelation, also von Config 62 zusätzlich folgende Features entfernt: RS4, RS7, RS1, RS6, RS2
    82: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4, 7],
        PointDistances: [1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Power Transformation
    # Reduktion der 10 stärksten Korrelation, also von Config 56 zusätzlich folgende Features entfernt: RS4, RS7, RS1, RS6, RS2
    83: {
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
        BearingDiffs: [2, 4, 7],
        PointDistances: [1, 2, 3, 4],
        LengthDiffs: [0, 1, 2, 4],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Normalisierung
    # Reduktion der 40 stärksten Korrelation, also von Config 81 zusätzlich folgende Features entfernt: RS8, LU3, PE3, LU1, PE2, LU2, LM
    84: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [3, 4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Standardisierung
    # Reduktion der 40 stärksten Korrelation, also von Config 82 zusätzlich folgende Features entfernt: RS8, LU3, PE3, LU1, PE2, LU2, LM
    85: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [3, 4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Power Transformation
    # Reduktion der 40 stärksten Korrelation, also von Config 83 zusätzlich folgende Features entfernt: RS8, LU3, PE3, LU1, PE2, LU2, LM
    86: {
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
    },
    # Test mit neuer lsa lane type Methode
    8602: {
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
    },
    # Test mit besser Transformation (Training, Test getrennt)
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
    },
    # Test mit optimierter extended projection
    8604: {
        "extended_projections": True,
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
    },
    # Anwendung Power Transformation
    # Reduktion der 40 stärksten Korrelation, also von Config 83 zusätzlich folgende Features entfernt: RS8, LU3, PE3, LU1, PE2, LU2, LM
    # TEST MIT NEUEN PROJEKTIONSMETHODE
    86001: {
        "extended_projections": False,
        "projection_method": "new",
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
    },
    # Anwendung Normalisierung
    # Reduktion der 50 stärksten Korrelation, also von Config 81 zusätzlich folgende Features entfernt: RS8, LU3, PE3, LU1, PE2, LU2, LM, RS5, PE4, RR
    87: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Standardisierung
    # Reduktion der 50 stärksten Korrelation, also von Config 82 zusätzlich folgende Features entfernt: RS8, LU3, PE3, LU1, PE2, LU2, LM, RS5, PE4, RR
    88: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Anwendung Power Transformation
    # Reduktion der 50 stärksten Korrelation, also von Config 83 zusätzlich folgende Features entfernt: RS8, LU3, PE3, LU1, PE2, LU2, LM, RS5, PE4, RR
    89: {
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
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [4],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },





    # ursprünglich Config 69, RFE - Decision Tree
    # Anwendung Normalisierung
    # Reduktion der 10 stärksten Korrelation, also von Config 69 zusätzlich folgende Features entfernt: RS7, RS1
    90: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [0],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 63, RFE - Decision Tree
    # Anwendung Standardisierung
    # Reduktion der 10 stärksten Korrelation, also von Config 63 zusätzlich folgende Features entfernt: RS7, RS1
    91: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [0],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 57, RFE - Decision Tree
    # Anwendung Power Transformation
    # Reduktion der 10 stärksten Korrelation, also von Config 57 zusätzlich folgende Features entfernt: RS7, RS1
    92: {
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
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [0],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, RouteBearingChange, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },




    # ursprünglich Config 71, Feature Importances - Random Forest (bis TM)
    # Anwendung Normalisierung
    # Entfernung der 50 stärksten Korrelationen, also zusätzlich zu Config 71 folgende Features entfernen:
    # RS4, RS7, RS1 // RS8, PE3, RS6 // PE2, LU4 // LM // RS5
    93: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [0],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 65, Feature Importances - Random Forest (bis TM)
    # Anwendung Standardisierung
    # Entfernung der 50 stärksten Korrelationen, also zusätzlich zu Config 65 folgende Features entfernen:
    # RS4, RS7, RS1 // RS8, PE3, RS6 // PE2, LU4 // LM // RS5
    94: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [0],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 59, Feature Importances - Random Forest (bis TM)
    # Anwendung Power Transformation
    # Entfernung der 50 stärksten Korrelationen, also zusätzlich zu Config 59 folgende Features entfernen:
    # RS4, RS7, RS1 // RS8, PE3, RS6 // PE2, LU4 // LM // RS5
    95: {
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
        BearingDiffs: [2],
        PointDistances: [4],
        LengthDiffs: [0],
        Lengths: [1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 71, Feature Importances - Random Forest (bis TM)
    # Anwendung Normalisierung
    # Entfernung der 30 stärksten Korrelationen, also zusätzlich zu Config 71 folgende Features entfernen:
    # RS4, RS7, RS1 // RS8, PE3, RS6 // PE2, LU4
    95001: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [4],
        LengthDiffs: [0],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 65, Feature Importances - Random Forest (bis TM)
    # Anwendung Normalisierung
    # Entfernung der 30 stärksten Korrelationen, also zusätzlich zu Config 65 folgende Features entfernen:
    # RS4, RS7, RS1 // RS8, PE3, RS6 // PE2, LU4
    95002: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [2, 4],
        PointDistances: [4],
        LengthDiffs: [0],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 59, Feature Importances - Random Forest (bis TM)
    # Anwendung Power Transformation
    # Entfernung der 30 stärksten Korrelationen, also zusätzlich zu Config 59 folgende Features entfernen:
    # RS4, RS7, RS1 // RS8, PE3, RS6 // PE2, LU4
    95003: {
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
        PointDistances: [4],
        LengthDiffs: [0],
        Lengths: [0, 1],
        "feature_extractor_combination":  [BearingDiffs, Lengths, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },




    # ursprünglich Config 72, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Normalisierung
    # Entfernung der 50 stärksten Korrelationen, also zusätzlich zu Config 72 folgende Features entfernen:
    # RS7, RS6, RS2 // RR // // PE1 // SM
    96: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 66, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Standardisierung
    # Entfernung der 50 stärksten Korrelationen, also zusätzlich zu Config 66 folgende Features entfernen:
    # RS7, RS6, RS2 // RR // // PE1 // SM
    97: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 60, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Power Transformation
    # Entfernung der 50 stärksten Korrelationen, also zusätzlich zu Config 60 folgende Features entfernen:
    # RS7, RS6, RS2 // RR // // PE1 // SM
    98: {
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
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Test mit neuem lsa lane type feature
    9802: {
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
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # Test mit neue Transformation (getrennt training und test)
    9803: {
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
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, Side, LSALaneType]
    },
    # ursprünglich Config 72, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Normalisierung
    # Entfernung der 40 stärksten Korrelationen, also zusätzlich zu Config 72 folgende Features entfernen:
    # RS7, RS6, RS2 // RR // // PE1
    98001: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, SegmentCount, Side, LSALaneType]
    },
    # ursprünglich Config 60, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Standadisierung
    # Entfernung der 40 stärksten Korrelationen, also zusätzlich zu Config 60 folgende Features entfernen:
    # RS7, RS6, RS2 // RR // // PE1
    98002: {
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
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, SegmentCount, Side, LSALaneType]
    },
    # ursprünglich Config 60, Feature Importances - Decision Tree (bis LU4)
    # Anwendung Power Transformation
    # Entfernung der 40 stärksten Korrelationen, also zusätzlich zu Config 60 folgende Features entfernen:
    # RS7, RS6, RS2 // RR // // PE1
    98003: {
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
        BearingDiffs: [7],
        PointDistances: [2],
        LengthDiffs: [3, 4],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs, LengthDiffs, PointDistances, Distance, SegmentCount, Side, LSALaneType]
    },




    # TSFRESH TEST
    99: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": True,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": True,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [],
        PointDistances: [],
        LengthDiffs: [],
        Lengths: [],
        "feature_extractor_combination":  []
    },
    # TSFRESH TEST Normalisierung
    100: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": True,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": True,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [],
        PointDistances: [],
        LengthDiffs: [],
        Lengths: [],
        "feature_extractor_combination":  []
    },
    # TSFRESH TEST Standardisierung
    101: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": True,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": True,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": True,
            "power_transformation": False,
        },
        BearingDiffs: [],
        PointDistances: [],
        LengthDiffs: [],
        Lengths: [],
        "feature_extractor_combination":  []
    },
    # TSFRESH TEST Power Transformation
    102: {
        "extended_projections": False,
        "projection_method": "old",
        "data_augmentation": False,
        "with_duplicates": True,
        "meta_last_bindings_data_update": {
            "commit": "85cccfe6aec5b9c918f3d1d182bf2410869c23d9",
            "datetime": "2022-08-23 5:44pm"
        },
        "tsfresh_features": True,
        "feature_transformation_only_numerical": False,
        "feature_transformation": {
            "normalization": False,
            "standardization": False,
            "power_transformation": True,
        },
        BearingDiffs: [],
        PointDistances: [],
        LengthDiffs: [],
        Lengths: [],
        "feature_extractor_combination":  []
    },




    # Cluster Test Normalisierung
    103: {
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
            "normalization": True,
            "standardization": False,
            "power_transformation": False,
        },
        BearingDiffs: [0, 1, 2, 3, 4, 5, 6, 7],
        PointDistances: [],
        LengthDiffs: [],
        Lengths: [],
        "feature_extractor_combination":  [BearingDiffs]
    },
}
