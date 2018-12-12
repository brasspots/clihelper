# python3 module for Linux command line programs
# this module provides most the boilerplate code for command line python scripts including:
#   - help message
#   - bad usage messages
#   - automatic argument parsing
#   - automatic file handling
#
# Note: This does not replace sys for accessing command line arguments
# It only makes syntax checking the arguments easier
#
# see https://github.com/brasspots/clihelper/tree/master for the latest version

# import stderr
from sys import stderr as standard_error
# import os.path
from os import path as path_check
# import type checks
from cores import checker, parser, translator

# initialise version
VERSION = "2.0"


# parameter class
class Parameter:
    # parameter constructor
    def __init__(self, flag_alias, long_name, description, value, value_type):
        """initialises a parameter
        takes:
            STR flag_alias - the short name for the parameter
            STR description - the description of the parameter to be displayed in the help entry
            STR value - the current value of the parameter as a string
            STR value_type - the type the value should be in the format '<TYPE>', used by the type checker
        gives:
            None"""

        # copy arguments into local namespace
        self.flag = flag_alias
        self.long_name = long_name
        self.description = description
        self.value = value
        self.value_type = value_type

    # assert that current value is the correct type
    def assert_type(self, strict=False):
        """checks that the current value matches the parameters type using cores/checker.py
        takes:
            BOOL strict - whether to throw an error if self.type_value is not in cores/checker.py's type dictionary
        gives:
            BOOL - True if the type matches, otherwise False"""

        # check if value_type is iterable
        if self.value_type[0] == "*":
            # check all values against checker function
            return type(self.value) == list and all(checker.type_dict.get(self.value_type, (lambda x: not strict))(value) for value in self.value)

        # otherwise run the checker function once
        else:
            # return boolean from checker
            return checker.type_dict.get(self.value_type, (lambda x: not strict))(self.value)


# interface class
class Interface:
    # initialise control characters
    control_characters = (" ", "|", "{", "}", "[", "]")

    # interface constructor
    def __init__(self, script_name, short_description, long_description, pattern_tree, parameter_information):
        """initialises interface
        takes:
            STR script_name - the name of the script (usually sys.argv[0])
            STR short_description - a brief description of the program to be shown at the top of the help message
            STR long_description - a more in-depth description to be shown at the bottom of the help message
            DICT pattern_tree - a dictionary of patterns to use keyed using sub commands
            ITER parameter_information - list of information about parameters in the format [flag, long name, description, default_value, value_type]
        gives:
            None
        note: each entry in parameter_information must have a long name, value_type and description are recommended and flag and default_value are completely optional
        note: any blank entry should be represented as an empty string"""

        # copy arguments into local namespace
        self.script_name = script_name
        self.short_description = short_description
        self.long_description = long_description
        self.pattern_tree = pattern_tree

        # initialise parameters dict to map long names to parameter objects
        self.parameters = []
        # initialise current working path to keep track of where we are in the pattern tree
        self.current_working_path = self.script_name
        # iterate over parameter information to assert formatting and add to self.parameters
        for parameter in parameter_information:

            # assert there are 5 values for the parameter
            if len(parameter) != 5 or any(type(value) != str for value in parameter):
                raise ValueError("Parameter is not valid. It must consist of exactly 5 strings, use an empty string to represent None")

            # assert flag is correctly formatted
            if parameter[0] != "" and (parameter[0][0] != "-" or len(parameter[0]) != 2 or parameter[0][1] in Interface.control_characters + ("-",)):
                raise ValueError("Flag '" + parameter[0] + "' is not valid. It must be a dash followed by a single, non-control character")

            # assert long name is correctly formatted
            if (not parameter[1].startswith("--")) or len(parameter[1]) < 3 or "--" in parameter[1][1:] or any(character in parameter[1] for character in Interface.control_characters):
                raise ValueError("Long name '" + parameter[1] + "' is not valid. It must be a label starting with '--' followed by any number of non-control characters")

            # assert long name is unique
            if parameter[1] in self.parameters:
                raise ValueError("Long name '" + parameter[1] + "' is a duplicate")
            # assert flag is unique
            elif parameter[0] in [obj.flag for obj in self.parameters]:
                raise ValueError("Flag '" + parameter[0] + "' is a duplicate")
            else:
                # add parameter to self.parameters
                self.parameters.append(Parameter(parameter[0], parameter[1], parameter[2], parameter[3], parameter[4]))

    # parse given arguments
    def parse(self, given_arguments, assert_typing=True):
        """match a list of given inputs to a pattern
        takes:
            LIST given_arguments - the arguments to match to a pattern, should be sys.argv
            BOOL assert_typing - whether to error on a type mismatch according to cores/checker.py
        gives:
            DICT - every possible long name as the key and its value as the value"""
        pass

    # display an error
    def display_error(self, message, error_code=-1):
        """displays error message to the user, via stderr then exit
        takes:
            STR message - the error to display to the user
            INT error_code - the error code to exit with
        gives:
            None"""

        # print error
        print(self.current_working_path + ": " + message + "\n\tTry '" + self.current_working_path + " --help' for more information", file=standard_error)
        # exit with error code
        exit(error_code)

    # display the help message
    def display_help(self):
        """displays information and usage patterns to user
        takes:
            None
        gives:
            None"""
        pass

    # open a file
    def open_file(self, path, mode):
        """wrapper for open() but checks for permissions, existing files and handles errors
        takes:
            STR path - the path to the file
            STR mode - the file will be opened in this mode
        gives:
            child of io.IOBase - the file object, the same thing returned from open() with the specified mode"""
        pass
