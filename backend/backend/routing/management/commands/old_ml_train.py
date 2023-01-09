import gzip
import json
import os

import numpy as np
from django.core.management.base import BaseCommand
from imblearn.under_sampling import RandomUnderSampler
from routing.matching.features import ModelMatcher
from routing.matching.hypermodel import *
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

names = [
    "Nearest Neighbors",
    "Decision Tree",
    "Random Forest",
    "Neural Net",
    "AdaBoost",
    "Naive Bayes",
    "QDA",
    "Linear SVM",
    "RBF SVM",
]


classifiers = [
    KNeighborsClassifier(3),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=10000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis(),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        dataset_path = os.path.join(settings.BASE_DIR, "../data/ml-dataset.json.gz")
        with gzip.open(dataset_path) as f:
            byte_array = f.read()
            dataset = json.loads(byte_array.decode("utf-8"))

        y = dataset["y"]
        X = dataset["X"]

        # Since we augmented the dataset with artificial samples, we need to
        # use a non-shuffled train test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        # Undersample the majority class to balance the dataset
        X_train, y_train = RandomUnderSampler().fit_resample(X_train, y_train)

        print(f"Train dataset size: {np.bincount(y_train)}")
        print(f"Test dataset size: {np.bincount(y_test)}")

        best_f1 = 0
        best_model = None
        best_model_name = None

        for name, clf in zip(names, classifiers):
            clf.fit(X_train, y_train)

            train_f1 = f1_score(y_train, clf.predict(X_train))
            test_f1 = f1_score(y_test, clf.predict(X_test))
            train_acc = clf.score(X_train, y_train)
            test_acc = clf.score(X_test, y_test)
            tn, fp, fn, tp = confusion_matrix(y_test, clf.predict(X_test)).ravel()
            
            print(f"{name}: test_f1={test_f1:.3f}, train_f1={train_f1:.3f}, test_acc={test_acc:.3f}, train_acc={train_acc:.3f}")
            print(f"{name}: tn={tn}, fp={fp}, fn={fn}, tp={tp}")

            if test_f1 > best_f1:
                best_f1 = test_f1
                best_model = clf
                best_model_name = name

        if best_model:
            ModelMatcher.store(best_model)
            print(f"Best model: {best_model_name} with F1={best_f1:.3f}")
