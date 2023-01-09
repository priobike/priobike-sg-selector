import gzip
import json
import os
from itertools import chain
import numpy as np
import pandas as pd
from composer.models import Route, RouteLSABinding
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from routing.matching import get_matches
from routing.matching.ml.features import get_features
from routing.matching.proximity import ProximityMatcher
from ml_evaluation.utils import get_feature_names
from tqdm import tqdm
from tsfresh import extract_relevant_features

from ml_evaluation.configs.datasets import config_data_and_features


def remove_duplicates(X, y, constellations, route_errors, dataset_logs):
    unique_count = 0
    removed_count = 0
    unique_datapoints = []
    unique_labels = []
    unique_constellations = []
    unique_route_errors = []
    for index, datapoint in enumerate(tqdm(X, desc="Removing duplicates")):
        datapoint_list = datapoint.tolist()
        if datapoint_list not in unique_datapoints:
            unique_datapoints.append(datapoint_list)
            unique_labels.append(int(y[index]))
            unique_constellations.append(constellations[index])
            unique_route_errors.append(route_errors[index])
            unique_count += 1
        else:
            removed_count += 1

    X = unique_datapoints
    y = unique_labels
    constellations = unique_constellations
    route_errors = unique_route_errors

    dataset_logs["duplicate_statistics"] = {
        "unique_count": unique_count,
        "removed_count": removed_count
    }

    return X, y, constellations, route_errors, dataset_logs


def process_route(route, config):
    bindings = RouteLSABinding.objects \
        .filter(route=route) \
        .select_related("lsa")

    all_lsas = get_matches(
        route.geometry, [ProximityMatcher(search_radius_m=20)])
    selected_lsas = list(b.lsa for b in bindings)
    selected_lsas_constellations = list(
        b.corresponding_constellation.name for b in bindings)
    selected_lsas_route_errors = list(
        b.corresponding_route_error.name if b.corresponding_route_error is not None else "NO_ERROR" for b in bindings)
    nonselected_lsas = [x for x in list(all_lsas) if x not in selected_lsas]

    # Count how many projected linestrings have duplicate coordinates
    projection_duplicates = 0
    projection_no_duplicates = 0

    # Count how many original linestrings (map topologies) have duplicate coordinates
    original_map_topology_duplicates = 0
    original_map_topology_no_duplicates = 0

    total_feature_timings = []
    total_normal_projection_timings = []
    total_extended_projection_timings = []

    X, y, constellations, route_errors = [], [], [], []
    for index, lsa in enumerate(selected_lsas):
        features, projection_duplicate, original_map_topology_duplicate, feature_timings, normal_projection_timings, extended_projection_timings = get_features(
            lsa, route.geometry, config)

        if projection_duplicate:
            projection_duplicates += 1
        else:
            projection_no_duplicates += 1

        if original_map_topology_duplicate:
            original_map_topology_duplicates += 1
        else:
            original_map_topology_no_duplicates += 1

        total_feature_timings.append(feature_timings)
        total_normal_projection_timings.append(normal_projection_timings)
        total_extended_projection_timings.append(extended_projection_timings)
        X.append(features)
        y.append(1)  # 1 = selected
        constellations.append(selected_lsas_constellations[index])
        route_errors.append(selected_lsas_route_errors[index])
    for lsa in nonselected_lsas:
        features, projection_duplicate, original_map_topology_duplicate, feature_timings, normal_projection_timings, extended_projection_timings = get_features(
            lsa, route.geometry, config)

        if projection_duplicate:
            projection_duplicates += 1
        else:
            projection_no_duplicates += 1

        if original_map_topology_duplicate:
            original_map_topology_duplicates += 1
        else:
            original_map_topology_no_duplicates += 1

        total_feature_timings.append(feature_timings)
        total_normal_projection_timings.append(normal_projection_timings)
        total_extended_projection_timings.append(extended_projection_timings)
        X.append(features)
        y.append(0)  # 0 = not selected
        constellations.append("NOT_SELECTED")
        route_errors.append("NOT_SELECTED")

    return X, y, constellations, route_errors, projection_duplicates, projection_no_duplicates, original_map_topology_duplicates, original_map_topology_no_duplicates,\
        total_feature_timings, total_normal_projection_timings, total_extended_projection_timings


class Command(BaseCommand):
    logs_path = "ml_evaluation/logs/dataset_with_features/"
    log_file_prefix = "logs_generate_dataset_config_feature_and_data_id_"
    data_file_path_and_prefix = "../backend/ml_evaluation/datasets/dataset_data_and_features_config_id_"

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('config_id', type=int)

    def handle(self, *args, **options):

        # Check if the path argument is valid
        if not options["config_id"]:
            raise Exception(
                "Please specify a config_id to specify which features should be extracted.")

        config_id = options["config_id"]

        unique_bindings_from_route_on = 117

        relevant_routes_1 = Route.objects.filter(
            id__range=(0, unique_bindings_from_route_on - 1))

        bindings_dir = "../data/bindings/"
        files = [int(f.replace(".json", "")) for f in os.listdir(
            bindings_dir) if os.path.isfile(os.path.join(bindings_dir, f))]

        relevant_routes_2_ids = [
            id for id in files if id >= unique_bindings_from_route_on]

        relevant_routes_2 = Route.objects.filter(id__in=relevant_routes_2_ids)

        print(f"Amount of routes in first part: {len(relevant_routes_1)}")
        print(
            f"Amount of routes in second part (mostly only looked at unique constellations between LSAs and routes): {len(relevant_routes_2)}")

        relevant_routes = list(chain(relevant_routes_1, relevant_routes_2))

        print(f"Total routes: {len(relevant_routes)}")

        dataset_logs = {}

        # Check if the given config id corresponds to a saved configuration
        if config_id not in config_data_and_features:
            raise KeyError('No config for the given config id available.')

        y = []
        X = []
        constellations = []
        route_errors = []
        feature_names = []
        total_feature_timings = []
        total_normal_projection_timings = []
        total_extended_projection_timings = []

        config = config_data_and_features[config_id]

        if config["tsfresh_features"]:
            # tsfresh feature extraction

            df_x = pd.DataFrame(columns=[
                                "id", "point_idx", "mt_lat", "mt_lon", "route_lat", "route_lon", "lat_diff", "lon_dif"])
            df_y = pd.Series(dtype=np.int8)
            for route in tqdm(relevant_routes, desc="Generating dataframe"):
                route_geometry = route.geometry.transform(
                    settings.METRICAL, clone=True)

                bindings = RouteLSABinding.objects \
                    .filter(route=route) \
                    .select_related("lsa")

                all_lsas = list(get_matches(route.geometry, [
                                ProximityMatcher(search_radius_m=20)]))
                selected_lsas = list(b.lsa for b in bindings)
                selected_lsas_constellations = list(
                    b.corresponding_constellation.name for b in bindings)
                selected_lsas_route_errors = list(
                    b.corresponding_route_error.name if b.corresponding_route_error is not None else "NO_ERROR" for b in bindings)

                index = 0
                for lsa in all_lsas:
                    is_match = lsa in selected_lsas
                    lsa_geometry = lsa.geometry.transform(
                        settings.METRICAL, clone=True)
                    augmented_geometries = [lsa_geometry]
                    """ for _ in range(N_AUGMENTED_SAMPLES_PER_SAMPLE):
                        augmented_geometries.append(jiggle_linestring(lsa_geometry)) """

                    for replica_idx, geometry in enumerate(augmented_geometries):
                        _id = f"{route.id}_{lsa.id}_{replica_idx}"

                        for point_idx, lsa_coord in enumerate(geometry.coords):
                            point_on_lsa = Point(
                                *lsa_coord[:2], srid=geometry.srid)
                            point_on_route = route_geometry.interpolate(
                                route_geometry.project(point_on_lsa))

                            df_x.loc[len(df_x)] = [
                                _id,
                                point_idx,
                                point_on_lsa.x,
                                point_on_lsa.y,
                                point_on_route.x,
                                point_on_route.y,
                                point_on_lsa.x - point_on_route.x,
                                point_on_lsa.y - point_on_route.y
                            ]

                        df_y.loc[_id] = int(is_match)

                        if is_match:
                            constellations.append(
                                selected_lsas_constellations[index])
                            route_errors.append(
                                selected_lsas_route_errors[index])
                            index += 1
                        else:
                            constellations.append("NOT_SELECTED")
                            route_errors.append("NOT_SELECTED")

            features: pd.DataFrame = extract_relevant_features(
                timeseries_container=df_x, y=df_y,
                column_id="id", column_sort="point_idx",
                disable_progressbar=False
            )

            # Get the features from the DataFrame column names
            feature_names = features.columns.values.tolist()

            X = features.values
            y = df_y.values

            # Remove duplicates if it was specified in the config
            if not config_data_and_features[config_id]["with_duplicates"]:
                X, y, constellations, route_errors, dataset_logs = remove_duplicates(
                    X, y, constellations, route_errors, dataset_logs)
        else:
            # Manual feature extraction

            all_projection_duplicates = 0
            all_projection_no_duplicates = 0

            all_original_map_topology_duplicates = 0
            all_original_map_topology_no_duplicates = 0

            # Process all routes
            for route in tqdm(relevant_routes, desc="Processing routes"):
                X_, y_, constellations_, route_errors_, projection_duplicates, projection_no_duplicates, original_map_topology_duplicates, original_map_topology_no_duplicates,\
                    feature_timings, normal_projection_timings, extended_projection_timings = process_route(
                        route, config)

                all_projection_duplicates += projection_duplicates
                all_projection_no_duplicates += projection_no_duplicates

                all_original_map_topology_duplicates += original_map_topology_duplicates
                all_original_map_topology_no_duplicates += original_map_topology_no_duplicates

                total_feature_timings.extend(feature_timings)
                total_normal_projection_timings.extend(
                    normal_projection_timings)
                total_extended_projection_timings.extend(
                    extended_projection_timings)

                X.extend(X_)
                y.extend(y_)

                constellations.extend(constellations_)
                route_errors.extend(route_errors_)

            # Remove duplicates if it was specified in the config
            if not config_data_and_features[config_id]["with_duplicates"]:
                X, y, constellations, route_errors, dataset_logs = remove_duplicates(
                    X, y, constellations, route_errors, dataset_logs)

            # Write logs
            X_numpy = np.array(X)
            index = 0
            for extractor in tqdm(config["feature_extractor_combination"], desc="Create statistics"):
                feature_count = 0
                if extractor in config:
                    feature_count = len(config[extractor])
                    features = X_numpy[:, index:index+feature_count]
                    dataset_logs[extractor.get_name_of_file()] = extractor.get_statistics(
                        features, y, config[extractor])
                else:
                    feature_count = len(extractor.FEATURE_NAMES)
                    features = X_numpy[:, index:index+feature_count]
                    dataset_logs[extractor.get_name_of_file(
                    )] = extractor.get_statistics(features, y)
                index += feature_count

            # Gather feature names
            feature_names = get_feature_names(
                config["feature_extractor_combination"], config)

            X = X_numpy.tolist()

            dataset_logs["duplicate_statistics_2"] = {
                "projections_with_duplicate_coordinates": all_projection_duplicates,
                "projections_with_no_duplicate_coorindates": all_projection_no_duplicates,
                "original_map_topologies_with_duplicate_coordinates": all_original_map_topology_duplicates,
                "original_map_topologies_with_no_duplicate_coordinates": all_original_map_topology_no_duplicates
            }

        dataset_logs["amount_of_routes"] = {
            "set_1_not_only_unique_constellations": len(relevant_routes_1),
            "set_2_mostly_only_unique_constellations": len(relevant_routes_2),
            "total_amount_of_routes": len(relevant_routes),
            "total_amount_of_constellations_between_routes_and_LSAs": len(X),
            "total_amount_of_selected_constellations_slash_matched_lsas": int(np.sum(y)),
            "total_amount_of_unselected_constellations_slash_unmatched_lsas": int(len(y) - np.sum(y))
        }

        # Calculate mean, max, min feature timings
        if len(total_feature_timings) > 0:
            dataset_logs["timings"] = {}
            total_feature_timings = np.array(total_feature_timings)

            index = 0
            for extractor in tqdm(config["feature_extractor_combination"], desc="Create feature timing statistics"):
                if extractor in config:
                    for feature in config[extractor]:
                        feature_name = extractor.FEATURE_NAMES[feature]
                        feature_timings = total_feature_timings[:, index]
                        base_timings = [
                            timing.base if timing.base is not None else 9999999 for timing in feature_timings]
                        base_timings = np.array(base_timings)
                        extra_timings = [
                            timing.extra if timing.extra is not None else 9999999 for timing in feature_timings]
                        extra_timings = np.array(extra_timings)
                        dataset_logs["timings"][f"{extractor.get_name_of_file()}_{feature_name}"] = {
                            f"base_timing_mean": float(np.mean(base_timings)),
                            f"base_timing_min": float(np.min(base_timings)),
                            f"base_timing_max": float(np.max(base_timings)),
                            f"extra_timing_mean": float(np.mean(extra_timings)),
                            f"extra_timing_min": float(np.min(extra_timings)),
                            f"extra_timing_max": float(np.max(extra_timings))
                        }
                        index += 1
                else:
                    for feature_name in extractor.FEATURE_NAMES:
                        feature_timings = total_feature_timings[:, index]
                        base_timings = [
                            timing.base if timing.base is not None else 9999999 for timing in feature_timings]
                        base_timings = np.array(base_timings)
                        extra_timings = [
                            timing.extra if timing.extra is not None else 9999999 for timing in feature_timings]
                        extra_timings = np.array(extra_timings)
                        dataset_logs["timings"][f"{extractor.get_name_of_file()}_{feature_name}"] = {
                            f"base_timing_mean": float(np.mean(base_timings)),
                            f"base_timing_min": float(np.min(base_timings)),
                            f"base_timing_max": float(np.max(base_timings)),
                            f"extra_timing_mean": float(np.mean(extra_timings)),
                            f"extra_timing_min": float(np.min(extra_timings)),
                            f"extra_timing_max": float(np.max(extra_timings))
                        }
                        index += 1

        # Save (normal/extended) projection timings
        used_projection_method = config["projection_method"]
        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}projection_timings/timings_projection_{used_projection_method}_normal_method.json"), 'w') as fp:
            json.dump(total_normal_projection_timings, fp, indent=4)
        if config["extended_projections"]:
            with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}projection_timings/timings_projection_extended_method.json"), 'w') as fp:
                json.dump(total_extended_projection_timings, fp, indent=4)

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                return json.JSONEncoder.default(self, obj)

        # Dump the dataset to disk
        dataset_path = os.path.join(
            settings.BASE_DIR, f"{self.data_file_path_and_prefix}{str(config_id)}.json.gz")
        with gzip.open(dataset_path, "wb") as f:
            json_data = json.dumps({
                "feature_names": feature_names,
                "X": X, "y": y,  "constellations": constellations, "route_errors": route_errors
            }, cls=NumpyEncoder)
            f.write(json_data.encode("utf-8"))
        print(f"Wrote dataset to {dataset_path}")

        # Save the logs into a file
        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}{self.log_file_prefix}{config_id}.json"), 'w') as fp:
            json.dump(dataset_logs, fp, indent=4)
