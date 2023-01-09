"""
Copy the config from ml_evaluation.configs.trainings to this file that should be used in production.

Note: Don't forget to also copy the required (trained) models from ml_evaluation.models to routing.matching.ml.models
(the classifier model and if needed the feature transformer model) and the config from ml_evaluation.configs.datasets to 
routing.matching.ml.configs.datasets
"""
config_train = {
    8603009191: {
        "config_data_and_features": 8603,
        "undersample": False,
        "shuffle": True,
        "ssf": True,
    },
}
