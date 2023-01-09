import json
import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from ml_evaluation.configs.datasets import config_data_and_features
from ml_evaluation.configs.features import name_transformation_base, name_transformation_extra


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

        # Get the log file of the creation of the dataset
        statistics_file_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/logs/dataset_with_features/logs_generate_dataset_config_feature_and_data_id_{str(config_data_and_features_id)}.json")
        with open(statistics_file_path) as f:
            statistics = json.load(f)

        timings = statistics["timings"]

        # csv header
        fieldnames = ['feature', 'baseMean', 'baseMin',
                      'baseMax', 'extraMean', 'extraMin', 'extraMax']

        # BASE TIMES CSV
        rows = [
            [
                next(value for key, value in name_transformation_base.items()
                     if key in name).partition('_')[0],
                timing["base_timing_mean"],
                timing["base_timing_min"],
                timing["base_timing_max"],
                timing["extra_timing_mean"] if timing["extra_timing_max"] < 999999 else 0,
                timing["extra_timing_min"] if timing["extra_timing_max"] < 999999 else 0,
                timing["extra_timing_max"] if timing["extra_timing_max"] < 999999 else 0
            ]
            for name, timing in timings.items() if timing["base_timing_mean"] != -524
        ]

        ordered_rows = [
            next(x for x in rows if x[0] == value.partition('_')[0])
            for key, value in name_transformation_base.items() if not ("_b" in value or "_c" in value)
        ]

        csv_file_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/logs/dataset_with_features/feature_timings/timings_generate_dataset_config_feature_and_data_id_{str(config_data_and_features_id)}_base.csv")
        with open(csv_file_path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=" ")
            writer.writerow(fieldnames)
            writer.writerows(ordered_rows)

        # EXTRA TIMES CSV
        rows = [
            [
                name_transformation_extra[name],
                timing["base_timing_mean"],
                timing["base_timing_min"],
                timing["base_timing_max"],
                timing["extra_timing_mean"] if timing["extra_timing_max"] < 999999 else 0,
                timing["extra_timing_min"] if timing["extra_timing_max"] < 999999 else 0,
                timing["extra_timing_max"] if timing["extra_timing_max"] < 999999 else 0
            ]
            for name, timing in timings.items() if name in name_transformation_extra
        ]

        ordered_rows = [
            next(x for x in rows if x[0] == value)
            for key, value in name_transformation_extra.items()
        ]

        csv_file_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/logs/dataset_with_features/feature_timings/timings_generate_dataset_config_feature_and_data_id_{str(config_data_and_features_id)}_extra.csv")
        with open(csv_file_path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=" ")
            writer.writerow(fieldnames)
            writer.writerows(ordered_rows)
