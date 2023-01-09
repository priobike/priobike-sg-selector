import os
import numpy as np

from django.core.management.base import BaseCommand
from django.conf import settings
import pandas as pd

class Command(BaseCommand):
    """
    Gets the average train and test f1-scores from all models that got trained for a certain config train id.
    """
    logs_path = "ml_evaluation/logs/training/"

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('training_id', type=int)

    def handle(self, *args, **options):

        # Check if the path argument is valid
        if not options["training_id"]:
            raise Exception("Please specify a training_id to specify what should be analysed.")

        training_id = options["training_id"]

        df = pd.read_csv(os.path.join(settings.BASE_DIR, f"{self.logs_path}logs_train_all_config_train_id_{training_id}.csv"), sep=" ")
        train_f1_scores = df["trainf1"]
        test_f1_scores = df["testf1"]

        train_average = np.mean(np.array(train_f1_scores))
        test_average = np.mean(np.array(test_f1_scores))

        print(f"Average train f1: {train_average}")
        print(f"Average test f1: {test_average}")