from django.core.management.base import BaseCommand
from django.conf import settings
import gzip
import json
import matplotlib.pyplot as plt
from routing.matching.ml.features.types import FeatureType
from ml_evaluation.utils import get_feature_names
import seaborn as sns
import numpy as np
import pandas as pd
import os
from ml_evaluation.configs.features import name_transformation_base, name_transformation_extra, feature_order
from ml_evaluation.configs.datasets import config_data_and_features


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('config_data_and_features_id', type=int)

    def handle(self, *args, **options):
        """ https://towardsdatascience.com/the-art-of-finding-the-best-features-for-machine-learning-a9074e2ca60d """

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

        ordered_latex_feature_names = [
            name for name in feature_order if name in latex_feature_names]
        ordered_latex_feature_names.append("Label")

        data = pd.DataFrame(data=dataset["X"], columns=latex_feature_names)
        data['Label'] = dataset["y"]
        corr = data.corr(method='kendall')
        corr = corr.reindex(ordered_latex_feature_names)
        corr = corr.reindex(columns=ordered_latex_feature_names)

        # Finde categorial features
        features_to_drop = []
        for extractor in config_data_and_features[config_data_and_features_id]["feature_extractor_combination"]:
            if extractor.FEATURE_TYPES[0] == FeatureType.CATEGORIAL:
                features_to_drop.append(extractor)
        features_names_to_drop = get_feature_names(features_to_drop, config)
        latex_feature_names_to_drop = [
            name_transformation_extra[name] if name in name_transformation_extra else name_transformation_base[name]
            for name in features_names_to_drop
        ]
        latex_feature_names_to_drop.append("Label")
        # Remove categorial features (correlation not meant for those)
        corr = corr.drop(columns=latex_feature_names_to_drop,
                         index=latex_feature_names_to_drop)

        # Get indeces of highest values
        mask_max = np.tril(m=np.ones_like(corr, dtype=np.bool), k=-1)
        highest = corr.where(mask_max, other=0).abs(
        ).stack().nlargest(80).index.tolist()
        print(highest)

        # visualise the data with seaborn
        mask = np.triu(np.ones_like(corr, dtype=np.bool))
        sns.set_style(style='white')
        f, ax = plt.subplots(figsize=(18, 18))
        cmap = sns.diverging_palette(10, 250, as_cmap=True)
        plot = sns.heatmap(corr, mask=mask, cmap=cmap, center=0.00,
                           square=True,
                           linewidths=.5, ax=ax, cbar_kws=dict(location="right", shrink=.5, anchor=(-1, 0.75)))
        fig = plot.get_figure()
        fig.savefig(os.path.join(settings.BASE_DIR, f"../backend/ml_evaluation/logs/feature_correlation/correlation_plot_config_data_and_features_id_{str(config_data_and_features_id)}.pdf"),
                    format="pdf", bbox_inches="tight")
