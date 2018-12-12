# python3 module used by clihelper to scan patterns
# this module contains various functions used to scan an input against a pattern string
#
# see https://github.com/brasspots/clihelper/tree/master for the latest version

# import stdin for pipes
from sys import stdin as standard_input

# initialise version
VERSION = "1.0"


# scan a pattern
def scan_pattern(pattern, input_list):
    """ function to match an input to a pattern
    takes:
        STR pattern - the pattern to match against in a clihelper pattern format (see DOCUMENTATION.md)
        LIST input_list - list of arguments to try and match
    gives:
        DICT matches - keys are the long name and values are True if the key is a flag or the given value if it is an argument
        DICT scan_errors - errors that occurred during the scan
    note: scan_errors have 3 string keys that map to 3 lists
        LIST missing_required - a list of all long names that are required but were not present in the input_list
        LIST missing_argument - a list of all long names that were given and pair with values in the pattern, but were supplied without a value
        LIST unknown - a list of all values in the input_list that did not match the pattern"""
    pass
