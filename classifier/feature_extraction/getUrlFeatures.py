from behaviouralClassifier.data_collection import *
from behaviouralClassifier.classifier.feature_extraction.FeatureEngineering import *
from behaviouralClassifier.classifier.classifier_v1 import *
from joblib import load

class LoadData:

    def __init__(self):
        pass

    @staticmethod
    def load_data(data_path):
        """load dataset from given path into dataframe and return the dataframe"""
        input_data = pd.read_csv(data_path)
        return input_data


if __name__ == '__main__':

    url = "https://www.google.com/search?q=if+using+all+scaller+values+you+must+pass+an+index&oq=if+using+all+scaller+values+you+must+pass+an+index&aqs=chrome..69i57j0l5.9687j0j7&sourceid=chrome&ie=UTF-8"
    model_path = "/home/shahid/projects/behaviouralClassifier/classifier/bcl_classifier.joblib"
    home_dir = expanduser('~')
    data_dir = home_dir + "/data/"

    data_dict = start_processing_url(url, data_dir, source='static')
    df = pd.DataFrame(data_dict, index=[0])
    feature_set_obj = FeatureSet()
    test_url = feature_set_obj.make_feature_set(df)

    # model = get_trained_model()
    model = load(model_path)
    predicted = model.predict(test_url)
    probs = model.predict_proba(test_url)

    if predicted[0] == 0:
        print("  -----  Benign with prob {}".format(probs))
    else:
        print("  -----  Malicious with prob {}".format(probs))
