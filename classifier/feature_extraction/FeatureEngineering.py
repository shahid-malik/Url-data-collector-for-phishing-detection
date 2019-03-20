import base64
import pandas as pd
from fuzzywuzzy import fuzz
import numpy as np
from os.path import expanduser


class LoadData:

    def __init__(self):
        pass

    @staticmethod
    def load_data(data_path):
        """load dataset from given path into dataframe and return the dataframe"""
        input_data = pd.read_csv(data_path, sep=',').fillna("")
        return input_data


class FeatureExtraction:

    # def __init__(self, input_file=''):
    def __init__(self, input_data):
        """ constructor for the FeatureExtraction class """
        try:
            # self.df = pd.read_csv(input_file, sep=',').fillna("")
            self.df = input_data
            self.counter = 0
        except Exception as e_init_FeatureExtraction:
            print("Invalid parameter %s " % e_init_FeatureExtraction, "\nPlease provide valid .csv file path of data")

    def get_df(self):
        """ returns data frame """
        try:
            return self.df
        except Exception as dfException:
            print("DataFrame issue, check Exception %s" % dfException)

    def remove_attributes(self, attributes_names=None):
        """ remove unwanted attributes from data """
        try:
            self.df = self.df.drop(columns=attributes_names, axis=1)
            return self.df
        except Exception as e_remove_attributes_FeatureExtraction:
            print ("Invalid parameter %s" % e_remove_attributes_FeatureExtraction,
                   "\n Provide valid list of attribute names to remove")

    @staticmethod
    def get_base64_decoded_string(base64_string):
        """ convert base64 to url(form of string) """
        try:
            decoded_string = base64.b64decode(base64_string).decode('utf8')
            return decoded_string
        except Exception as EncodingException:
            print("Invalid Encoding:    %s" % EncodingException, "\n\nProvide base64 encoded string")

    def matching_url_domain(self, domain_og, url_og):
        """
        match url and domain, fully matches or partially
        :param domain_og: domain url outgoing domains
        :param url_og: url outgoing domains
        :return: return 0 for no match, 1 for full match and 2 for partial match
        """
        try:
            values = [len(domain_og), len(url_og)]
            index = values.index(min(values))
            # iterator = ''
            # matcher = ''
            full_match = 0
            partial_match = 0
            if index == 0:
                iterator = domain_og
                matcher = url_og
            else:
                iterator = url_og
                matcher = domain_og
            matcher_urls = self.get_base64_decoded_string(matcher)
            url_string = self.get_base64_decoded_string(iterator)
            if fuzz.ratio(url_string, matcher_urls) > 90:
                full_match += 1
                return full_match
            elif fuzz.partial_ratio(url_string, matcher_urls) > 90:
                partial_match += 2
                return partial_match
            self.counter += 1
            return full_match
        except Exception as e_matching_og_domains:
            print("Matching Unsuccessful %s" % e_matching_og_domains, "\n\n")

    @staticmethod
    def matching_md5_og_domains(domain_og, url_og):
        """
        Counts og domains match
        :param domain_og: domain url outgoing domains
        :param url_og: url outgoing domains
        :return: count of matching domains
        """
        full_match = 0
        try:
            if len(domain_og) == 0 & len(url_og) == 0:
                return full_match
            else:
                if type(domain_og) == int or type(url_og) == int:
                    return full_match
                domain_og = domain_og.split(',')
                url_og = url_og.split(',')
                values = [len(domain_og), len(url_og)]
                index = values.index(min(values))
                # iterator = list()
                # matcher = list()
                # partial_match = 0
                if index == 0:
                    iterator = domain_og
                    matcher = url_og
                else:
                    iterator = url_og
                    matcher = domain_og

                for code_64 in iterator:
                    list_matches = list(map(lambda x: x == code_64, matcher))
                    matches = np.count_nonzero(list_matches)
                    full_match += matches

                return full_match
        except Exception as e_matching_og_domains:
            print("Matching Unsuccessful %s" % e_matching_og_domains, "\n\n")

    def matching_md5_og_domains_column(self, column_name=None, new_feature=''):
            """
            Function for applying (matching_md5_og_domains) function to whole column of dataframe
            :param column_name: column names of dataframe for matching
            :param new_feature: feature name to be placed in dataframe
            :return: complete dataframe
            """
            if column_name is None:
                column_name = ['']
            first_column = self.df[column_name[0]]
            second_column = self.df[column_name[1]]
            self.df[new_feature] = map(lambda x, y: FeatureExtraction.matching_md5_og_domains(x, y), first_column,
                                       second_column)
            return self.df

    def matching_url_domain_column(self, column_name=None, new_feature=''):
        """
        Function for applying (matching_url_domain) function to whole columns of dataframe
        :param column_name: column names of dataframe for matching
        :param new_feature: feature name to be placed in dataframe
        :return: complete dataframe
        """
        try:
            first_column = self.df[column_name[0]]
            second_column = self.df[column_name[1]]
            self.df[new_feature] = map(lambda x, y: FeatureExtraction.matching_url_domain(self, x, y), first_column,
                                       second_column)
            return self.df
        except Exception as MatchingException:
            print ("Please input valid column names %s" % MatchingException)

    def convert_title_match(self):
        def convert_title_match_text_to_int(title):
            if title == 'True':
                return 1
            elif title == 'False':
                return 0
            else:
                return title

        self.df['title_match'] = self.df['title_match'].apply(convert_title_match_text_to_int)

    def create_total_favicon_ratio(self):
        def calculate_fav_ration(row):
            try:
                return row['url_total_favicon'] / float(row['domain_total_favicon'])
            except ZeroDivisionError:
                return 0

        self.df['total_favicon_ratio'] = self.df.apply(lambda row: calculate_fav_ration(row), axis=1)

    def create_total_og_domain_ratio(self):
        def calculate_og_ration(row):
            try:
                return row['url_total_og_domains'] / float(row['domain_total_og_domains'])
            except ZeroDivisionError:
                return 0

        self.df['total_og_domains_ratio'] = self.df.apply(lambda row: calculate_og_ration(row), axis=1)

    def create_total_og_links_ratio(self):
        def calculate_links_ration(row):
            try:
                return row['url_total_og_links'] / float(row['domain_total_og_links'])
            except ZeroDivisionError:
                return 0

        self.df['total_og_links_ratio'] = self.df.apply(lambda row: calculate_links_ration(row), axis=1)

    def create_url_to_uri_ratio(self):
        def calculate_url_to_uri_ratio(row):
            try:
                return row['url_length'] / float(row['uri_length'])
            except ZeroDivisionError:
                return 0

        self.df['url_ratio'] = self.df.apply(lambda row: calculate_url_to_uri_ratio(row), axis=1)

    def create_entropy_ratio(self):
        def calculate_entropy_ratio(row):
            try:
                return row['url_entropy'] / float(row['domain_entropy'])
            except ZeroDivisionError:
                return 0

        self.df['entropy_ratio'] = self.df.apply(lambda row: calculate_entropy_ratio(row), axis=1)

    def convert_url_is_html(self):
        def convert_text_to_integer(is_html):
            if is_html:
                return 1
            else:
                return 0
        self.df['url_is_html'] = self.df['url_is_html'].apply(convert_text_to_integer)
        self.df['domain_is_html'] = self.df['domain_is_html'].apply(convert_text_to_integer)

    def convert_url_content_type(self):
        self.df['url_content_type'] = self.df['url_content_type'].astype('category').cat.codes

    def convert_domain_content_type(self):
        self.df['domain_content_type'] = self.df['domain_content_type'].astype('category').cat.codes

    def convert_domain_file_type(self):
        self.df['domain_file_type'] = self.df['domain_file_type'].astype('category').cat.codes

    def convert_url_file_type(self):
        self.df['url_file_type'] = self.df['url_file_type'].astype('category').cat.codes

    def convert_verdict(self):
        self.df['verdict'] = self.df['verdict'].astype('category').cat.codes


class FeatureSet:
    def __init__(self):
        pass

    @staticmethod
    def make_feature_set(input_data=''):
        """
        make complete feature set, this fuction is to be customize according to the usage
        :param input_data: name of the file on which feature extraction is to be applied
        :return: dataframe containing feature set
        """
        try:
            feature_class = FeatureExtraction(input_data)
            removal_list = ["url_title", "domain_title", "landing_url_hash", "landing_url_base64", "timestamp"]
            if 'verdict_update_timestamp' in input_data:
                removal_list.append('verdict_update_timestamp')
            if 'domain' in input_data:
                removal_list.append('domain')
            if 'url' in input_data:
                removal_list.append('url')
            if 'source' in input_data:
                removal_list.append('source')

            feature_class.remove_attributes(attributes_names=removal_list)
            feature_class.convert_url_is_html()
            feature_class.convert_url_content_type()
            feature_class.convert_domain_content_type()
            feature_class.convert_domain_file_type()
            feature_class.convert_url_file_type()
            feature_class.convert_title_match()
            if 'verdict' in input_data:
                feature_class.convert_verdict()

            feature_class.matching_md5_og_domains_column(['domain_og_domains', 'url_og_domains'], new_feature='og_matches')
            feature_class.matching_md5_og_domains_column(['domain_favicons', 'url_favicons'], new_feature='favicon_matches')
            feature_class.matching_url_domain_column(column_name=['url_base64', 'domain_base64'],
                                                     new_feature='full_partial_match')
            final_removal_list = ['url_md5', 'domain_md5', 'url_base64', 'url_favicons', 'url_og_domains', 'domain_base64',
                                  'domain_favicons', 'domain_og_domains']

            feature_class.create_total_favicon_ratio()
            feature_class.create_total_og_domain_ratio()
            feature_class.create_total_og_links_ratio()
            feature_class.create_url_to_uri_ratio()
            feature_class.create_entropy_ratio()

            feature_class.remove_attributes(attributes_names=final_removal_list)
            df = feature_class.get_df()
            return df
        except Exception as FeatureException:
            print("Problem in %s" % FeatureException)


if __name__ == '__main__':
    try:
        home_dir = expanduser('~')
        dataset_file_path = home_dir+"/projects/behaviouralClassifier/classifier/data/labelled_data_v1.csv"
        feature_df_path = home_dir+"/projects/behaviouralClassifier/classifier/data/features_db/temp2_feature_dataset_v1_19032019.csv"
        data_packages_path = home_dir+'/data/'

        load_data_obj = LoadData()
        data = load_data_obj.load_data(dataset_file_path)
        feature_set_obj = FeatureSet()
        features_df = feature_set_obj.make_feature_set(data)

        features_df.to_csv(feature_df_path)
        print(features_df.head())

    except Exception as e:
        print("Exception in main function %s" % e)
