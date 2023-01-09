import gzip
import json
import os
import csv
import json
import random
from routing.matching.ml.features.types import FeatureType
from routing.matching.ml.features.feature_length_diffs import LengthDiffs
from routing.matching.ml.features.feature_lengths import Lengths
from routing.matching.ml.features.feature_point_distances import PointDistances
from routing.matching.ml.features.feature_bearing_diffs import BearingDiffs
import numpy as np
from django.core.management.base import BaseCommand
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split, StratifiedKFold, StratifiedShuffleSplit
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler, StandardScaler, PowerTransformer
from django.conf import settings
from ml_evaluation.configs.classifiers import classifiers
from ml_evaluation.configs.trainings import config_train
from ml_evaluation.configs.datasets import config_data_and_features
from routing.matching.ml.matcher import MLMatcher
from ml_evaluation.utils import generate_feature_transformer
from composer.models import Constellation, RouteError

class Command(BaseCommand):

    logs_path = "ml_evaluation/logs/training/"
    
    def get_jiggle_feature(self, value, factor):
        return random.uniform(value-(value*factor), value+(value*factor))
    
    def get_jiggled_data_point(self, data_point, factor, numerical_features_indices):
        for index, feature in enumerate(data_point):
            if index in numerical_features_indices:
                data_point[index] = self.get_jiggle_feature(feature, factor)
                
        return data_point
    
    def augment(self, X, y, constellations, route_errors, data_and_features_config):
        factor = 0.0001
        duplicate_amount = 3
        only_selected_topologies = True
        only_specific_constellation = True
        
        # Gather all numerical features indices
        numerical_features_indices = []
        index = 0
        for extractor in data_and_features_config["feature_extractor_combination"]:
            features_types = None
            if extractor == BearingDiffs:
                features_types = [extractor.FEATURE_TYPES[i] for i in data_and_features_config[BearingDiffs]]
            if extractor == LengthDiffs:
                features_types = [extractor.FEATURE_TYPES[i] for i in data_and_features_config[LengthDiffs]]
            if extractor == Lengths:
                features_types = [extractor.FEATURE_TYPES[i] for i in data_and_features_config[Lengths]]
            if extractor == PointDistances:
                features_types = [extractor.FEATURE_TYPES[i] for i in data_and_features_config[PointDistances]]
            if features_types is None:
                features_types = extractor.FEATURE_TYPES
            for feature_type in features_types:
                if feature_type == FeatureType.NUMERICAL:
                    numerical_features_indices.append(index)
                index += 1
        
        for index, value in enumerate(X):
            if (not only_selected_topologies or y[index] == 1) and (not only_specific_constellation or self.get_constellation_custom_id(constellations[index]).startswith("2")):
                for i in range(duplicate_amount):
                    X = np.insert(arr=X, obj=index, values=self.get_jiggled_data_point(value, factor, numerical_features_indices), axis=0)
                    y = np.insert(arr=y, obj=index, values=y[index], axis=0)
                    constellations = np.insert(arr=constellations, obj=index, values=constellations[index], axis=0)
                    route_errors = np.insert(arr=route_errors, obj=index, values=route_errors[index], axis=0)
                    
        return X, y, constellations, route_errors
    
    def get_constellation_custom_id(self, name):
        return Constellation.objects.filter(name=name).first().custom_id if name != "NOT_SELECTED" else name
    
    def get_router_error_custom_id(self, name):
        return RouteError.objects.filter(name=name).first().custom_id if name != "NOT_SELECTED" and name != "NO_ERROR" else name
    
    def get_average_meta_ratio(self, all_meta_logs, meta_name, example_model_name):
        # meta_name: trainConstellationsRatios or testConstellationsRatios or trainRouteErrorsRatios or testRouteErrorsRatios
        all_ratios = {
            name: np.mean(np.array([
                model_logs[meta_name][name] for model_name, model_logs in all_meta_logs.items()
            ])) for name in all_meta_logs[example_model_name][meta_name]
        }
        return all_ratios
    
    def update_meta_data(self, already_included, meta_data_true_or_false, meta_data_item):
        if not already_included:
            meta_data_true_or_false[meta_data_item] = 1
        else:
            meta_data_true_or_false[meta_data_item] = meta_data_true_or_false[meta_data_item] + 1
        return meta_data_true_or_false
    
    def get_meta_statistics(self, labels, predicted_labels, meta_data_1, meta_data_2, meta_data_1_true, meta_data_1_false, meta_data_2_true, meta_data_2_false):
        for index, (label, predicted_label) in enumerate(zip(labels, predicted_labels)):
            if label == predicted_label:
                meta_data_1_true = self.update_meta_data(meta_data_1[index] in meta_data_1_true, meta_data_1_true, meta_data_1[index])
                meta_data_2_true = self.update_meta_data(meta_data_2[index] in meta_data_2_true, meta_data_2_true, meta_data_2[index])
            else:
                meta_data_1_false = self.update_meta_data(meta_data_1[index] in meta_data_1_false, meta_data_1_false, meta_data_1[index])
                meta_data_2_false = self.update_meta_data(meta_data_2[index] in meta_data_2_false, meta_data_2_false, meta_data_2[index])
        return meta_data_1_true, meta_data_1_false, meta_data_2_true, meta_data_2_false
    
    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('config_train_id', type=int)
    
    def handle(self, *args, **options):
        # Check if the path argument is valid
        if not options["config_train_id"]:
            raise Exception("Please specify a config_train_id to specify which features should be extracted.")
        
        config_train_id = options["config_train_id"]
        
        if config_train_id not in config_train:
            raise KeyError('No config for the given config id available.')
        
        config_data_and_features_id = config_train[config_train_id]["config_data_and_features"]
        
        dataset_path = os.path.join(settings.BASE_DIR, f"../backend/ml_evaluation/datasets/dataset_data_and_features_config_id_{str(config_data_and_features_id)}.json.gz")
        with gzip.open(dataset_path) as f:
            byte_array = f.read()
            dataset = json.loads(byte_array.decode("utf-8"))

        y = dataset["y"]
        X = dataset["X"]
        constellations = dataset["constellations"]
        route_errors = dataset["route_errors"]

        # Since we augmented the dataset with artificial samples, we need to
        # use a non-shuffled train test split
        random_state = 123            
        """ X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, shuffle=config_train[config_train_id]["shuffle"], random_state=random_state)
        
        # Used for analysis:
        constellations_train, constellations_test, route_errors_train, route_errors_test = train_test_split(constellations, route_errors, test_size=0.25, shuffle=config_train[config_train_id]["shuffle"], random_state=random_state)
        
        if config_train[config_train_id]["undersample"]:
            # Undersample the majority class to balance the dataset
            X_train, y_train = RandomUnderSampler().fit_resample(X_train, y_train)

        print(f"Train dataset size: {np.bincount(y_train)}")
        print(f"Test dataset size: {np.bincount(y_test)}") """

        best_f1 = 0
        best_model = None
        best_model_name = None
        
        logs_json = {}
        logs_csv = []
        
        logs_csv.append(["name", "trainf1", "testf1", "trainacc", "testacc", "tn", "fp", "fn", "tp"])
        
        meta_logs_json = {}

        for name, clf in classifiers.items():
            # Create StratifiedKFold/StratifiedShuffleSplit object.
            if "ssf" in config_train[config_train_id] and config_train[config_train_id]["ssf"]:
                skf = StratifiedShuffleSplit(n_splits=10, test_size=0.25, random_state=random_state)
            else:
                skf = StratifiedKFold(n_splits=10, shuffle=config_train[config_train_id]["shuffle"], random_state=random_state)
            all_train_f1s, all_test_f1s, all_train_accs, all_test_accs, all_tns, all_fps, all_fns, all_tps = [],[],[],[],[],[],[],[]
            
            constellations_train, constellations_test, route_errors_train, route_errors_test = [],[],[],[]
            x_train_fold, x_test_fold, y_train_fold, y_test_fold = [],[],[],[]
            
            for train_index, test_index in skf.split(X, y):
                x_train_fold, x_test_fold = np.array(X)[train_index], np.array(X)[test_index]
                y_train_fold, y_test_fold = np.array(y)[train_index], np.array(y)[test_index]
                
                # Apply one of the feature scaling techniques if it was specified in the config
                transformer = None
                model_name = None
                if config_data_and_features[config_data_and_features_id]["feature_transformation"]["normalization"]:
                    transformer = MinMaxScaler()
                    model_name = "min_max_scaler"
                elif config_data_and_features[config_data_and_features_id]["feature_transformation"]["standardization"]:
                    transformer = StandardScaler()
                    model_name = "standard_scaler"
                elif config_data_and_features[config_data_and_features_id]["feature_transformation"]["power_transformation"]:
                    transformer = PowerTransformer(method='yeo-johnson')
                    model_name = "yeo_johnson_power_transformer"
                    
                if transformer is not None:
                    X_train_numpy = np.array(x_train_fold)
                    X_test_numpy = np.array(x_test_fold)
                    column_transformer = generate_feature_transformer(features_numpy=X_train_numpy, transformer=transformer,
                                                    data_feature_config=config_data_and_features[config_data_and_features_id],
                                                    config_id=config_data_and_features_id, model_name=model_name)
                    
                    X_train_numpy = column_transformer.transform(X_train_numpy)
                    x_train_fold = X_train_numpy.tolist()
                    X_test_numpy = column_transformer.transform(X_test_numpy)
                    x_test_fold = X_test_numpy.tolist()
                
                constellations_train, constellations_test = np.array(constellations)[train_index], np.array(constellations)[test_index]
                route_errors_train, route_errors_test = np.array(route_errors)[train_index], np.array(route_errors)[test_index]
                
                if "augment" in config_train[config_train_id] and config_train[config_train_id]["augment"]:
                    x_train_fold, y_train_fold, constellations_train, route_errors_train = self.augment(x_train_fold, y_train_fold, constellations_train, route_errors_train,
                                                                                                        config_data_and_features[config_data_and_features_id])
                
                clf.fit(x_train_fold, y_train_fold)
                all_train_f1s.append(f1_score(y_train_fold, clf.predict(x_train_fold)))
                all_test_f1s.append(f1_score(y_test_fold, clf.predict(x_test_fold)))
                all_train_accs.append(clf.score(x_train_fold, y_train_fold))
                all_test_accs.append(clf.score(x_test_fold, y_test_fold))
                tn, fp, fn, tp = confusion_matrix(y_test_fold, clf.predict(x_test_fold)).ravel()
                all_tns.append(tn)
                all_fps.append(fp)
                all_fns.append(fn)
                all_tps.append(tp)
                
            train_f1 = np.mean(np.array(all_train_f1s))
            test_f1 = np.mean(np.array(all_test_f1s))
            train_acc = np.mean(np.array(all_train_accs))
            test_acc = np.mean(np.array(all_test_accs))
            tn = np.mean(np.array(all_tns))
            fp = np.mean(np.array(all_fps))
            fn = np.mean(np.array(all_fns))
            tp = np.mean(np.array(all_tps))
            
            """ clf.fit(X_train, y_train)
            
            train_f1 = f1_score(y_train, clf.predict(X_train))
            test_f1 = f1_score(y_test, clf.predict(X_test))
            train_acc = clf.score(X_train, y_train)
            test_acc = clf.score(X_test, y_test)
            tn, fp, fn, tp = confusion_matrix(y_test, clf.predict(X_test)).ravel() """
            
            train_constellations_right = {}
            train_constellations_false = {}
            test_constellations_right = {}
            test_constellations_false = {}
            train_route_errors_right = {}
            train_route_errors_false = {}
            test_route_errors_right = {}
            test_route_errors_false = {}
            # Compute constellations and route error statistics
            # For train data
            train_constellations_right, train_constellations_false,\
                train_route_errors_right, train_route_errors_false = self.get_meta_statistics(
                    y_train_fold,
                    clf.predict(x_train_fold),
                    constellations_train,
                    route_errors_train,
                    train_constellations_right,
                    train_constellations_false,
                    train_route_errors_right,
                    train_route_errors_false)
            # For test data
            test_constellations_right, test_constellations_false,\
                test_route_errors_right, test_route_errors_false = self.get_meta_statistics(
                    y_test_fold,
                    clf.predict(x_test_fold),
                    constellations_test,
                    route_errors_test,
                    test_constellations_right,
                    test_constellations_false,
                    test_route_errors_right,
                    test_route_errors_false)
                
            meta_logs_json[name] = {
                "trainConstellationsRatios": {
                    f"K{self.get_constellation_custom_id(constellation)}": amount/(amount + train_constellations_false[constellation]) if constellation in train_constellations_false else 1
                    for constellation, amount in train_constellations_right.items()
                },
                "testConstellationsRatios": {
                     f"K{self.get_constellation_custom_id(constellation)}": amount/(amount + test_constellations_false[constellation]) if constellation in test_constellations_false else 1
                    for constellation, amount in test_constellations_right.items()
                },
                "trainRouteErrorsRatios": {
                    f"R{self.get_router_error_custom_id(route_error)}".replace("RNO_ERROR", "R-"): amount/(amount + train_route_errors_false[route_error]) if route_error in train_route_errors_false else 1
                    for route_error, amount in train_route_errors_right.items()
                },
                "testRouteErrorsRatios": {
                    f"R{self.get_router_error_custom_id(route_error)}".replace("RNO_ERROR", "R-"): amount/(amount + test_route_errors_false[route_error]) if route_error in test_route_errors_false else 1
                    for route_error, amount in test_route_errors_right.items()
                },
            }
            
            # For the cases when a constellation is not in the "right" constellations/route errors array
            for constellation in train_constellations_false:
                if f"K{self.get_constellation_custom_id(constellation)}" not in meta_logs_json[name]["trainConstellationsRatios"]:
                    meta_logs_json[name]["trainConstellationsRatios"][f"K{self.get_constellation_custom_id(constellation)}"] = 0
            for constellation in test_constellations_false:
                if f"K{self.get_constellation_custom_id(constellation)}" not in meta_logs_json[name]["testConstellationsRatios"]:
                    meta_logs_json[name]["testConstellationsRatios"][f"K{self.get_constellation_custom_id(constellation)}"] = 0
            for route_error in train_route_errors_false:
                if f"R{self.get_router_error_custom_id(route_error)}".replace("RNO_ERROR", "R-") not in meta_logs_json[name]["trainRouteErrorsRatios"]:
                    meta_logs_json[name]["trainRouteErrorsRatios"][f"R{self.get_router_error_custom_id(route_error)}".replace("RNO_ERROR", "R-")] = 0
            for route_error in test_route_errors_false:
                if f"R{self.get_router_error_custom_id(route_error)}".replace("RNO_ERROR", "R-") not in meta_logs_json[name]["testRouteErrorsRatios"]:
                    meta_logs_json[name]["testRouteErrorsRatios"][f"R{self.get_router_error_custom_id(route_error)}".replace("RNO_ERROR", "R-")] = 0
                    
                
            logs_json[name] = {
                "trainf1": train_f1,
                "testf1": test_f1,
                "trainacc": train_acc,
                "testacc": test_acc,
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp)
            }
            
            logs_csv.append([name,train_f1,test_f1,train_acc,test_acc,tn,fp,fn,tp])
            
            print(f"{name}: test_f1={test_f1:.3f}, train_f1={train_f1:.3f}, test_acc={test_acc:.3f}, train_acc={train_acc:.3f}")
            print(f"{name}: tn={tn}, fp={fp}, fn={fn}, tp={tp}")
            
            MLMatcher.store(clf, name, config_train_id)

            if test_f1 > best_f1:
                best_f1 = test_f1
                best_model = clf
                best_model_name = name

        if best_model:
            print(f"Best model: {best_model_name} with F1={best_f1:.3f}")
            
        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}logs_train_all_config_train_id_{config_train_id}.csv"),"w") as my_csv:
            csvWriter = csv.writer(my_csv,delimiter=' ')
            csvWriter.writerows(logs_csv)
            
        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}logs_train_all_config_train_id_{config_train_id}.json"), 'w') as fp:
            json.dump(logs_json, fp, indent=4)
            
        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}/meta_train_logs/all_meta_logs_train_all_config_train_id_{config_train_id}.json"), 'w', encoding='utf-8') as fp:
            json.dump(meta_logs_json, fp, indent=4)
            
        highlight_meta_logs = {}
        highlight_meta_logs[f"best_model_{best_model_name}"] = meta_logs_json[best_model_name]
        highlight_meta_logs["average_all_models"] = {
            "trainConstellationsRatios": self.get_average_meta_ratio(meta_logs_json, "trainConstellationsRatios", best_model_name),
            "testConstellationsRatios": self.get_average_meta_ratio(meta_logs_json, "testConstellationsRatios", best_model_name),
            "trainRouteErrorsRatios": self.get_average_meta_ratio(meta_logs_json, "trainRouteErrorsRatios", best_model_name),
            "testRouteErrorsRatios": self.get_average_meta_ratio(meta_logs_json, "testRouteErrorsRatios", best_model_name),
        }
        
        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}/meta_train_logs/highlight_meta_logs_train_all_config_train_id_{config_train_id}.json"), 'w', encoding='utf-8') as fp:
            json.dump(highlight_meta_logs, fp, indent=4)
            
        constellation_names = [constellation_name for constellation_name in highlight_meta_logs["average_all_models"]["trainConstellationsRatios"] if constellation_name != "KNOT_SELECTED"]
        route_error_names = [route_error_name for route_error_name in highlight_meta_logs["average_all_models"]["trainRouteErrorsRatios"] if route_error_name != "RNOT_SELECTED"]
        constellation_names.sort()
        route_error_names.sort()
        
        csv_header = ["run"] + constellation_names + route_error_names
        csv_highlight_logs = [csv_header]
        
        # Add train const. and route er. for best model
        csv_highlight_logs.append(["bestTrain"] +
                                  [highlight_meta_logs[f"best_model_{best_model_name}"]["trainConstellationsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["trainConstellationsRatios"] else 0 for name in constellation_names] +
                                  [highlight_meta_logs[f"best_model_{best_model_name}"]["trainRouteErrorsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["trainRouteErrorsRatios"] else 0 for name in route_error_names])
        
        # Add test const. and route er. for best model
        csv_highlight_logs.append(["bestTest"] +
                                  [highlight_meta_logs[f"best_model_{best_model_name}"]["testConstellationsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["testConstellationsRatios"] else 0 for name in constellation_names] +
                                  [highlight_meta_logs[f"best_model_{best_model_name}"]["testRouteErrorsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["testRouteErrorsRatios"] else 0 for name in route_error_names])

        
        # Add train const. and route er. for average
        csv_highlight_logs.append(["averageTrain"] +
                                  [highlight_meta_logs["average_all_models"]["trainConstellationsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["trainConstellationsRatios"] else 0 for name in constellation_names] +
                                  [highlight_meta_logs["average_all_models"]["trainRouteErrorsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["trainRouteErrorsRatios"] else 0 for name in route_error_names])
        
        # Add test const. and route er. for average
        csv_highlight_logs.append(["averageTest"] +
                                  [highlight_meta_logs["average_all_models"]["testConstellationsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["testConstellationsRatios"] else 0 for name in constellation_names] +
                                  [highlight_meta_logs["average_all_models"]["testRouteErrorsRatios"][name]
                                   if name in highlight_meta_logs[f"best_model_{best_model_name}"]["testRouteErrorsRatios"] else 0 for name in route_error_names])
        
        
        
        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}/meta_train_logs/highlight_meta_logs_train_all_config_train_id_{config_train_id}.csv"),"w") as my_csv:
            csvWriter = csv.writer(my_csv,delimiter=' ')
            csvWriter.writerows(np.array(csv_highlight_logs).T)