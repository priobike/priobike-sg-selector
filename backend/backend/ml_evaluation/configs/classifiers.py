from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

classifiers = {
    # "k-NN": KNeighborsClassifier(3),
    "k-NN": KNeighborsClassifier(algorithm='ball_tree', leaf_size=34, n_neighbors=12, p=1, weights='uniform'),
    # "DecisionTree": DecisionTreeClassifier(max_depth=5),
    "DecisionTree": DecisionTreeClassifier(max_depth=19, criterion='log_loss', min_samples_leaf=25, min_samples_split=25, splitter='random'),
    # "DecisionTree": DecisionTreeClassifier(max_depth=14, criterion='log_loss', min_samples_leaf=3, min_samples_split=87, splitter='best'),
    "RandomForest": RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    # "MLP":  MLPClassifier(alpha=1, max_iter=1000),
    # "MLP": MLPClassifier(alpha=0.1, max_iter=10000, activation='relu', hidden_layer_sizes=(100,), learning_rate='constant', solver='adam'),
    "MLP": MLPClassifier(alpha=0.0001, max_iter=10000, activation='relu', hidden_layer_sizes=(100,), learning_rate='constant', solver='adam'),
    "AdaBoost": AdaBoostClassifier(),
    "G-NaiveBayes": GaussianNB(),
    "QDA": QuadraticDiscriminantAnalysis(),
    "LinearSVM": SVC(kernel="linear", C=0.025),
    # "RBFSVM": SVC(gamma=2, C=1),
    "RBFSVM": SVC(gamma=1.0634265504945482, C=1.8282373630014912),
    # "RBFSVM": SVC(gamma=1.1969489017213468, C=1.2057918414397644),
}
