import gzip
import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from composer.models import Constellation, RouteError
from sklearn.manifold import TSNE
from sklearn import decomposition
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ml_evaluation.configs.datasets import config_data_and_features


class Command(BaseCommand):

    SAVE_IMAGE_PATH = "backend/composer/logs/constellation_route_errors_clusters/"

    def get_constellation_custom_id(self, name):
        return Constellation.objects.filter(name=name).first().custom_id if name != "NOT_SELECTED" else name

    def get_route_error_custom_id(self, name):
        return RouteError.objects.filter(name=name).first().custom_id if name != "NOT_SELECTED" and name != "NO_ERROR" else name

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

        dataset_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/datasets/dataset_data_and_features_config_id_{str(config_data_and_features_id)}.json.gz")
        with gzip.open(dataset_path) as f:
            byte_array = f.read()
            dataset = json.loads(byte_array.decode("utf-8"))

        if not "constellations" in dataset:
            raise Exception("Dataset does not contain constellations.")

        if not "route_errors" in dataset:
            raise Exception("Dataset does not contain route errors.")

        # Only apply to selected matches and dont show constellations between no matches
        reduced_X, reduced_y, reduced_constellations, reduced_route_errors = [], [], [], []

        for index, label in enumerate(dataset["y"]):
            if label == 1:
                reduced_y.append(label)
                reduced_X.append(dataset["X"][index])
                reduced_constellations.append(
                    self.get_constellation_custom_id(dataset["constellations"][index]))
                """ reduced_constellations.append("Geradeaus" if "Geraudeaus" in dataset["constellations"][index]
                                              else "Abbiegung, Verläuft weiter geradeaus" if "Abbiegung, Verläuft weiter geradeaus" in dataset["constellations"][index]
                                                else "Abbiegung") """
                route_error_id = self.get_route_error_custom_id(
                    dataset["route_errors"][index])
                reduced_route_errors.append(
                    route_error_id if route_error_id != "NO_ERROR" else "Kein Fehler")

        n_components = 2

        # Run t-SNE
        perplexities = [30, 35, 40, 45, 50]
        for perplexity in perplexities:
            tsne = TSNE(n_components=n_components, perplexity=perplexity)
            tsne_result = tsne.fit_transform(np.array(reduced_X))

            # Plot the constellation results in 2D scatterplot
            tsne_result_df = pd.DataFrame(
                {'t-SNE 1': tsne_result[:, 0], 't-SNE 2': tsne_result[:, 1], 'label': reduced_constellations})
            fig, ax = plt.subplots(1)
            sns.scatterplot(x='t-SNE 1', y='t-SNE 2', hue='label',
                            data=tsne_result_df, ax=ax, s=20)
            lim = (tsne_result.min()-5, tsne_result.max()+5)
            ax.set_xlim(lim)
            ax.set_ylim(lim)
            ax.set_aspect('equal')
            ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

            handles, labels = ax.get_legend_handles_labels()

            handles = [handles[1], handles[2], handles[4], handles[0],
                       handles[7], handles[3], handles[5], handles[6]]
            labels = [labels[1], labels[2], labels[4], labels[0],
                      labels[7], labels[3], labels[5], labels[6]]

            ax.legend(handles, labels, loc=2)

            frame1 = plt.gca()
            frame1.axes.xaxis.set_ticklabels([])
            frame1.axes.yaxis.set_ticklabels([])

            # Save the plot to an png
            plt.savefig(os.path.join(settings.BASE_DIR, f"{self.SAVE_IMAGE_PATH}tSNE_config_data_and_features_id_{str(config_data_and_features_id)}_constellations_perplexity_{str(perplexity)}.pdf"),
                        format="pdf", bbox_inches="tight")

            # reset matplotlib
            plt.clf()
            plt.close()

            # Plot the route error results in 2D scatterplot
            tsne_result_df = pd.DataFrame(
                {'t-SNE 1': tsne_result[:, 0], 't-SNE 2': tsne_result[:, 1], 'label': reduced_route_errors})
            fig, ax = plt.subplots(1)
            sns.scatterplot(x='t-SNE 1', y='t-SNE 2', hue='label',
                            data=tsne_result_df, ax=ax, s=20)
            lim = (tsne_result.min()-5, tsne_result.max()+5)
            ax.set_xlim(lim)
            ax.set_ylim(lim)
            ax.set_aspect('equal')
            ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

            handles, labels = ax.get_legend_handles_labels()

            handles = [handles[0], handles[2], handles[3], handles[1]]
            labels = [labels[0], labels[2], labels[3], labels[1]]

            ax.legend(handles, labels, loc=2)

            frame1 = plt.gca()
            frame1.axes.xaxis.set_ticklabels([])
            frame1.axes.yaxis.set_ticklabels([])

            # Save the plot to an png
            plt.savefig(os.path.join(settings.BASE_DIR, f"{self.SAVE_IMAGE_PATH}tSNE_config_data_and_features_id_{str(config_data_and_features_id)}_route_errors_perplexity_{str(perplexity)}.pdf"),
                        format="pdf", bbox_inches="tight")

            # reset matplotlib
            plt.clf()
            plt.close()

        print("###### FINISHED APPLYING t-SNE AND CREATING THE IMAGES ######")
