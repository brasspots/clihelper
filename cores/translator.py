# python3 module used by clihelper to translate flags into long names
# this module contains various functions used to translate strings and patterns into a long name only form
#
# see https://github.com/brasspots/clihelper/tree/master for the latest version

# initialise version
VERSION = "1.1"


# translate flags in string into full names
def flag_translate(string, mapping):
    """replaces all flags with their long names according to mapping
    takes:
        STR string - the string to translate
        DICT mapping - the non-prefixed flags to long names dictionary
    gives:
        STR string - the translated string"""

    # iterate over every flag to replace all instances of it
    for flag in mapping:

        # replace all instances of flag
        while flag in string and string[string.find(flag) + 2] == " " and string[string.find(flag) - 1] == " ":
            string.replace(flag, mapping[flag])

    # return the translated string
    return string


# translate a pattern string into a usable pattern string
def full_translate(string, parameters):
    """replaces all flags with long names and expands [OPTIONS]
    takes:
        STR string - the string to translate
        LIST parameters - a list containing parameter objects
    gives:
        STR translated - the translated string"""

    # create a list of long names for options expansion
    long_name_list = [obj.long_name for obj in parameters]

    # replace flags with long names
    translated = flag_translate(string, {obj.flag: obj.long_name for obj in parameters})

    # expand options
    if "[OPTIONS]" in translated:

        # initialise replacement string (space as last character will be stripped)
        replacement_string = " "

        # iterate over long names to check if it is present in the pattern
        for name in long_name_list:
            # check if name is not in pattern followed by a space
            if not (name in translated and translated[translated.find(name) + len(name)] == " "):

                # add control prefixes to long name required by first finding prefix
                for obj in parameters:
                    if name == obj.long_name and obj.value_type != "<BOOL>":

                        # add control prefix
                        replacement_string += "#" if obj.value_type[0] != "*" else "*"
                        break

                # add name to replacement string
                replacement_string += name + " "

        # strip last character of replacement string
        replacement_string = replacement_string[:-1]

        # add optional tokens only if there are names in replacement string
        if replacement_string:
            replacement_string = "[ " + replacement_string + " ]"

        # actually do the replacement
        translated.replace("[OPTIONS]", replacement_string)

        # return the translated string
        return translated


# translate a pattern string into a displayable pattern string
def display_translate(string, parameters):
    """replaces all control flags with readable flags and squishes spaces
    takes:
        STR string - the string to translate
        LIST parameters - a list containing parameter objects
    gives:
        STR translated - the translated string"""

    # initialise translated
    translated = ""

    # split up pattern string into tokens and remove opening and closing brackets
    tokens = string[2:-2].split()

    # iterate over tokens to add them to translated
    for token_index in range(len(tokens)):

        # add regular control characters to translated
        if tokens[token_index] in ("{", "}", "[", "]", "|"):
            translated += tokens[token_index]

        # add regular flags and long names to translated
        else:
            # check for a prefix
            if tokens[token_index][0] in ("*", "#"):

                # add flag or long name without prefix to translated
                translated += tokens[token_index][1:]

                # find parameter with flag or long name equal to token
                for obj in parameters:
                    if tokens[token_index][1:] in (obj.flag, obj.long_name):
                        # add value_type to translated
                        translated += " " + obj.value_type
                        break

            # add regular token
            else:
                translated += tokens[token_index]

            # add space separator unless next token is a closing control character
            if token_index != len(tokens) + 1 and tokens[token_index + 1] not in ("|", "}", "]"):
                translated += " "

    # return translated string
    return translated
