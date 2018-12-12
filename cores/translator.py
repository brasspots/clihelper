# python3 module used by clihelper to translate flags into long names
# this module contains various functions used to translate strings and patterns into a long name only form
#
# see https://github.com/brasspots/clihelper/tree/master for the latest version

# initialise version
VERSION = "1.0"

# translate values in string
def translate(string, mapping, strict=True):
    """replaces all flags with their long names according to mapping
    takes:
        STR string - the string to translate
        DICT mapping - the flags to long names dictionary
        BOOL strict - whether to throw an error if a flag is not in the mapping or not
    gives:
        STR - the translated string"""
    pass