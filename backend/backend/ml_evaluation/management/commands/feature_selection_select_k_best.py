from django.core.management.base import BaseCommand
from django.conf import settings
import gzip
import json

from ml_evaluation.utils import get_feature_names

import pandas as pd
import os
from ml_evaluation.configs.datasets import config_data_and_features
from ml_evaluation.configs.features import name_transformation_base, name_transformation_extra, feature_order
from sklearn.feature_selection import SelectKBest
from matplotlib_venn import venn2
import matplotlib.pyplot as plt


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
        extractors = config["feature_extractor_combination"]

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

        data = pd.DataFrame(data=dataset["X"], columns=latex_feature_names)
        data['target'] = dataset["y"]

        X = data.drop('target', axis=1)
        y = data['target']

        selector = SelectKBest()
        """ print("Original feature shape:", X.shape) """

        new_X = selector.fit_transform(X, y)
        """ print("Transformed feature shape:", new_X.shape) """

        selected_features = selector.get_feature_names_out()
        removed_features = [
            name for name in latex_feature_names if name not in selected_features]

        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}/feature_select_k_best/logs_selected_features_config_data_and_features_id_{config_data_and_features_id}.json"), 'w') as fp:
            json.dump(selected_features.tolist(), fp, indent=4)

        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}/feature_select_k_best/logs_removed_features_config_data_and_features_id_{config_data_and_features_id}.json"), 'w') as fp:
            json.dump(removed_features, fp, indent=4)

        plt.rcParams["figure.figsize"] = [8, 8]

        ordered_selected_features = [
            feature for feature in feature_order if feature in selected_features.tolist()]

        ordered_latex_feature_names = [
            feature for feature in feature_order if feature in latex_feature_names]

        sets = [set(ordered_selected_features),
                set(ordered_latex_feature_names)]

        # Create and instance of a venn diagram with 3 areas
        diagram = venn2(sets, ("SelectKBest", "Alle Features"))

        # Set text content of areas
        diagram.get_label_by_id('10').set_text("\n".join(
            [feature for feature in ordered_selected_features if feature not in ordered_latex_feature_names]))
        diagram.get_label_by_id('01').set_text("\n".join(
            [feature for feature in ordered_latex_feature_names if feature not in ordered_selected_features]))
        diagram.get_label_by_id('11').set_text("\n".join(
            [feature for feature in ordered_selected_features if feature in ordered_latex_feature_names]))

        diagram.get_patch_by_id('11').set_alpha(1)
        diagram.get_patch_by_id('11').set_color('#949494')
        diagram.get_patch_by_id('01').set_alpha(1)
        diagram.get_patch_by_id('01').set_color('#c9c9c9')

        # Modify font sizes
        for text in diagram.set_labels:
            text.set_fontsize(16)
        for text in diagram.subset_labels:
            text.set_fontsize(12)
        plt.tight_layout()
        plt.savefig(os.path.join(settings.BASE_DIR, f"{self.logs_path}feature_select_k_best/logs_select_k_best_features_config_data_and_features_id_{config_data_and_features_id}.pdf"),
                    format="pdf")
