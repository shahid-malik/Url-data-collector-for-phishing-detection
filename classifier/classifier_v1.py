from __future__ import division
import os
import copy
import pandas as pd
import numpy as np
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

plt.switch_backend('agg')


class Model:
    def __init__(self):
        pass

    def load_dataset(self, path):
        """ Load Dataset to pandas dataframe and return dataframe """
        url_data = pd.read_csv(path)
        return url_data

    @staticmethod
    def get_train_test_set_manual(input_data, mal_start_index, mal_end_index, ben_start_index, ben_end_index):
        """ Get train and test set from data based on indexes provided manually. """
        df_malicious = input_data.loc[input_data['verdict'] == 1]
        df_benign = input_data.loc[input_data['verdict'] == 0]

        total_mal = df_malicious.shape[0]
        total_ben = df_benign.shape[0]

        testset = pd.concat(
            [df_malicious.iloc[mal_start_index:mal_end_index, :], df_benign.iloc[ben_start_index:ben_end_index, :]])
        trainset = pd.concat(
            [df_malicious.iloc[mal_end_index + 1:total_mal, :], df_benign.iloc[ben_end_index + 1:total_ben, :]])

        return [trainset, testset]

    def save_classifier_to_disk(self, classifier):
        file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bcl_classifier.joblib')
        classifier_dump = dump(classifier, file_name)
        return classifier_dump

    def get_rf_classifier(self, features, labels):
        """ Get a trained random classifier trained on given features and labels"""
        tree = RandomForestClassifier(n_estimators=1000, max_depth=5, random_state=0)
        rf = tree.fit(features, labels)
        return rf

    def get_dt_classifier(self, input_features, labels):
        """
        Get trained decision tree classifier
        :rtype: object
        """
        tree = DecisionTreeClassifier(min_samples_split=50, random_state=0)
        dt = tree.fit(input_features, labels)
        self.save_classifier_to_disk(dt)
        return dt

    def get_trained_model(self):
        model_path = "/home/shahid/projects/behaviouralClassifier/classifier/bcl_classifier.joblib"
        model = load(model_path)
        return model

    def get_train_test_set(self, data, test_percent):
        df_malicious_a = data.loc[data['verdict'] == 1]
        df_benign_a = data.loc[data['verdict'] == 0]

        print("\nMaclisious count: **", df_malicious_a.shape)
        print("Benign count: ******", df_benign_a.shape)

        df_malicious = copy.deepcopy(df_malicious_a)
        df_benign = copy.deepcopy(df_benign_a)

        mal_y = df_malicious.pop('verdict')
        mal_x = df_malicious
        ben_y = df_benign.pop('verdict')
        ben_x = df_benign

        mal_xTrain, mal_xTest, mal_yTrain, mal_yTest = train_test_split(mal_x, mal_y, test_size=test_percent,
                                                                        random_state=0)
        ben_xTrain, ben_xTest, ben_yTrain, ben_yTest = train_test_split(ben_x, ben_y, test_size=test_percent,
                                                                        random_state=0)

        train_dataX = pd.concat([mal_xTrain, ben_xTrain])
        train_dataY = pd.concat([mal_yTrain, ben_yTrain])

        test_dataX = pd.concat([mal_xTest, ben_xTest])
        test_dataY = pd.concat([mal_yTest, ben_yTest])

        mal_test_data = pd.concat([ben_xTrain, ben_yTrain])
        print("TrainSet Count: \t ", train_dataX.shape[0], "\t TestSet Count \t:", test_dataX.shape[0])
        return [train_dataX, train_dataY, test_dataX, test_dataY]

    def get_accuracy_on_testset(self, classifier, test_x, y_test):
        """ Get classifier metrics on given testset """
        predicted = self.get_verdict(classifier, test_x)

        self.get_n_print_classifier_accuracy(predicted, y_test)
        self.get_n_print_classifier_confusion_matrix(predicted, y_test)
        self.get_n_print_classifier_metrics(predicted, y_test)

    def get_verdict(self, classifier, test_set_temp):
        predicted = classifier.predict(test_set_temp)
        return predicted

    def get_n_print_classifier_accuracy(self, predicted, y_test):
        """ Get the accuracy of the model on given predicted and true labels"""
        print("\n  Accuracy = {}".format(np.mean(predicted == y_test)))

    def get_n_print_classifier_confusion_matrix(self, predicted, y_test):
        """ Get the confusion matrix of trained model """
        confusion_matrix_dt = metrics.confusion_matrix(y_test, predicted)
        print("\n      [ {}    {} ]    ".format(str(confusion_matrix_dt[0][0]).zfill(5),
                                                str(confusion_matrix_dt[0][1]).zfill(5)))
        print("      [ {}    {} ]    ".format(str(confusion_matrix_dt[1][0]).zfill(5),
                                              str(confusion_matrix_dt[1][1]).zfill(5)))
        tn, fp, fn, tp = confusion_matrix_dt.ravel()
        print("\n  Precision of Malicious = {}".format(round(float(tp / (tp + fp)), 3)))
        print("\n  Recall of Malicious = {}".format(round(float(tp / (tp + fn)), 3)))

    def get_n_print_classifier_metrics(self, predicted, y_test):
        """ Get the classifier metrics on predicted and true labels """
        classifier_metrics = metrics.classification_report(y_test, predicted, output_dict=True)
        ben_f1_score = round(classifier_metrics['0']['f1-score'], 3)
        ben_precision = round(classifier_metrics['0']['precision'], 3)
        ben_recall = round(classifier_metrics['0']['recall'], 3)
        ben_support = round(classifier_metrics['0']['support'], 3)
        mal_f1_score = round(classifier_metrics['1']['f1-score'], 3)
        mal_precision = round(classifier_metrics['1']['precision'], 3)
        mal_recall = round(classifier_metrics['1']['recall'], 3)
        mal_support = round(classifier_metrics['1']['support'], 3)
        avg_f1_score = round(classifier_metrics['weighted avg']['f1-score'], 3)
        avg_recall = round(classifier_metrics['weighted avg']['recall'], 3)
        avg_precision = round(classifier_metrics['weighted avg']['precision'], 3)
        avg_support = round(classifier_metrics['weighted avg']['support'], 3)
        print("\n  ******************************************************************  ")
        print("                precision       recall     f1-score      support")
        print("        0       {}           {}      {}          {}".format(ben_precision, ben_recall, ben_f1_score,
                                                                           ben_support))
        print("        1       {}           {}      {}          {}".format(mal_precision, mal_recall, mal_f1_score,
                                                                           mal_support))
        print("   avg / total  {}           {}      {}          {}".format(avg_precision, avg_recall, avg_f1_score,
                                                                           avg_support))
        print("  ******************************************************************  ")

    def get_accuracy_on_testset_manual(classifier, testset):
        """ Get classifier metrics on given testset """
        test_set_temp = copy.deepcopy(testset)
        y_test = test_set_temp.pop('verdict')
        predicted = classifier.predict(test_set_temp)

        print("\n  Accuracy = {}".format(np.mean(predicted == y_test)))
        print(metrics.confusion_matrix(y_test, predicted))
        print(metrics.classification_report(y_test, predicted))

    # def get_trained_model(self):
    #     global test_set, dt_classifier
    #     data_path = "../data/final_dataset_14032019.csv"
    #     data = self.load_dataset(data_path)
    #     # train_set, test_set = get_train_test_set_manual(data, 0, 214, 0, 11995)
    #     train_set, test_set = self.get_train_test_set_manual(data, 0, 214, 0, 11995)
    #     y = train_set.pop('verdict')
    #     X = train_set
    #     dt_classifier = self.get_dt_classifier(X, y)  # type: object
    #     return dt_classifier


if __name__ == '__main__':
    data_path = "data/final_dataset_14032019.csv"
    model = Model()
    data = model.load_dataset(data_path)

    trainX, trainY, testX, testY = model.get_train_test_set(data, 0.2)
    dt_classifier = model.get_dt_classifier(trainX, trainY)  # type: object
    model.get_accuracy_on_testset(dt_classifier, testX, testY)

    # train_set, test_set = get_train_test_set_manual(data, 0, 214, 0, 11995)
    # y = train_set.pop('verdict')
    # X = train_set
    # dt_classifier = get_dt_classifier(X, y)  # type: object
    # dt_classifier = get_dt_classifier(X, y)  # type: object
    # get_accuracy_on_testset_manual(dt_classifier, test_set)
    #
