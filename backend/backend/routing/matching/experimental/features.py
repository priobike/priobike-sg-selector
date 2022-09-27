import os
import pickle
from typing import List, Tuple

import numpy as np
from django.conf import settings
from django.contrib.gis.geos import LineString
from django.db.models.query import QuerySet
from routing.matching import RouteMatcher
from routing.matching.bearing import calc_bearing_diffs, calc_side
from routing.matching.length import calc_length_diffs
from routing.matching.projection import project_onto_route


def calc_features(linestring: LineString, route: LineString, system=settings.METRICAL) -> List[float]:
    """
    Calculate features from a linestring with regards to the route.
    """
    if len(linestring.coords) < 2:
        raise ValueError("LineString must have at least 2 coordinates")
    
    features = np.array([]).astype(np.float32)

    system_linestring = linestring.transform(system, clone=True)
    system_route = route.transform(system, clone=True)

    projected_linestring = project_onto_route(system_linestring, system_route, system=system)

    # Features related to the bearing of the linestring
    bearing_diffs = calc_bearing_diffs(system_linestring, projected_linestring)
    if bearing_diffs:
        bearing_scale = 360
        features = np.append(features, [
            # Mean bearing diff
            np.mean(bearing_diffs) / bearing_scale,
            # Max bearing diff
            np.max(bearing_diffs) / bearing_scale, 
            # Min bearing diff
            np.min(bearing_diffs) / bearing_scale,
            # Last bearing diff
            bearing_diffs[-1] / bearing_scale,
            # First bearing diff
            bearing_diffs[0] / bearing_scale,
        ])
    else:
        features = np.append(features, [0.0, 0.0, 0.0, 0.0, 0.0])

    # Features related to the length of the linestring
    length_diffs = calc_length_diffs(system_linestring, projected_linestring, system=system)
    if length_diffs:
        features = np.append(features, [
            # Mean length diff
            np.mean(length_diffs),
            # Max length diff
            np.max(length_diffs),
            # Min length diff
            np.min(length_diffs),
            # Last length diff
            length_diffs[-1],
            # First length diff
            length_diffs[0],
        ])
    else:
        features = np.append(features, [0.0, 0.0, 0.0, 0.0, 0.0])

    # Other features
    features = np.append(features, [
        # Feature denoting the side of the route the linestring is on
        0 if calc_side(system_linestring, projected_linestring) == "left" else 1,
        # Feature denoting the number of segments
        len(projected_linestring.coords) - 1,
        # Features denoting the length of the linestrings
        system_linestring.length,
        projected_linestring.length,
        # Distance of the linestring from the route
        system_linestring.distance(system_route),        
    ])    

    return features


class ModelMatcher(RouteMatcher):
    """
    An elementwise matcher using a ML model.
    """

    model_path = os.path.join(settings.BASE_DIR, 'config/model.joblib')

    @classmethod
    def store(cls, clf):
        with open(cls.model_path, 'wb') as f:
            pickle.dump(clf, f)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(self.model_path, 'rb') as f:
            self.clf = pickle.load(f)

    def matches(self, sgs: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        """
        Return the SGs that match the route, as a queryset.
        """
        sgs, route = super().matches(sgs, route)

        X = np.array([calc_features(sg.geometry, route) for sg in sgs])
        y = self.clf.predict(X)
        pks_to_include = [sg.pk for sg, prediction in zip(sgs, y) if prediction]

        return sgs.filter(pk__in=pks_to_include), route
