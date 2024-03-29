# driver.py
# File for running our experimental design.

import src.data.data_set as d
from src.networks.rbfnn import RBFNN
from src.networks.mfnn import MFNN
import math


# Gets the folds for running rbf using a certain algorithm, as these folds are stored in a file so we do not have to
# rerun our center algs.
def get_rbf_data(data_set_name, data_opener):
    data_set_name = "../rbf-data/" + data_set_name
    folds = []
    # Get set of files for each folds.
    for fold_i in range(10):
        # train, test, and center data in separate files.
        train_data = data_opener(data_set_name + "-fold-" + str(fold_i) + "-train.txt", False)
        test_data = data_opener(data_set_name + "-fold-" + str(fold_i) + "-test.txt", False)
        center_data = data_opener(data_set_name + "-fold-" + str(fold_i) + "-centers.txt", False)
        folds.append({'train': train_data, 'test': test_data, 'center': center_data})
    return folds


# Runs the RBFNN using cross validation on specific classification data set with the given parameters.
def run_rbfnn_classification(data_set_name, data_opener, classes, learning_rate, convergence_size):
    print(data_set_name)
    # Standard parameters to run on the data_set
    num_folds = 10
    folds = get_rbf_data(data_set_name, data_opener)
    fold_average = []
    # Iterate through each fold in cross validation..
    for fold_i, fold in enumerate(folds):
        test = fold['test']
        # partition the training part of the fold into a true training set AND a small validation set.
        train, validation = fold['train'].partition(.8)
        center = fold['center']
        size_inputs = len(test.attr_cols)
        # Create the network.
        rbfnn = RBFNN(center, train, validation, size_inputs, learning_rate, convergence_size, classes)
        # Train the network.
        rbfnn.train()
        # Get the accuracy on the test set.
        fold_accuracy = rbfnn.get_accuracy(test)
        fold_average.append(fold_accuracy)
        print("\t Fold: " + str(fold_i + 1) + " - Accuracy: " + str(fold_accuracy))
    # Show average accuracy across all folds.
    print("Average Accuracy: " + str(sum(fold_average) / num_folds))


# Runs the RBFNN using cross validation on specific regression data set with the given parameters.
def run_rbfnn_regression(data_set_name, data_opener, learning_rate, convergence_size):
    print(data_set_name)
    # Standard parameters to run on the data_set
    num_folds = 10
    folds = get_rbf_data(data_set_name, data_opener)
    fold_average = []
    # Iterate through each fold in cross validation.
    for fold_i, fold in enumerate(folds):
        test = fold['test']
        # partition the training part of the fold into a true training AND a small validation set.
        train, validation = fold['train'].partition(.8)
        center = fold['center']
        size_inputs = len(test.attr_cols)
        # Create the newtork.
        rbfnn = RBFNN(center, train, validation, size_inputs, learning_rate, convergence_size)
        # Train the network.
        rbfnn.train()
        # Get the accuracy on the test set.
        fold_error = rbfnn.get_error(test)
        fold_average.append(fold_error)
        print("\t Fold: " + str(fold_i + 1) + " - Error: " + str(fold_error))
    # Show average accuracy across all folds.
    print("Average Error: " + str(sum(fold_average) / num_folds))


# Runs the MFNN using cross validation on specific classification data set with the given parameters.
def run_mfnn_classification(data_set, classes, learning_rate, momentum, convergence_size):
    print(data_set.filename)
    # Standard parameters to run on the data_set
    num_folds = 10
    size_inputs = len(data_set.attr_cols)
    # Want to examine 0, 1, and 2 hidden layers.
    num_hidden_layers = [0, 1, 2]
    size_outputs = len(classes)
    # The size of the hidden layers is the average between the size of inputs and outputs.
    size_hidden_layers = math.floor((size_inputs + size_outputs) / 2)
    folds = data_set.validation_folds(num_folds)
    # Iterate over all the number of hidden layers we need to try.
    for hidden_layer in num_hidden_layers:
        # Setup the layer sizes into a list.
        layers = [size_inputs] + ([size_hidden_layers] * hidden_layer) + [size_outputs]
        print("Network " + str(layers))
        fold_average = []
        # Iterate through each fold in cross validation.
        for fold_i, fold in enumerate(folds):
            test = fold['test']
            # partion the training part of the fold into a true training set AND a small validation set.
            train, validation = fold['train'].partition(.8)
            print(layers)
            # Create the network.
            mfnn = MFNN(train, validation, layers, learning_rate, momentum, convergence_size, classes)
            # Train the network/
            mfnn.train()
            # Get the accuracy on the test set.
            fold_average.append(mfnn.get_accuracy(test))
            print("\t Fold: " + str(fold_i+1) + " - Accuracy: " + str(mfnn.get_accuracy(test)))
        print("Average Accuracy: " + str(sum(fold_average) / num_folds))


# Runs the MFNN using cross validation on specific regression data set with the given parameters.
def run_mfnn_regression(data_set, learning_rate, momentum, convergence_size):
    print(data_set.filename)
    num_folds = 10
    size_inputs = len(data_set.attr_cols)
    # Want to examine 0, 1, and 2 hidden layers.
    num_hidden_layers = [0, 1, 2]
    # Size of the hidden layers (num nodes) is the average of the input and output size.
    size_hidden_layers = math.floor((size_inputs + 1) / 2)

    folds = data_set.validation_folds(num_folds)
    # Iterate over all the number of hidden layers we need to try.
    for hidden_layers in num_hidden_layers:
        # Setup the layer sizes into a list.
        layers = [size_hidden_layers] * (hidden_layers + 2)
        layers[0], layers[-1] = size_inputs, 1
        print("Network " + str(layers))
        fold_average = []
        # Iterate through each fold in cross validation.
        for fold_i, fold in enumerate(folds):
            test = fold['test']
            # Partion the training part of the fold into a true training set AND a small validation set.
            train, validation = fold['train'].partition(.8)
            # Create the network.
            mfnn = MFNN(train, validation, layers, learning_rate, momentum, convergence_size, None)
            # Train the network.
            mfnn.train()
            # Get the accuracy on the test.
            fold_average.append(mfnn.get_error(test))
            print("\t Fold: " + str(fold_i+1) + " - Error: " + str(mfnn.get_error(test)))
        print("Average Error: " + str(sum(fold_average)/num_folds))


# Runs the RBFNN on each classification data set, using the specified algorithm for getting center vectors.
def run_rbfnn_classification_data_sets(center_alg_name):
    abalone_classes = [float(i) for i in range(1, 30)]
    car_classes = ["unacc", "acc", "good", "vgood"]
    segmentation_classes = ["BRICKFACE", "SKY", "FOLIAGE", "CEMENT", "WINDOW", "PATH", "GRASS"]

    run_rbfnn_classification("abalone-" + center_alg_name, d.get_abalone_data, abalone_classes, 1, 10)
    run_rbfnn_classification("car-" + center_alg_name, d.get_car_data, car_classes, 1, 10)
    run_rbfnn_classification("segmentation-" + center_alg_name, d.get_segmentation_data, segmentation_classes, 1, 30)


# Runs the RBFNN on each regression data set, using the specified algorithm for getting center vectors.
def run_rbfnn_regression_data_sets(center_alg_name):
    run_rbfnn_regression("forestfires-" + center_alg_name, d.get_forest_fires_data, 1, 100)
    run_rbfnn_regression("machine-" + center_alg_name, d.get_machine_data, .1, 100)
    run_rbfnn_regression("winequality-" + center_alg_name, d.get_wine_data, 1, 20)


# Runs the MFNN on each classification data set.
def run_mfnn_classification_data_sets():
    abalone_data = d.get_abalone_data("../data/abalone.data")
    abalone_classes = [float(i) for i in range(1, 30)]
    car_data = d.get_car_data("../data/car.data")
    car_classes = ["unacc", "acc", "good", "vgood"]
    segmentation_data = d.get_segmentation_data("../data/segmentation.data")
    segmentation_classes = ["BRICKFACE", "SKY", "FOLIAGE", "CEMENT", "WINDOW", "PATH", "GRASS"]

    run_mfnn_classification(abalone_data, abalone_classes, 1, .1, 100)
    run_mfnn_classification(car_data, car_classes, 1, .1, 100)
    run_mfnn_classification(segmentation_data, segmentation_classes, 1, .1, 100)


# Runs the MFNN on each regression data set.
def run_mfnn_regression_data_sets():
    forest_fires_data = d.get_forest_fires_data("../data/forestfires.data")
    machine_data = d.get_machine_data("../data/machine.data")
    wine_data = d.get_wine_data("../data/winequality.data")

    run_mfnn_regression(forest_fires_data, 1, 0.1, 100)
    run_mfnn_regression(machine_data, 1, 0.1, 100)
    run_mfnn_regression(wine_data, 1, 0.1, 100)


# Runs each set of regression and classification for the different data sets and configurations.
def main():
    run_mfnn_regression_data_sets()
    run_mfnn_classification_data_sets()

    run_rbfnn_regression_data_sets("eknn")
    run_rbfnn_classification_data_sets("eknn")

    run_rbfnn_regression_data_sets("kmeans")
    run_rbfnn_classification_data_sets("kmeans")

    run_rbfnn_regression_data_sets("pam")
    run_rbfnn_classification_data_sets("pam")

main()
