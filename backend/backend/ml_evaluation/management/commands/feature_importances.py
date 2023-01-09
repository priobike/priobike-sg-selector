from django.core.management.base import BaseCommand
from django.conf import settings
import matplotlib.pyplot as plt
from ml_evaluation.utils import get_feature_names
import numpy as np
import os
import pickle
from ml_evaluation.configs.datasets import config_data_and_features
from ml_evaluation.configs.trainings import config_train
from ml_evaluation.configs.classifiers import classifiers
from ml_evaluation.configs.features import name_transformation_base, name_transformation_extra


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('config_train_id', type=int)

    def handle(self, *args, **options):

        # Check if the path argument is valid
        if not options["config_train_id"]:
            raise Exception(
                "Please specify a config_train_id to specify which training config should be analysed.")

        config_train_id = options["config_train_id"]
        config_data_and_features_id = config_train[
            config_train_id]["config_data_and_features"]

        config = config_data_and_features[config_data_and_features_id]
        extractors = config["feature_extractor_combination"]

        plt.rcParams["figure.figsize"] = [14, 7]
        plt.rcParams["figure.autolayout"] = True
        columns = 3
        rows = 1
        index = 1

        feature_names = get_feature_names(extractors, config)

        latex_feature_names = [
            name_transformation_extra[name] if name in name_transformation_extra else name_transformation_base[name]
            for name in feature_names
        ]

        for name, classifier in classifiers.items():
            model_path = os.path.join(
                settings.BASE_DIR, f'ml_evaluation/models/model_config_train_id_{config_train_id}_name_{name}.joblib')

            try:
                with open(model_path, 'rb') as f:
                    clf = pickle.load(f)
            except FileNotFoundError:
                print("Model does not exist!")

            if hasattr(clf, 'feature_importances_'):
                importances = clf.feature_importances_

                indices = np.argsort(importances)

                plt.subplot(rows, columns, index)
                plt.title(f'Feature Importances {name}')
                plt.barh(range(len(indices)),
                         importances[indices], color='grey', align='center')
                plt.yticks(range(len(indices)), [
                           latex_feature_names[i] for i in indices])
                plt.xlabel('Relative Importance')

                index += 1

        plt.savefig(os.path.join(settings.BASE_DIR, f"../backend/ml_evaluation/logs/feature_importance/_TOTAL_feature_importance_plot_config_train_id_{str(config_train_id)}.pdf"),
                    format="pdf", bbox_inches="tight")
        plt.clf()
        plt.close()

        for name, classifier in classifiers.items():
            model_path = os.path.join(
                settings.BASE_DIR, f'routing/ml_evaluation/models/model_config_train_id_{config_train_id}_name_{name}.joblib')

            try:
                with open(model_path, 'rb') as f:
                    clf = pickle.load(f)
            except FileNotFoundError:
                print("Model does not exist!")

            if hasattr(clf, 'feature_importances_'):
                importances = clf.feature_importances_

                indices = np.argsort(importances)

                plt.figure(figsize=(10, 15))
                plt.title(f'Feature Importances {name}')
                plt.barh(range(len(indices)),
                         importances[indices], color='grey', align='center')
                plt.yticks(range(len(indices)), [
                           latex_feature_names[i] for i in indices])
                plt.xlabel('Relative Importance')
                plt.savefig(os.path.join(settings.BASE_DIR, f"../backend/ml_evaluation/logs/feature_importance/feature_importance_plot_config_train_id_{str(config_train_id)}_name_{name}.pdf"),
                            format="pdf", bbox_inches="tight")

                index += 1
