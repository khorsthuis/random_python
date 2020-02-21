"""
This file contains the class tha holds the helper-functions for the automated deployment of
infrastructure on GCP
"""
import json
import yaml


class HelperFunctions:
    """
    Class that contains the methods that aid in the functioning of the
    Interaction methods contained in the Interact class
    """
    def check_are_strings(self, *args):
        """
        Method that checks all it arguments to be string. If one is not string a value-error wil be raised
        :return True when all arguments are strings
        """
        for ar in args:
            if not isinstance(ar, str):
                raise ValueError("Parrameter {} should be string but is of type {}".format(ar, type(ar)))

    def check_are_bool(self, *args):
        """
        Method that checks all it arguments to be Boolean. If one is not a bool, a value-error wil be raised
        :return True when all arguments are booleans
        """
        for ar in args:
            if not isinstance(ar, bool):
                raise ValueError("Parameter {} should be a boolean but is of type {}".format(ar, type(ar)))

    def check_are_string_lists(self, *args):
        """
        Method that checks that all the arguments that are passed are of type list and that their
        contents are of type string
        :return True when all arguments are lists with strings
        """
        for ar in args:
            if not isinstance(ar, list):
                raise ValueError("Parameter {} should be a list but is of type {}".format(ar, type(ar)))
            else:
                for element in ar:
                    if not isinstance(element, str):
                        raise ValueError("Contents of list should be strings only")

    def json_string_to_dict(self, json_string):
        """
        Method that takes in a json formatted string and returns a hashmap style dictionary
        :param json_string: json-style formatted string
        :return: dictionary formed from the json string
        """""
        self.check_are_strings(json_string)
        return json.loads(json_string)

    def yaml_string_to_dict(self, yaml_string):
        """
        Method that takes in a YAML formatted string and returns a hashmap style dictionary
        :param yaml_string: yaml-style formatted string
        :return: dictionary formed from the yaml string
        """""
        self.check_are_strings(yaml_string)
        return yaml.load(yaml_string, Loader=yaml.BaseLoader)

    def dict_to_yaml_string(self, yaml_dict):
        """
        Method that converts a python dictionary to a yaml-formated string
        :param yaml_dict: Dict that is to be converted
        :return: a yaml-formatted string
        """
        return yaml.dump(yaml_dict)

