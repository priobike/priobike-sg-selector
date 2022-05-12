import gzip
import json
import os

import numpy as np
from composer.models import Route, RouteLSABinding
from django.conf import settings
from django.core.management.base import BaseCommand
from routing.matching import get_matches
from routing.matching.experimental.features import calc_features
from routing.matching.proximity import ProximityMatcher
from tqdm import tqdm


def process_route(route):
    bindings = RouteLSABinding.objects \
        .filter(route=route) \
        .select_related("lsa")

    all_lsas = get_matches(route.geometry, [ProximityMatcher(search_radius_m=15)])
    selected_lsas = set(b.lsa for b in bindings)
    nonselected_lsas = set(all_lsas) - selected_lsas

    X, y = [], []
    for lsa in selected_lsas:
        X.append(calc_features(lsa.geometry, route.geometry))
        y.append(1) # 1 = selected
    for lsa in nonselected_lsas:
        X.append(calc_features(lsa.geometry, route.geometry))
        y.append(0) # 0 = not selected

    return X, y


class Command(BaseCommand):
    def handle(self, *args, **options):
        routes_with_bindings = Route.objects \
            .filter(bound_lsas__isnull=False) \
            .distinct()

        y = []
        X = []

        # Process all routes
        for route in tqdm(routes_with_bindings, desc="Processing routes"):
            X_, y_ = process_route(route)
            X.extend(X_)
            y.extend(y_)       

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return json.JSONEncoder.default(self, obj)

        # Dump the dataset to disk
        dataset_path = os.path.join(settings.BASE_DIR, "../data/ml-dataset.json.gz")
        with gzip.open(dataset_path, "wb") as f:
            json_data = json.dumps({
                "X": X, "y": y, 
            }, cls=NumpyEncoder)
            f.write(json_data.encode("utf-8"))
        print(f"Wrote dataset to {dataset_path}")
