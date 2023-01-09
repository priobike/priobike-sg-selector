import json
import csv
import os
from pathlib import Path
import numpy as np

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def get_statistics_csv(self, timings, name):
        np_timings = np.array(timings)
        return [
            name,
            float(np.mean(np_timings)),
            float(np.min(np_timings)),
            float(np.max(np_timings))
        ]

    def handle(self, *args, **options):
        extended_method_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/logs/dataset_with_features/projection_timings/timings_projection_extended_method.json")
        normal_old_method_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/logs/dataset_with_features/projection_timings/timings_projection_old_normal_method.json")
        normal_new_method_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/logs/dataset_with_features/projection_timings/timings_projection_new_normal_method.json")

        field_names = ["projectionMethod", "mean", "min", "max"]
        rows = []

        if Path(normal_old_method_path).is_file():
            with open(normal_old_method_path) as f:
                timings = json.load(f)
                rows.append(self.get_statistics_csv(timings, "P1"))

        if Path(extended_method_path).is_file():
            with open(extended_method_path) as f:
                timings = json.load(f)
                rows.append(self.get_statistics_csv(timings, "P2"))

        if Path(normal_new_method_path).is_file():
            with open(normal_new_method_path) as f:
                timings = json.load(f)
                rows.append(self.get_statistics_csv(timings, "P3"))

        csv_file_path = os.path.join(settings.BASE_DIR, f"../backend/ml_evaluation/logs/dataset_with_features/projection_timings/projection_timings.csv")
        with open(csv_file_path, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=" ")
            writer.writerow(field_names)
            writer.writerows(rows)