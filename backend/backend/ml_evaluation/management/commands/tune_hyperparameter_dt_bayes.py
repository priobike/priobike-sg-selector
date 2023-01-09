# Train, Validation, Test Data
# StratifiedKFold mit Train und Validation
# Testen mit Test Data

import gzip
import json
import os
import json
import numpy as np
from django.core.management.base import BaseCommand
from sklearn.model_selection import train_test_split
from django.conf import settings
from ml_evaluation.configs.trainings import config_train
from ml_evaluation.configs.datasets import config_data_and_features
from ml_evaluation.utils import generate_feature_transformer
from sklearn.preprocessing import MinMaxScaler, StandardScaler, PowerTransformer
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from hyperopt import tpe, STATUS_OK, Trials, hp, fmin, STATUS_OK, space_eval


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Add an argument to the parser that
        # specifies train config that should be used
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

        # Apply one of the feature scaling techniques if it was specified in the config
        transformer = None
        model_name = None
        if config_data_and_features[config_data_and_features_id]["feature_transformation"]["normalization"]:
            transformer = MinMaxScaler()
            model_name = "min_max_scaler"
        elif config_data_and_features[config_data_and_features_id]["feature_transformation"]["standardization"]:
            transformer = StandardScaler()
            model_name = "standard_scaler"
        elif config_data_and_features[config_data_and_features_id]["feature_transformation"]["power_transformation"]:
            transformer = PowerTransformer(method='yeo-johnson')
            model_name = "yeo_johnson_power_transformer"

        if transformer is not None:
            X_train_numpy = np.array(X_train)
            X_test_numpy = np.array(X_test)
            column_transformer = generate_feature_transformer(features_numpy=X_train_numpy, transformer=transformer,
                                                    data_feature_config=config_data_and_features[config_data_and_features_id],
                                                    config_id=config_data_and_features_id, model_name=model_name)
                    
            X_train_numpy = column_transformer.transform(X_train_numpy)
            X_train = X_train_numpy.tolist()
            X_test_numpy = column_transformer.transform(X_test_numpy)
            X_test = X_test_numpy.tolist()

        # Define the search space
        parameter_space = {
            'criterion': hp.choice('criterion', ['gini', 'entropy', 'log_loss'],),
            'splitter': hp.choice('splitter', ['best', 'random'],),
            'max_depth': hp.choice('max_depth', np.arange(1, 20, dtype=int)),
            'min_samples_split': hp.choice('min_samples_split', np.arange(2, 100, dtype=int)),
            'min_samples_leaf': hp.choice('min_samples_leaf', np.arange(1, 100, dtype=int)),
        }

        scoring = 'f1'
        # Set up the k-fold cross-validation
        cv = RepeatedStratifiedKFold(
            n_splits=5, n_repeats=3, random_state=random_state)

        # Objective function
        def objective(params):
            svc = DecisionTreeClassifier(**params)
            scores = cross_val_score(
                svc, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
            # Extract the best score
            best_score = max(scores)
            # Loss must be minimized
            loss = - best_score
            # Dictionary with information for evaluation
            return {'loss': loss, 'params': params, 'status': STATUS_OK}

        # Trials to track progress
        bayes_trials = Trials()
        # Optimize
        best = fmin(fn=objective, space=parameter_space,
                    algo=tpe.suggest, max_evals=10000, trials=bayes_trials)

        # Print the index of the best parameters
        print(best)
        # Print the values of the best parameters
        print(space_eval(parameter_space, best))

        # Train model using the best parameters
        mlp = DecisionTreeClassifier(
            criterion=space_eval(parameter_space, best)['criterion'],
            splitter=space_eval(parameter_space, best)['splitter'],
            max_depth=space_eval(parameter_space, best)['max_depth'],
            min_samples_split=space_eval(parameter_space, best)[
                'min_samples_split'],
            min_samples_leaf=space_eval(parameter_space, best)['min_samples_leaf'],).fit(X_train, y_train)
        # Print the best f1 score for the testing dataset
        print(
            f'The f1 score for the testing dataset is {mlp.score(X_test, y_test):.8f}')
