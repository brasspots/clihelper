# DOCUMENTATION
Below is the documentation for various parts of the clihelper module. Hopefully it will allow you to make some sense of the horrible mess of code that I've written! 

## What Does it Do?
clihelper is a python3 module, primarily to interface with the command line but it has other functions as well. It is all based around an Interface class, from which you call certain methods to do certain things.

The main functionality of this class is to parse command line arguments. To do this, clihelper uses a pattern to check if a given input is valid. It will then return a dictionary which maps all the parameters to their values.

## How to Use it
After importing clihelper into your script, you need to initialise the Interface. This is the class which will handle the argument parsing and other such tasks. To initialise it, you need to pass it several values:
- script_name: This is the name of your script, or more precisely, the first value in sys.argv
- short_description: This is a simple description of what your code does. It will be displayed at the top of the help message
- long_description: This is a more in-depth explanation and will be present at the bottom of the help message
- pattern_tree: This allows your script to assume different patterns based on commands. It will be discussed below
- parameter_information: This contains all the information about the parameters that your script can take. Again, this will be discussed below

## The Pattern Tree
Lorem ipsum

## Pattern Rules
Lorem ipsum

## Defining Custom Types
Lorem ipsum
