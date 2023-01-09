# Train, Validation, Test Data
# StratifiedKFold mit Train und Validation
# Testen mit Test Data

import gzip
import json
import os
import json
from skopt import BayesSearchCV
from django.core.management.base import BaseCommand
from sklearn.model_selection import train_test_split
from django.conf import settings
from ml_evaluation.configs.trainings import config_train
from sklearn.metrics import f1_score
from sklearn.svm import SVC
from sklearn.model_selection import RepeatedStratifiedKFold


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies feature config that should be used
        parser.add_argument('config_train_id', type=int)

    def handle(self, *args, **options):
        # Check if the path argument is valid
        if not options["config_train_id"]:
            raise Exception(
                "Please specify a config_train_id to specify which features should be extracted.")

        config_train_id = options["config_train_id"]

        if config_train_id not in config_train:
            raise KeyError('No config for the given config id available.')

        config_data_and_features_id = config_train[
            config_train_id]["config_data_and_features"]

        dataset_path = os.path.join(
            settings.BASE_DIR, f"../backend/ml_evaluation/datasets/dataset_data_and_features_config_id_{str(config_data_and_features_id)}.json.gz")
        with gzip.open(dataset_path) as f:
            byte_array = f.read()
            dataset = json.loads(byte_array.decode("utf-8"))

        y = dataset["y"]
        X = dataset["X"]

        random_state = 123

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=config_train[config_train_id]["shuffle"], random_state=random_state)

        # define search space
        params = dict()
        params['C'] = (1e-6, 100.0, 'log-uniform')
        params['gamma'] = (1e-6, 100.0, 'log-uniform')
        params['kernel'] = ['rbf']
        # define evaluation
        cv = RepeatedStratifiedKFold(
            n_splits=5, n_repeats=6, random_state=random_state)
        # define the search
        search = BayesSearchCV(
            estimator=SVC(), search_spaces=params, n_jobs=-1, cv=cv, scoring="f1", verbose=5)
        # perform the search
        search.fit(X_train, y_train)
        # report the best result
        print(search.best_score_)
        print(search.best_params_)
        # test with test set
        clf = search.best_estimator_
        print("Test F1-Score: ")
        print(f1_score(y_test, clf.predict(X_test)))
