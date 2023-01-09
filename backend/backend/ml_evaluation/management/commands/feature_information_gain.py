from django.core.management.base import BaseCommand
from django.conf import settings
import gzip
import json
import matplotlib.pyplot as plt
from routing.matching.ml.features.types import FeatureType
from ml_evaluation.utils import get_feature_names
import pandas as pd
import numpy as np
import os
from ml_evaluation.configs.datasets import config_data_and_features
from ml_evaluation.configs.features import name_transformation_base, name_transformation_extra
from sklearn.feature_selection import mutual_info_classif


class Command(BaseCommand):

    logs_path = "ml_evaluation/logs/"

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('config_data_and_features_id', type=int)

    def handle(self, *args, **options):

        # Check if the path argument is valid
        if not options["config_data_and_features_id"]:
            raise Exception(
                "Please specify a config_data_and_features_id to specify which dataset should be analysed.")

        config_data_and_features_id = options["config_data_and_features_id"]

        # Get feature extractors from config
        if config_data_and_features_id not in config_data_and_features:
            raise KeyError('No config for the given config id available.')

        config = config_data_and_features[config_data_and_features_id]
        extractors = config_data_and_features[
            config_data_and_features_id]["feature_extractor_combination"]

        dataset_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/datasets/dataset_data_and_features_config_id_{str(config_data_and_features_id)}.json.gz")
        with gzip.open(dataset_path) as f:
            byte_array = f.read()
            dataset = json.loads(byte_array.decode("utf-8"))

        feature_names = get_feature_names(extractors, config)

        latex_feature_names = [
            name_transformation_extra[name] if name in name_transformation_extra else name_transformation_base[name]
            for name in feature_names
        ]

        features_discrete_value_mask = []
        for extractor in config_data_and_features[config_data_and_features_id]["feature_extractor_combination"]:
            for feature_type_dc in extractor.FEATURE_TYPES_DC:
                if feature_type_dc == FeatureType.DISCRETE:
                    features_discrete_value_mask.append(True)
                elif feature_type_dc == FeatureType.CONTINUOUS:
                    features_discrete_value_mask.append(False)

        data = pd.DataFrame(data=dataset["X"], columns=latex_feature_names)
        data['target'] = dataset["y"]

        X = data.drop('target', axis=1)
        y = data['target']

        importances = mutual_info_classif(
            X, y, discrete_features=features_discrete_value_mask)
        indices = np.argsort(importances)

        plt.barh(range(len(indices)), importances[indices], color=(
            148/255, 150/255, 152/255), align='center')
        plt.yticks(range(len(indices)), [
                   latex_feature_names[i] for i in indices])

        plt.savefig(os.path.join(settings.BASE_DIR, f"../backend/ml_evaluation/logs/feature_information_gain/features_information_gain_plot_config_data_and_features_id_{str(config_data_and_features_id)}.pdf"),
                    format="pdf", bbox_inches="tight")
