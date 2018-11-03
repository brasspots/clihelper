# python3 processor for Linux command line programs
# this module provides most the boilerplate code for command line python scripts including:
#   - help message
#   - bad usage messages
#   - automatic flag handling
#
# Note: This does not replace sys for accessing command line arguments
# It only makes syntax checking the arguments easier
#
# see https://github.com/brasspots/clihelper/tree/master for the latest version

# initialise version
VERSION = "1.0"
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
        for command in self.internal_command_path:
            target_patterns = target_patterns[command]
        # unpack pattern sub tree
        if type(target_patterns) == dict:
            target_patterns = self.unpack_pattern_tree(target_patterns)
        else:
            target_patterns = [target_patterns]
        # unpack internal command path
        caller_address = self.unpack_command_path(self.internal_command_path)
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
        caller_address = self.unpack_command_path(self.internal_command_path)
        # print message
        print(caller_address + ": " + message + "\tTry: '" + caller_address + " --help' for more info")

    # scan pattern
    def scan_pattern(self, pattern, depth):
        """recursively scans the arguments to match to pattern and updates argument_results with the findings
        takes:
            STR pattern - the pattern to match against
        gives:
            BOOL - the pattern is matched"""
        # get element type and strip brackets
        type = pattern[0]
        pattern_parts = pattern[1:-1].split(" ")
        # run the base case
        if (len(pattern_parts) == 1 or (len(pattern_parts) == 2 and pattern_parts[1] == "<")) and all("|" not in part for part in pattern_parts):
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
                else:
                    append_value = True
                # remove flag from given arguments
                self.given_arguments.remove(pattern_parts[0])
                # add result to results collection
                self.argument_results.append((pattern_parts[0], append_value))
                return True
            # detect unassigned value
            elif pattern_parts[0].startswith("<") and depth == 0:
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
                self.argument_results.append(pattern_parts[0], append_value)
                return False
        # run the recursion
        else:
            pass

    # parse arguments
    def parse(self, arguments):
        """parses command line arguments, tests them against a pattern and returns the results
        takes:
            ITER arguments - the argument from the command line (should be sys.argv)
        gives:
            DICT results - information about the command and the various flags it can take"""
        # initialise the command branch
        pattern_branch = self.pattern_tree
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
        # assert that pattern branch is a pattern
        assert type(pattern_branch) == str
        # reset results and load arguments to scan
        self.argument_results = {}
        self.argument_scan = self.given_arguments[argument_index + 1:]
        # start pattern scanning with required pattern
        self.scan_pattern("{" + pattern_branch + "}", 0)
        # alert the user to any unknown flags
        if self.given_arguments:
            # detect help
            if "--help" in self.given_arguments:
                self.display_help()
                exit(0)
            else:
                self.display_error("Unrecognised flag " + self.given_arguments[0])
        # return the findings
        return {pair[0]:pair[1] for pair in self.argument_results}