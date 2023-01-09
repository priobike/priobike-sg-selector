import time
from typing import List

import numpy as np
from django.conf import settings
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from django.contrib.gis.measure import D

from ml_evaluation.utils_meta import get_filename

from routing.models import PlanetOsmLine


class StreetCrossings(FeatureExtractor):
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
        Initialize the street crossings feature extractor.
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
                "number_of_crossed_streets_by_map_topology_mean": np.mean(features_binding_selected[:, 0]),
                "number_of_crossed_streets_by_map_topology_max": np.max(features_binding_selected[:, 0]),
                "number_of_crossed_streets_by_map_topology_min": np.min(features_binding_selected[:, 0]),
                "number_of_crossed_streets_by_map_topology_standard_deviation": np.std(features_binding_selected[:, 0]),
            },
            "binding_not_selected": {
                "number_of_crossed_streets_by_map_topology_mean": np.mean(features_binding_not_selected[:, 0]),
                "number_of_crossed_streets_by_map_topology_max": np.max(features_binding_not_selected[:, 0]),
                "number_of_crossed_streets_by_map_topology_min": np.min(features_binding_not_selected[:, 0]),
                "number_of_crossed_streets_by_map_topology_standard_deviation": np.std(features_binding_not_selected[:, 0]),
            }
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()

        lsa_linestring_osm_System = featureExtractionState.lsa_system_linestring.transform(
            settings.METRICAL, clone=True)

        # Highway field described here: https://wiki.openstreetmap.org/wiki/Key:highway
        relevant_streets = PlanetOsmLine.objects.filter(way__dwithin=(lsa_linestring_osm_System, D(m=14)),
                                                        highway__in=('trunk',
                                                                     'primary',
                                                                     'secondary',
                                                                     'tertiary',
                                                                     'unclassified',
                                                                     'residential',
                                                                     'trunk_link',
                                                                     'motorway_link',
                                                                     'primary_link',
                                                                     'secondary_link',
                                                                     'tertiary_link',
                                                                     'living_street',
                                                                     'track',
                                                                     'road',
                                                                     'busway'))

        crossings = 0
        for relevant_street in relevant_streets:
            if relevant_street.way.crosses(lsa_linestring_osm_System):
                crossings += 1

        # print(f'Route-ID: {route.id}, LSA-ID: {lsa.id}, Crossings: {crossings}')

        # Feature denoting how many streets the MAP topology is crossing
        # 0 = 0 crossings, 1 = 1 crossing, 2 = 2 crossings ...
        featureExtractionState.features = np.append(
            featureExtractionState.features, [crossings])

        end = time.time()
        featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
            Timing(base=end - start, extra=None)
        ])
        return featureExtractionState
