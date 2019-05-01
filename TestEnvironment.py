import numpy as np
import pandas as pd
from datetime import datetime
import os
import json

from functions.evaluation import *

__all__ = [
    "TestEnvironment"
]


class TestEnvironment:
    def __init__(self, tests_root_dir="./test/"):
        self.__tests_root_dir = tests_root_dir

        if self.__tests_root_dir[-1] != '/':
            self.__tests_root_dir += '/'

        if not os.path.exists(tests_root_dir):
            print("Path does not exist!")

        self.__model = None

    def set_model(self, model):
        self.__model = model

    def evaluate(self, X_test, y_true, is_classification=True, is_one_hot_encoded=False, show_results=True, save_results=True, title="", dataset_name=""):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        path = self.__tests_root_dir + timestamp + '/'
        os.mkdir(path)

        y_pred = self.__model.predict(X_test)

        if is_one_hot_encoded:
            y_pred = np.argmax(y_pred, axis=1)
            y_true = np.argmax(y_true, axis=1)

        metrics = evaluate_result(y_true=y_true, y_pred=y_pred)

        # show metrics
        if show_results:
            for key in metrics:
                print(key + ":", metrics[key], '%')
            print()

        if is_classification:
            plot_confusion_matrix(y_true, y_pred, title=title, show_fig=show_results, save_fig=save_results, filename=path + "cm.png")
            plot_confusion_matrix(y_true, y_pred, normalize=True, title=title, show_fig=show_results, save_fig=save_results, filename=path + "cm_normalized.png")

        if save_results:
            # save model architecture
            try:
                model_json = self.__model.to_json()
                with open(path + 'model.json', 'w') as file:
                    json.dump(model_json, file)
            except AttributeError:
                pass  # no such repr - ignore

            use_header = not os.path.exists(self.__tests_root_dir + "results.csv")

            # save metrics
            with open(self.__tests_root_dir + "results.csv", 'a') as file:
                metrics.update({"timestamp": timestamp, "title": title, "dataset": dataset_name})
                df = pd.DataFrame(metrics, index=[0])
                df.to_csv(file, index=False, header=use_header)

    def fit(self, *args, **kwargs):
        self.__model.fit(*args, **kwargs)
