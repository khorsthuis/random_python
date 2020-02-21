"""
This file contains the class that hold the methods that handle the interaction with CLI and the
returning of the output thereof
"""

import subprocess
import helper_functions
import os


class Interact(helper_functions.HelperFunctions):
    """
    This class (subclass of "HelperFunctions" contains all the methods that interact with the Google Gcloud SDK
    This class is a singleton class as to not have multiple commands running at the same time. Running multiple
    commands at the same time (even when they execute in different sessions) are likely to cause "racing conditions"
    """
    __instance = None

    @staticmethod
    def get_instance():
        """
        This method returns the single object of Interact that can exist
        :return: the single instance of the object Interact.
        """
        if Interact.__instance is None:
            Interact()
        return Interact.__instance
    
    def __init__(self):
        """
        Constructor method for singleton class setting __ instance to self
        """
        if Interact.__instance is not None:
            raise Exception("This is a Singleton class!")
        else:
            Interact.__instance = self

    def gcp_login(self):
        """
        Method that logs in using the browser popup to log-in a user-account if no account is active.
        This method will keep calling itself until a user-account has been found.
        :return: True when an account has been found
        """
        check_login = ["gcloud", "auth", "list"]
        process1 = subprocess.Popen(check_login, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output1 = process1.communicate()[0].decode("utf-8")  # first index of tuple decoded byte > string
        if len(output1) > 0:
            return True
        else:
            print("Please login using browser or follow the link below")
            do_login = ["gcloud", "auth", "login"]
            process2 = subprocess.Popen(do_login, stdout=subprocess.PIPE)
            process2.communicate()
            return self.gcp_login()

    def run_command(self, command_list, terminal_out=False):
        """
        Method that returns the output of a cli command as a string
        :param command_list: the list that forms the command to be executed
        :param terminal_out: optional parameter to indicate if the error message is to be returned
        :return: string with the resulting output of the command
        """
        # Check that command list contains only strings and check login
        self.check_are_string_lists(command_list)
        self.gcp_login()

        # conditional to set shell=True for non-posix systems
        shell_var = os.name != "posix"

        helper_functions.HelperFunctions.check_are_string_lists(command_list)
        if terminal_out:  # the terminal return is requested to show
            p = subprocess.Popen(command_list, shell=shell_var, stdout=subprocess.PIPE)
        else:  # suppress the error message
            p = subprocess.Popen(command_list, shell=shell_var, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o = p.communicate()
        return o[0].decode("utf-8")

    def run_command_raw(self, command_list):
        """
        Method that runs a terminal command but does not format the output in any way
        :param command_list: the list containing the commands that is to be ran
        :return: the raw output of the subprocess.communicate()
        """
        # Check that command list contains only strings
        self.check_are_string_lists(command_list)

        # conditional to set shell=True for non-posix systems
        shell_var = os.name != "posix"

        o = subprocess.Popen(command_list, shell=shell_var, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return o.communicate()
