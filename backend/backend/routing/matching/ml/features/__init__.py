from typing import List
import time
from routing.matching.ml.features.types import Timing
from composer.models import Route

import numpy as np
from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from routing.matching.projection import project_onto_route, project_onto_route_new, get_extended_projected_linestring
from routing.matching.ml.utils import remove_duplicate_coordinates
from routing.models import LSA

class FeatureExtractionState:
    def __init__(
        self,
        features: List[float],
        lsa: LSA,
        lsa_system_linestring: LineString,
        lsa_projected_linestring: LineString,
        lsa_extended_projected_linestring: LineString,
        route: Route,
        route_system_linestring: LineString,
        config: map,
        feature_timing_sums: List[Timing],
        *args,
        **kwargs
    ):
        """
        Initialize the feature state object.
        """
        self.features = features
        self.lsa = lsa
        self.lsa_system_linestring = lsa_system_linestring
        self.lsa_projected_linestring = lsa_projected_linestring
        self.lsa_extended_projected_linestring = lsa_extended_projected_linestring
        self.route = route
        self.route_system_linestring = route_system_linestring
        self.config = config
        self.feature_timing_sums = feature_timing_sums

class FeatureExtractor:
    def __init__(self, *args, **kwargs):
        """
        Initialize the feature extractor.
        """    
    
    def extract(self):
        """
        Extract specific feature of the binding
        
        Returns:
            FeatureExtractionState: The FeatureExtractionState with the new features
        """

    @staticmethod
    def get_name_of_file():
        """Gets the name of the feature extractor .py-file.

        Returns:
            string: The name of the feature extractor file
        """

    @staticmethod
    def get_statistics():
        """Gets the statistics of some given features.

        Returns:
            dict: An object with all the statistics for the features.
        """

def get_features(lsa: LSA, route_linestring: LineString, config):
    """
    Extract features from a LSA with regards to the route.
    """

    # Important for length features! For bearing LONLAT is better and the transformation
    # into the LONLAT system happens in the respective feature extractors
    system = settings.METRICAL

    lsa_linestring = lsa.geometry

    if len(lsa_linestring.coords) < 2:
        raise ValueError("LSA LineString must have at least 2 coordinates")
    if len(route_linestring.coords) < 2:
        raise ValueError("Route LineString must have at least 2 coordinates")

    system_lsa_linestring = lsa_linestring.transform(system, clone=True)
    system_route_linestring = route_linestring.transform(system, clone=True)

    # Analyse how many MAP-Topologies have duplicate coordinates
    map_topology_duplicate_coordinates = False
    for coordinate in system_lsa_linestring.coords:
        count = 0
        for coordinate2 in system_lsa_linestring.coords:
            if coordinate == coordinate2:
                count += 1
                if count > 2:
                    # Used for Debugging:
                    """ print(f"M.T. Duplicates: Route: {route.id}, LSA: {lsa.id}") """
                    map_topology_duplicate_coordinates = True
                    break
        if map_topology_duplicate_coordinates:
            break

    # If duplicates were found remove them
    if map_topology_duplicate_coordinates:
        system_lsa_linestring = remove_duplicate_coordinates(
            system_lsa_linestring)

    # Error check whether after removing duplicate coordinates there are still duplicate coordinates
    for coordinate in system_lsa_linestring.coords:
        count = 0
        for coordinate2 in system_lsa_linestring.coords:
            if coordinate == coordinate2:
                count += 1
                if count > 2:
                    raise Exception(
                        f"Error! Still duplicates in LSA after removing duplicates: {lsa.id} (eg in route {route.id})")

    # For analyzing the timings of the diffeernt projection methods:
    normal_projection_start = time.time()

    projected_lsa_linestring = None
    if config["projection_method"] == "new":
        projected_lsa_linestring, system_lsa_linestring = project_onto_route_new(
            system_lsa_linestring, system_route_linestring)
    elif config["projection_method"] == "old":
        projected_lsa_linestring = project_onto_route(
            system_lsa_linestring, system_route_linestring)
        """ if not projected_lsa_linestring.equals_exact(projected_lsa_linestring_test, tolerance=0.00000001):
            print(f"-------------------------------------------------------1.1------Route-{route.id}-LSA-{lsa.id}-------------------------------------------------")
            print(projected_lsa_linestring)
            print(projected_lsa_linestring_test)
        if not system_lsa_linestring.equals_exact(system_lsa_linestring_test, tolerance=0.00000001):
            print(f"-------------------------------------------------------2.2---Route-{route.id}-LSA-{lsa.id}-------------------------------------------------")
            print(system_lsa_linestring)
            print(system_lsa_linestring_test) """

    normal_projection_end = time.time()

    extended_projection_start = time.time()

    extended_projected_linestring = None
    if config["extended_projections"]:
        extended_projected_linestring = get_extended_projected_linestring(
            system_lsa_linestring, system_route_linestring)

    extended_projection_end = time.time()

    timing_normal_projection = normal_projection_end - normal_projection_start
    timing_extended_projection = extended_projection_end - extended_projection_start

    # Analayze how many with the old method projected linestrings have duplicated coordinates
    duplicate_projected_coordinates = False
    for coordinate in projected_lsa_linestring.coords:
        count = 0
        for coordinate2 in projected_lsa_linestring.coords:
            if coordinate == coordinate2:
                count += 1
                if count > 2:
                    # Used for Debugging:
                    """ print(f"Projected Duplicates: Route: {route.id}, LSA: {lsa.id}") """
                    duplicate_projected_coordinates = True
                    break
        if duplicate_projected_coordinates:
            break

    features = np.array([]).astype(np.float32)
    feature_timing_sums = []

    featureExtractionState = FeatureExtractionState(
        features=features,
        lsa=lsa,
        lsa_system_linestring=system_lsa_linestring,
        lsa_projected_linestring=projected_lsa_linestring,
        lsa_extended_projected_linestring=extended_projected_linestring,
        route=None,
        route_system_linestring=system_route_linestring,
        config=config,
        feature_timing_sums=feature_timing_sums
    )

    for extractor in config["feature_extractor_combination"]:
        featureExtractionState = extractor().extract(featureExtractionState)
    return featureExtractionState.features, duplicate_projected_coordinates, map_topology_duplicate_coordinates, featureExtractionState.feature_timing_sums, timing_normal_projection, timing_extended_projection
