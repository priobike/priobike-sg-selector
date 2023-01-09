import os
import pickle
from typing import Tuple

import numpy as np
from django.conf import settings
from django.contrib.gis.geos import LineString
from django.db.models.query import QuerySet
from routing.matching import RouteMatcher
from routing.matching.ml.features import get_features
from routing.matching.ml.configs_production.trainings import config_train
from routing.matching.ml.configs_production.datasets import config_data_and_features
from routing.matching.ml.path_configs import models_production_path, models_evaluation_path


class MLMatcher(RouteMatcher):
    """
    An elementwise matcher using a ML model.
    """

    @classmethod
    def store(cls, clf, model_name, config_train_id):
        """Store a model on the disk.

        Args:
            clf (sklearn classifier model): The trained model.
            model_name (_type_): The name under which the model should be saved.
            config_train_id (_type_): The ID under which circumstances the model got trained.
        """
        model_path = os.path.join(
            settings.BASE_DIR, f'{models_evaluation_path}model_config_train_id_{config_train_id}_name_{model_name}.joblib')
        with open(model_path, 'wb') as f:
            pickle.dump(clf, f)

    def __init__(self, *args, **kwargs):
        """
        Initialize the ml matcher.
        """
        super().__init__(*args, **kwargs)
        
        # Needs to be set according to the available configurations in routing.matching.ml.configs_production.trainings.
        self.config_train_id = 8603009191
        # Needs to be set according to the models available in routing.matching.ml.models.
        self.model_name = "MLP"
        
        # Load the ml model.
        model_path = os.path.join(
            settings.BASE_DIR, f'{models_production_path}model_config_train_id_{self.config_train_id}_name_{self.model_name}.joblib')
        try:
            with open(model_path, 'rb') as f:
                self.clf = pickle.load(f)
        except FileNotFoundError:
            print("Model does not exist!")

        # Get from the provided config, whether a feature transformer should be used.
        data_features_id = config_train[self.config_train_id]["config_data_and_features"]
        min_max_scaler_used = config_data_and_features[
            data_features_id]["feature_transformation"]["normalization"]
        standard_scaler_used = config_data_and_features[
            data_features_id]["feature_transformation"]["standardization"]
        yeo_johnson_power_transformer_used = config_data_and_features[
            data_features_id]["feature_transformation"]["power_transformation"]

        # If a feature transformer should be used, load it from the disk.
        if min_max_scaler_used:
            path = os.path.join(
                settings.BASE_DIR, f'{models_production_path}model_config_feature_data_id_{data_features_id}_name_min_max_scaler.joblib')
            try:
                with open(path, 'rb') as f:
                    self.transformer = pickle.load(f)
            except FileNotFoundError:
                print("Min max scaler model does not exist!")
        elif standard_scaler_used:
            path = os.path.join(
                settings.BASE_DIR, f'{models_production_path}model_config_feature_data_id_{data_features_id}_name_standard_scaler.joblib')
            try:
                with open(path, 'rb') as f:
                    self.transformer = pickle.load(f)
            except FileNotFoundError:
                print("Standard scaler model does not exist!")
        elif yeo_johnson_power_transformer_used:
            path = os.path.join(
                settings.BASE_DIR, f'{models_production_path}model_config_feature_data_id_{data_features_id}_name_yeo_johnson_power_transformer.joblib')
            try:
                with open(path, 'rb') as f:
                    self.transformer = pickle.load(f)
            except FileNotFoundError:
                print("Yeo Johnson power transformer model does not exist!")
        else:
            self.transformer = None

    def matches(self, lsas: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        """
        Return the LSAs that match the route, as a queryset.
        """

        if not hasattr(self, 'clf'):
            raise KeyError("NO MODEL FOUND!")

        if not hasattr(self, 'config_train_id'):
            raise KeyError("NO CONFIG TRAIN ID FOUND!")

    	# Get the training/inference config.
        config_train_id = self.config_train_id
        if config_train_id not in config_train:
            raise KeyError(
                'No config for the given config train id available. Check whether it is in routing.matching.ml.configs_production.trainings')

        # Get the data/feature config.
        config_data_and_features_id = config_train[
            config_train_id]["config_data_and_features"]
        if config_data_and_features_id not in config_data_and_features:
            raise KeyError(
                'No config for the given config data/features id available. Check whether it is in routing.matching.ml.configs_production.datasets')
        data_features_config = config_data_and_features[config_data_and_features_id]

        lsas, route = super().matches(lsas, route)

        # Calculate the features. What features are used is specified in the data/feature config.
        X = np.array([get_features(lsa, route, data_features_config)[0]
                     for lsa in lsas])

        # If the dataset ist empty, return an empty queryset (when there are no lsas). 
        if len(X) == 0:
            return lsas.filter(pk__in=[]), route
            
        # If a feature transformer is used, apply it to the features.
        if self.transformer is not None:
            X_numpy = np.array(X)
            X_numpy = self.transformer.transform(X_numpy)
            X = X_numpy.tolist()

        # Perform the matching.
        y = self.clf.predict(X)
        pks_to_include = [lsa.pk for lsa,
                        prediction in zip(lsas, y) if prediction]

        return lsas.filter(pk__in=pks_to_include), route
