import time
from typing import List
import numpy as np
from django.contrib.gis.geos.linestring import LineString, Point
from routing.matching.ml.features.types import FeatureType, Timing
from routing.matching.ml.features import FeatureExtractor, FeatureExtractionState
from routing.matching.bearing import calc_bearing_diffs
from ml_evaluation.utils_meta import get_filename


class RouteBearingChange(FeatureExtractor):
    FEATURE_NAMES = [
        "_"
    ]

    FEATURE_TYPES = [
        FeatureType.NUMERICAL,
    ]

    FEATURE_TYPES_DC = [
        FeatureType.CONTINUOUS,
    ]

    SUPPORTS_EXTENDED_PROJECTION = True

    def __init__(self, *args, **kwargs):
        """
        Initialize the route bearing change feature extractor.
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
                "bearing_change_mean": np.mean(features_binding_selected[:, 0]),
                "bearing_change_max": np.max(features_binding_selected[:, 0]),
                "bearing_change_min": np.min(features_binding_selected[:, 0]),
                "bearing_change_standard_deviation": np.std(features_binding_selected[:, 0]),
            },
            "binding_not_selected": {
                "bearing_change_mean": np.mean(features_binding_not_selected[:, 0]),
                "bearing_change_max": np.max(features_binding_not_selected[:, 0]),
                "bearing_change_min": np.min(features_binding_not_selected[:, 0]),
                "bearing_change_standard_deviation": np.std(features_binding_not_selected[:, 0]),
            }
        }
        return statistic

    def extract(self, featureExtractionState: FeatureExtractionState) -> FeatureExtractionState:
        start = time.time()

        lsa_projected_linestring = featureExtractionState.lsa_projected_linestring if not featureExtractionState.config["extended_projections"]\
            else featureExtractionState.lsa_extended_projected_linestring

        system_srid = lsa_projected_linestring.srid

        point_1 = Point(
            lsa_projected_linestring.coords[0][0], lsa_projected_linestring.coords[0][1], srid=system_srid)
        point_2 = Point(
            lsa_projected_linestring.coords[1][0], lsa_projected_linestring.coords[1][1], srid=system_srid)

        first_segment = LineString([point_1, point_2], srid=system_srid)

        number_of_coords = len(lsa_projected_linestring.coords)

        point_3 = Point(lsa_projected_linestring.coords[number_of_coords - 2][0],
                        lsa_projected_linestring.coords[number_of_coords - 2][1], srid=system_srid)
        point_4 = Point(lsa_projected_linestring.coords[number_of_coords - 1][0],
                        lsa_projected_linestring.coords[number_of_coords - 1][1], srid=system_srid)

        last_segment = LineString([point_3, point_4], srid=system_srid)

        bearing_diff = calc_bearing_diffs(first_segment, last_segment)

        # DEBUGGING:
        """ if bearing_diff[0] == 352.32827173980473:
            print(f'LSA ID: {lsa.id}; Route ID: {route.id}')
            print(serialize("geojson", list([LSA(id=lsa.id, geometry=first_segment)]), geometry_field="geometry"))
            print(serialize("geojson", list([LSA(id=lsa.id, geometry=last_segment)]), geometry_field="geometry"))
            print(serialize("geojson", list([LSA(id=lsa.id, geometry=lsa_projected_linestring)]), geometry_field="geometry"))
            print(bearing_diff)
            print("\n") """

        # bearing difference between first and last segment of projected lsa linestring
        featureExtractionState.features = np.append(
            featureExtractionState.features, [bearing_diff[0]])

        end = time.time()
        featureExtractionState.feature_timing_sums = np.append(featureExtractionState.feature_timing_sums, [
            Timing(base=end - start, extra=None)
        ])

        return featureExtractionState
