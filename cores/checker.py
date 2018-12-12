# python3 module used by clihelper to type check
# this module contains various functions to assert that the type of a given argument is correct
#
# to create a custom type write a function that takes 1 value
# this is the value that will be checked
# it should return a boolean, True matches the type criteria, False if otherwise
# then add your new type check to the type dictionary at the bottom of the file
# the key must be the angle brace wrapped identifier and the value must be the name of your function
#
# Note: the type checking supported in clihelper does not cast the given value to the type
# you will still receive a string for the value of arguments
#
# see https://github.com/brasspots/clihelper/tree/master for the latest version

# initialise version
VERSION = "1.1"


# check integer
def check_int(value):
    """asserts a given value is a valid integer
    takes:
        STR value - the value to check
    gives:
        BOOL - true if the value is a valid integer, otherwise false"""
    return all(character.isdigit() for character in value)


# check float
def check_float(value):
    """asserts a given value is a valid float
    takes:
        STR value - the value to check
    gives:
        BOOL - true is the value is a valid float, otherwise false
    note: this is a strong check so integers will be rejected"""
    return all(character.isdigit() or character == "." for character in value) and "." in value


# check hexadecimal
def check_hex(value):
    """asserts a given value is valid hexadecimal
    takes:
        STR value - the value to check
    gives:
        BOOL - true is the value is valid hexadecimal, otherwise false"""
    return all(character.upper() in tuple(chr(dec) for dec in range(48, 58)) + tuple(chr(dec) for dec in range(65, 71)) for character in value)


# check octal
def check_oct(value):
    """asserts a given value is valid octal
    takes:
        STR value - the value to check
    gives:
        BOOL - true is the value is valid octal, otherwise false"""
    return all(character in (chr(dec) for dec in range(48, 56)) for character in value)


# check binary
def check_bin(value):
    """asserts a given value is valid binary
    takes:
        STR value - the value to check
    gives:
        BOOL - true is the value is valid binary, otherwise false"""
    return all(character in ("0", "1") for character in value)


# check boolean
def check_bool(value):
    """asserts a given value is valid boolean
        takes:
            STR value - the value to check
        gives:
            BOOL - true is the value is valid boolean, otherwise false"""
    return value in (True, False)

# initialise type dictionary
type_dict = {"<INT>": check_int,
             "<FLOAT>": check_float,
             "<HEX>": check_hex,
             "<OCT>": check_oct,
             "<BIN>": check_bin}