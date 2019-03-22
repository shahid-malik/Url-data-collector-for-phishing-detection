import sys
from data_collection import *
from classifier.feature_extraction.FeatureEngineering import *
from classifier.classifier_v1 import *
from lib.db import *


class LoadData:

    def __init__(self):
        pass

    @staticmethod
    def load_data(data_path):
        """load dataset from given path into dataframe and return the dataframe"""
        input_data = pd.read_csv(data_path)
        return input_data


if __name__ == '__main__':

    # url = "https://www.google.com/"
    while True:

        try:
            url = api.get_url()
            url_md5 = get_md5_hash(url)

            data_dir = expanduser('~') + "/data/"

            modelObj = Model()
            model = modelObj.get_trained_model()

            data_dict = start_processing_url(url, data_dir, source='static')
            db.insert_data(data_dict)

            df = pd.DataFrame(data_dict, index=[0])

            feature_set_obj = FeatureSet()
            test_url = feature_set_obj.make_feature_set(df)

            # model = get_trained_model()
            predicted = model.predict(test_url)
            probs = model.predict_proba(test_url)

            data = {
                'verdict': predicted[0],
                'url_source': 'urlScan',
                'verdict_prob': probs,
                'url_md5': url_md5,
                'timestamp': get_current_time(),
                'clf_version': 'v1.0'

                }

            insert_verdict_data(data)

            if predicted[0] == 0:
                print("  -----  Benign with prob {}".format(probs))
            else:
                print("  -----  Malicious with prob {}".format(probs))
        except:
            pass