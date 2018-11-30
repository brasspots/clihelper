# python3 module for Linux command line programs
# this module provides most the boilerplate code for command line python scripts including:
#   - help message
#   - bad usage messages
#   - automatic flag handling
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
import type_check
# initialise version
VERSION = "1.4"


# interface class
class Interface:
    # interface constructor
    def __init__(self, script_name, script_description, long_description, pattern_tree, parameter_information):
        """initialises interface
        takes:
            STR script_name - the name of the script (usually sys.argv[0])
            STR script_description - a brief description of the program to be shown at the top of the help message
            STR long_description - a more in-depth description to be shown at the bottom of the help message
            DICT pattern_tree - a dictionary of patterns to use keyed using sub commands
            ITER parameter_information - list of information about parameters in the format [flag, description, default_value]
        gives:
            None"""
        # copy variables into local namespace
        self.script_name = script_name
        self.script_description = script_description
        self.long_description = long_description
        self.pattern_tree = pattern_tree
        self.parameter_information = parameter_information
        # initialise current internal command path
        self.internal_command_path = []
        # initialise argument results, argument scan an given arguments
        self.argument_results = []
        self.argument_scan = []
        self.given_arguments = []

    # unpack command path into a string
    def unpack_command_path(self, given_path):
        """unpacks a path into a string for printing
        takes:
            ITER given_path - a list containing the path elements
        gives:
            STR string_path - the internal command path as a string"""
        # initialise string path
        string_path = given_path[0]
        # add path element to string path
        for command in given_path[1:]:
            string_path += " " + command
        # return string path
        return string_path

    # unpack pattern tree into list
    def unpack_pattern_tree(self, given_pattern):
        """recursively unpacks a pattern into a list of possible patterns
        takes:
            DICT given_pattern - a tree of the patterns to unpack
        gives:
            ITER pattern_list - a list of all possible patterns"""
        # initialise pattern list
        pattern_list = []
        # iterate over pattern keys
        for key in given_pattern:
            # if content is a pattern
            if type(given_pattern[key]) == str:
                # add pattern to pattern list
                pattern_list.append(key + " " + given_pattern[key])
            # if content is a sub tree
            else:
                # recurse
                pattern_list += [key + " " + pattern for pattern in self.unpack_pattern_tree(given_pattern[key])]
        # return the pattern list
        return pattern_list

    # display a help message to the user
    def display_help(self):
        """displays information and usage patterns to user
        takes:
            None
        gives:
            None"""
        # acquire target patterns
        target_patterns = self.pattern_tree
        for command in (self.internal_command_path if self.internal_command_path else [self.script_name]):
            target_patterns = target_patterns[command]
        # unpack pattern sub tree
        if type(target_patterns) == dict:
            target_patterns = self.unpack_pattern_tree(target_patterns)
        else:
            target_patterns = [target_patterns]
        # unpack internal command path
        caller_address = self.unpack_command_path(self.internal_command_path if self.internal_command_path else [self.script_name])
        # print usage header
        usage_message = "Usage: " + caller_address + " "
        print(usage_message + target_patterns[0])
        # print additional patterns if applicable
        for pattern in target_patterns[1:]:
            print(" " * len(usage_message) + pattern)
        # print out short description
        print("\n" + self.script_description + "\n")
        # construct flag information
        present_arguments = []
        for pattern in target_patterns:
            # look at each argument in the pattern
            for argument in pattern.split(" "):
                # remove all control characters
                for character in ["[", "]", "{", "}", "|"]:
                    argument = argument.replace(character, "")
                # skip input values
                if argument.startswith("<"):
                    continue
                # add flag to present flags
                else:
                    present_arguments.append(argument)
        # print out argument information
        if present_arguments:
            # initialise columns
            columns = [[], [], [], []]
            for information in self.parameter_information:
                if information[0] in present_arguments:
                    # add values to columns
                    for value_index in range(len(information)):
                        columns[value_index].append(information[value_index])
            # initialise max widths
            max_widths = []
            # add headers
            for column_index in range(len(columns)):
                # if the column is used
                if any(columns[column_index]):
                    # add the header
                    columns[column_index] = [{0:"ARGUMENT", 1:"VALUE", 2:"DESCRIPTION", 3:"DEFAULT VALUE"}[column_index]] + columns[column_index]
                    # add to max widths
                    max_widths.append(max([len(value) for value in columns[column_index]]))
                # set the column to unused
                else:
                    max_widths.append(0)
            # print out columns
            print("Argument Information:\n")
            for row_index in range(len(columns[0])):
                # start row
                print("\t", end="")
                for column_index in range(len(max_widths)):
                    # skip unused columns
                    if max_widths[column_index] == 0:
                        continue
                    # print out padded string
                    else:
                        print(columns[column_index][row_index].ljust(max_widths[column_index], " "), end="    ")
                # end row with newline
                print()
        # print long description
        if self.long_description:
            print("\n" + self.long_description + "\n")
        else:
            print()

    # display error to user
    def display_error(self, message):
        """displays error message to the user
        takes:
            STR message - the error to display to the user
        gives:
            None"""
        # unpack internal command path
        caller_address = self.unpack_command_path(self.internal_command_path if self.internal_command_path else [self.script_name])
        # print message to standard error
        print(caller_address + ": " + message + "\n\tTry: '" + caller_address + " --help' for more info", file=standard_error)

    # scan pattern
    def scan_pattern(self, pattern, depth, parent):
        """recursively scans the arguments to match to pattern and updates argument_results with the findings
        takes:
            STR pattern - the pattern to match against
        gives:
            ITER - a list of all present flags"""
        # get element mode and strip brackets
        mode = pattern[0]
        pattern = pattern[1:-1]
        pattern_parts = pattern.split(" ")
        # sanitise mode
        if mode not in ("{", "["):
            raise SyntaxError("Mode for pattern " + pattern + " is not valid")
        # run the base case
        if (len(pattern_parts) == 1 or (len(pattern_parts) == 2 and pattern_parts[1][0] == "<")) and all("|" not in part for part in pattern_parts):
            # check if pattern part is in arguments
            if pattern_parts[0] in self.given_arguments:
                # set up value to append
                if len(pattern_parts) == 2:
                    try:
                        value_index = self.given_arguments.index(pattern_parts[0]) + 1
                        append_value = self.given_arguments[value_index]
                        # remove that value from given arguments
                        self.given_arguments = self.given_arguments[:value_index] + self.given_arguments[value_index + 1:]
                        # detect missing argument
                        if append_value.startswith("-"):
                            raise IndexError()
                    except IndexError:
                        self.display_error("Missing argument for flag " + pattern_parts[0])
                        exit(1)
                    # detect correct typing
                    if self.assert_typing and pattern_parts[1] in type_check.type_dict and not type_check.type_dict[pattern_parts[1]](append_value):
                        # alert the user to bad type
                        self.display_error("Incorrect type for " + pattern_parts[0])
                        exit(1)
                else:
                    append_value = True
                # remove flag from given arguments
                self.given_arguments.remove(pattern_parts[0])
                # add result to results collection
                self.argument_results.append((pattern_parts[0], append_value))
                return [pattern_parts[0]]
            # detect unassigned value
            elif pattern_parts[0].startswith("<") and (depth == 1 or (depth == 0 and len(pattern_parts) == 1)):
                try:
                    # remove the unassigned value
                    append_value = self.given_arguments.pop()
                    # detect missing argument
                    if append_value.startswith("-"):
                        raise IndexError()
                except IndexError:
                    self.display_error("Missing argument " + pattern_parts[0])
            # add default values
            else:
                # set up append value
                append_value = self.parameter_information[[entry[0] for entry in self.parameter_information].index(pattern_parts[0])][2]
                if not append_value:
                    append_value = False
                # add result to results collection
                self.argument_results.append((pattern_parts[0], append_value))
                return ["-*"] if mode == "[" else []
        # run the recursion
        else:
            # get elements
            pattern_parts = []
            match_character = ""
            base_pointer = 0
            for current_pointer in range(len(pattern)):
                # detect open bracketed element
                if pattern[current_pointer] in ("{", "[") and not match_character:
                    # update match character
                    match_character = {"{": "}", "[": "]"}[pattern[current_pointer]]
                    # cycle base pointer
                    while pattern[base_pointer] in (" ", "}", "]"):
                        base_pointer += 1
                    # add current scanned element to pattern parts
                    if pattern[base_pointer:current_pointer]:
                        pattern_parts.append(pattern[base_pointer:current_pointer])
                    # update base pointer
                    base_pointer = current_pointer
                # detect close bracketed element
                elif pattern[current_pointer] == match_character:
                    # update match character
                    match_character = ""
                    # add current scanned element to pattern parts
                    if pattern[base_pointer:current_pointer + 1]:
                        pattern_parts.append(pattern[base_pointer:current_pointer + 1])
                    # update base pointer
                    base_pointer = current_pointer
                # detect end of element
                elif not match_character and pattern[current_pointer] == " " and current_pointer != len(pattern) - 1 and pattern[current_pointer + 1] != "<":
                    # cycle base pointer
                    while pattern[base_pointer] in (" ", "}", "]") and base_pointer < current_pointer:
                        base_pointer += 1
                    # add current scanned element to pattern parts
                    if pattern[base_pointer:current_pointer]:
                        pattern_parts.append(pattern[base_pointer:current_pointer])
                    # update base pointer
                    base_pointer = current_pointer
            # last cycle of base pointer
            while base_pointer <= current_pointer and pattern[base_pointer] in (" ", "}", "]"):
                base_pointer += 1
            # add final scanned element to pattern parts
            if pattern[base_pointer:]:
                pattern_parts.append(pattern[base_pointer:])
            # reset base pointer and initialise to pipe and pipe parts
            base_pointer = 0
            to_pipe = ""
            pipe_parts = []
            # detect pipes
            for current_pointer in range(len(pattern_parts)):
                if "|" in pattern_parts[current_pointer] and pattern_parts[current_pointer][0] not in ["{", "["]:
                    # split pattern part into pipe parts
                    pipe_split = pattern_parts[current_pointer].split("|")
                    # add pipe splits to pipe parts
                    for pipe_pointer in range(len(pipe_split)):
                        # the first split part
                        if pipe_pointer == 0:
                            pipe_parts.append(" ".join([to_pipe] + pattern_parts[base_pointer:current_pointer] + [pipe_split[pipe_pointer]]).strip(" "))
                            # reset the to pipe buffer
                            to_pipe = ""
                            # update the base pointer
                            base_pointer = current_pointer + 1
                        # the last split part
                        elif pipe_pointer == len(pipe_split) - 1:
                            to_pipe = pipe_split[pipe_pointer]
                        # in the middle
                        elif pipe_split[pipe_pointer]:
                            pipe_parts.append(pipe_split[pipe_pointer])
            # add last pattern part to pipe parts
            pipe_parts.append(" ".join([to_pipe] + pattern_parts[base_pointer:]).strip(" "))
            # remove all blanks
            while "" in pipe_parts:
                pipe_parts.remove("")
            # evaluate parts with pipes
            if len(pipe_parts) > 1:
                # initialise responses
                pipe_responses = []
                # get responses from evaluating sub-patterns
                for subpattern in pipe_parts:
                    # add inherited wrapping if necessary
                    if subpattern[0] not in ("{", "["):
                        subpattern = mode + subpattern + {"{": "}", "[": "]"}[mode]
                    # evaluate the sub pattern
                    pipe_responses.append(self.scan_pattern(subpattern, depth + 1, "|"))
                # count the matches
                match_count = [1 if response else 0 for response in pipe_responses].count(1)
                # check there is no more than 2
                if match_count >= 2:
                    # alert user to invalid arguments
                    self.display_error("Only one part of " + pattern + " can be filled")
                    exit(1)
                # required mode
                if mode == "{":
                    # check there is exclusively one match
                    if match_count != 1:
                        # alert user to invalid arguments
                        self.display_error("There must be exactly one part of " + pattern + " filled")
                        exit(1)
                # initialise return flags
                return_flags = []
                # return all set flags
                for response in pipe_responses:
                    for flag in response:
                        return_flags.append(flag)
                return return_flags
            # evaluate parts without pipes
            else:
                # required mode
                if mode == "{":
                    # initialise responses
                    pattern_responses = []
                    for subpattern in pattern_parts:
                        # add inherited wrapping if necessary
                        if subpattern[0] not in ("{", "["):
                            subpattern = mode + subpattern + {"{": "}", "[": "]"}[mode]
                        # evaluate the sub pattern
                        pattern_responses.append(self.scan_pattern(subpattern, depth + 1, parent))
                    # count the matches
                    match_count = [1 if response else 0 for response in pattern_responses].count(1)
                    # check for some but not all matches
                    if 0 < match_count < len(pattern_responses):
                        # alert user to invalid arguments
                        self.display_error("All flags are required in " + pattern)
                        exit(1)
                    # check for no entries unless parent will handle invalids
                    if match_count == 0 and not parent:
                        # alert user to invalid arguments
                        self.display_error("All flags are required in " + pattern)
                        exit(1)
                else:
                    # initialise responses
                    pattern_responses = []
                    for subpattern in pattern_parts:
                        # add inherited wrapping if necessary
                        if subpattern[0] not in ("{", "["):
                            subpattern = mode + subpattern + {"{": "}", "[": "]"}[mode]
                        # evaluate the sub pattern
                        pattern_responses.append(self.scan_pattern(subpattern, depth + 1, "["))
                # initialise return flags
                return_flags = []
                # return all set flags
                for response in pattern_responses:
                    for flag in response:
                        return_flags.append(flag)
                # add value to satisfy optional mode nested in required mode
                if mode == "[" and not return_flags:
                    return_flags.append("-*")
                return return_flags


    # parse arguments
    def parse(self, arguments, assert_typing=True):
        """parses command line arguments, tests them against a pattern and returns the results
        takes:
            ITER arguments - the argument from the command line (should be sys.argv)
        gives:
            DICT results - information about the command and the various flags it can take"""
        # initialise the command branch
        pattern_branch = self.pattern_tree
        # copy assert typing into local namespace
        self.assert_typing = assert_typing
        # copy arguments into local namespace
        self.given_arguments = [argument for argument in arguments]
        # get pattern to match with
        for argument_index in range(len(self.given_arguments)):
            # check for help
            if self.given_arguments[argument_index] == "--help":
                self.display_help()
                exit(0)
            # check if command is known
            if not self.given_arguments[argument_index] in pattern_branch:
                # display error to user
                self.display_error("Unknown command: " + self.given_arguments[argument_index])
                exit(1)
            # branch into command
            pattern_branch = pattern_branch[self.given_arguments[argument_index]]
            # add command to internal command path
            self.internal_command_path.append(self.given_arguments[argument_index])
            # detect pattern
            if type(pattern_branch) == str:
                # break out of loop
                break
        # remove command path from given arguments
        for command in self.internal_command_path:
            self.given_arguments.remove(command)
        # assert that pattern branch is a pattern
        assert type(pattern_branch) == str
        # reset results and load arguments to scan
        self.argument_results = []
        self.argument_scan = self.given_arguments[argument_index + 1:]
        # start pattern scanning with required pattern
        self.scan_pattern("{" + pattern_branch + "}", 0, "")
        # alert the user to any unknown flags
        if self.given_arguments:
            # detect help
            if "--help" in self.given_arguments:
                self.display_help()
                exit(0)
            else:
                self.display_error("Unrecognised flag " + self.given_arguments[0])
        # return the findings
        return {pair[0]: pair[1] for pair in self.argument_results}

    # open file
    def open_file(self, path, mode):
        """wrapper for open() but checks for permissions, existing files and handles errors
        takes:
            STR path - the path to the file
            STR mode - the file will be opened in this mode
        gives:
            _io.TxtIOWrapper - the file object, the same thing returned from open()"""
        # potential file overwrite
        if path_check.isfile(path) and "w" in mode:
            # unpack internal command path
            caller_address = self.unpack_command_path(self.internal_command_path if self.internal_command_path else [self.script_name])
            # acquire overwrite confirmation
            user_confirmation = (caller_address + ": File " + path + " already exists, overwrite? [y/n]: ").upper()
            while user_confirmation not in ("Y", "N"):
                print(caller_address + ": Please enter 'Y' or 'N'")
                user_confirmation = (caller_address + ": File " + path + " already exists, overwrite? [y/n]: ").upper()
            # check for overwrite denial
            if user_confirmation == "N":
                exit(0)
        # attempt to open the file
        try:
            file = open(path, mode)
        # permission denied
        except PermissionError:
            self.display_error("Permission denied when accessing file " + path)
            exit(1)
        # file not found
        except FileNotFoundError:
            self.display_error("Could not locate file " + path)
            exit(1)
        # file exists
        except FileExistsError:
            self.display_error("File " + path + " already exists")
            exit(1)
        # catch all
        except:
            self.display_error("Could not access file " + path)
            exit(1)
        # return IO object
        return file
