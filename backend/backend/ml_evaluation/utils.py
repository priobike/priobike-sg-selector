import pickle
import os.path
from sklearn.compose import ColumnTransformer
from typing import List
from django.conf import settings
from routing.matching.ml.features.types import FeatureType
from routing.matching.ml.features.feature_bearing_diffs import BearingDiffs
from routing.matching.ml.features.feature_length_diffs import LengthDiffs
from routing.matching.ml.features.feature_lengths import Lengths
from routing.matching.ml.features.feature_point_distances import PointDistances
from routing.matching.ml.path_configs import models_evaluation_path



def get_feature_names(extractors, config) -> List[str]:
    """
    Returns the feature names of every single feature if an extractor extracts multiple features
    """
    feature_names = []

    for extractor in extractors:
        if extractor in config:
            for feature in config[extractor]:
                feature_names.append(
                    f"{extractor.get_name_of_file()}_{extractor.FEATURE_NAMES[feature]}")
        else:
            feature_count = len(extractor.FEATURE_NAMES)
            for i in range(feature_count):
                feature_names.append(
                    f"{extractor.get_name_of_file()}_{extractor.FEATURE_NAMES[i]}")

    return feature_names

def generate_feature_transformer(features_numpy, transformer, data_feature_config, config_id, model_name):
    """Trains and save a feature transformer for the given transformer type and given features.

    Args:
        features_numpy (Numpy Array): Numpy Array with the dataset containing the features
        transformer (sklearn transformer object): The transformer model that should be trained and saved (either sklearn.preprocessing.StandardScaler or sklearn.preprocessing.Normalizer or sklearn.preprocessing.PowerTransformer).
        data_feature_config (dict): The data and feature config (ml_evaluation.configs.datasets)
        config_id (number): The id of the data and feature config (ml_evaluation.configs.datasets)
        model_name (string): The name of the feature transformer that should be saved (eg StandardScaler or Normalizer or PowerTransformer)
    
    Returns:
        sklearn transformer: The trained and also saved transformer.
    """
    setting = None
    
    if "feature_transformation_only_numerical" in data_feature_config and not data_feature_config["feature_transformation_only_numerical"]:
        setting = transformer.fit(features_numpy)
        model_path = os.path.join(
            settings.BASE_DIR, f'{models_evaluation_path}model_config_feature_data_id_{config_id}_name_{model_name}.joblib')
        with open(model_path, 'wb') as f:
            pickle.dump(setting, f)
    else:
        numerical_features_indices = []
        # Gather all numerical features indices
        index = 0
        for extractor in data_feature_config["feature_extractor_combination"]:
            features_types = None
            if extractor == BearingDiffs:
                features_types = [extractor.FEATURE_TYPES[i]
                                    for i in data_feature_config[BearingDiffs]]
            if extractor == LengthDiffs:
                features_types = [extractor.FEATURE_TYPES[i]
                                    for i in data_feature_config[LengthDiffs]]
            if extractor == Lengths:
                features_types = [extractor.FEATURE_TYPES[i]
                                    for i in data_feature_config[Lengths]]
            if extractor == PointDistances:
                features_types = [extractor.FEATURE_TYPES[i]
                                    for i in data_feature_config[PointDistances]]
            if features_types is None:
                features_types = extractor.FEATURE_TYPES
            for feature_type in features_types:
                if feature_type == FeatureType.NUMERICAL:
                    numerical_features_indices.append(index)
                index += 1

        column_transformer = ColumnTransformer([
            ('transformer', transformer, numerical_features_indices)
        ], remainder='passthrough')

        setting = column_transformer.fit(features_numpy)

        model_path = os.path.join(
            settings.BASE_DIR, f'{models_evaluation_path}model_config_feature_data_id_{config_id}_name_{model_name}.joblib')
        with open(model_path, 'wb') as f:
            pickle.dump(setting, f)
            
    return setting