from django.core.management.base import BaseCommand
from django.conf import settings
import gzip
import json
import pickle
import pandas as pd
import os

from sklearn.feature_selection import RFECV
from matplotlib_venn import venn3
import matplotlib.pyplot as plt

from ml_evaluation.configs.trainings import config_train
from ml_evaluation.configs.datasets import config_data_and_features
from ml_evaluation.configs.classifiers import classifiers
from ml_evaluation.configs.features import name_transformation_base, name_transformation_extra, feature_order
from ml_evaluation.utils import get_feature_names


class Command(BaseCommand):

    logs_path = "ml_evaluation/logs/"

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('training_id', type=int)

    def handle(self, *args, **options):

        # Check if the path argument is valid
        if not options["training_id"]:
            raise Exception(
                "Please specify a training_id to specify what should be analysed.")

        training_id = options["training_id"]

        # Get feature extractors from config
        if training_id not in config_train:
            raise KeyError('No config for the given config id available.')

        data_feature_training_id = config_train[training_id]["config_data_and_features"]
        config = config_data_and_features[data_feature_training_id]
        extractors = config["feature_extractor_combination"]

        dataset_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/datasets/dataset_data_and_features_config_id_{str(data_feature_training_id)}.json.gz")
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

        logs = {}

        selected = []
        ordered_selected = []
        selected_names = []

        for name, classifier in classifiers.items():
            model_path = os.path.join(
                settings.BASE_DIR, f'ml_evaluation/models/model_config_train_id_{training_id}_name_{name}.joblib')
            try:
                with open(model_path, 'rb') as f:
                    clf = pickle.load(f)
            except FileNotFoundError:
                print("Model does not exist!")
            if hasattr(clf, "feature_importances_") or hasattr(clf, "coef_"):
                rfe = RFECV(classifier)
                rfe.fit(X, y)
                logs[name] = {
                    "summary": {},
                    "details": []
                }

                if len(selected) < 3:
                    selected.append(set(rfe.get_feature_names_out().tolist()))
                    ordered_selected.append(
                        [feature for feature in feature_order if feature in rfe.get_feature_names_out().tolist()])
                    selected_names.append(name)

                logs[name]["summary"] = {
                    "selected_features": rfe.get_feature_names_out().tolist(),
                    "removed_features": [name for name in latex_feature_names if name not in rfe.get_feature_names_out().tolist()]
                }

                logs[name]["details"] = [{
                    "feature":  feature,
                    "selected": True if rfe.support_[index] else False,
                    "rank": int(rfe.ranking_[index])
                } for index, feature in enumerate(latex_feature_names)]

                logs[name]["details"] = sorted(
                    logs[name]["details"], key=lambda d: d['rank'], reverse=True)

        with open(os.path.join(settings.BASE_DIR, f"{self.logs_path}feature_recursive_feature_elimination/logs_feature_recursive_feature_elimination_config_training_id_{training_id}.json"), 'w') as fp:
            json.dump(logs, fp, indent=4)

        plt.rcParams["figure.figsize"] = [8, 8]

        # Create and instance of a venn diagram with 3 areas
        diagram = venn3(
            selected, (selected_names[0], selected_names[1], selected_names[2]))

        # Set text content of areas
        diagram.get_label_by_id('100').set_text("\n".join(
            [feature for feature in ordered_selected[0] if feature not in ordered_selected[1] and feature not in ordered_selected[2]]))
        diagram.get_label_by_id('110').set_text("\n".join(
            [feature for feature in ordered_selected[0] if feature in ordered_selected[1] and feature not in ordered_selected[2]]))
        diagram.get_label_by_id('111').set_text("\n".join(
            [feature for feature in ordered_selected[0] if feature in ordered_selected[1] and feature in ordered_selected[2]]))
        diagram.get_label_by_id('010').set_text("\n".join(
            [feature for feature in ordered_selected[1] if feature not in ordered_selected[0] and feature not in ordered_selected[2]]))
        diagram.get_label_by_id('001').set_text("\n".join(
            [feature for feature in ordered_selected[2] if feature not in ordered_selected[0] and feature not in ordered_selected[1]]))
        diagram.get_label_by_id('011').set_text("\n".join(
            [feature for feature in ordered_selected[2] if feature in ordered_selected[1] and feature not in ordered_selected[0]]))
        diagram.get_label_by_id('101').set_text("\n".join(
            [feature for feature in ordered_selected[1] if feature not in ordered_selected[1] and feature in ordered_selected[2]]))

        diagram.get_patch_by_id('100').set_alpha(0.25)
        diagram.get_patch_by_id('110').set_alpha(0.45)
        diagram.get_patch_by_id('111').set_alpha(0.6)
        diagram.get_patch_by_id('010').set_alpha(0.3)
        diagram.get_patch_by_id('001').set_alpha(0.2)
        diagram.get_patch_by_id('011').set_alpha(0.4)
        diagram.get_patch_by_id('101').set_alpha(0.5)

        color = '#000000'
        diagram.get_patch_by_id('100').set_color(color)
        diagram.get_patch_by_id('110').set_color(color)
        diagram.get_patch_by_id('111').set_color(color)
        diagram.get_patch_by_id('010').set_color(color)
        diagram.get_patch_by_id('001').set_color(color)
        diagram.get_patch_by_id('011').set_color(color)
        diagram.get_patch_by_id('101').set_color(color)

        # Modify font sizes
        for text in diagram.set_labels:
            text.set_fontsize(16)
        for text in diagram.subset_labels:
            text.set_fontsize(12)
        plt.tight_layout()
        plt.savefig(os.path.join(settings.BASE_DIR, f"{self.logs_path}feature_recursive_feature_elimination/logs_feature_recursive_feature_elimination_config_training_id_{training_id}.pdf"),
                    format="pdf")
