# DOCUMENTATION
Below is the documentation for various parts of the clihelper module. Hopefully it will allow you to make some sense of the horrible mess of code that I've written! 

## What Does it Do?
Lorem ipsum

## How to Use it
Lorem ipsum

## Pattern Rules and Workings
The clihelper interface uses a pattern to determine if a given set of arguments is valid. It determines which pattern to use by navigating through a command tree. At each node, clihelper will look at the argument that was passed in through the command line and branch to it. If it arrives and an end node then that is the pattern it will scan against.

There are a few rules to follow when creating a command tree:
1. The first note must be the same as sys.argv[0], the name of the script
2. Each node can be a dictionary (a branch of the command tree) or a string (a pattern)

As an example, let's say we have a script that will be invoked by running 'foo.py'. We shall also say that this script has two command, push and pull. The command tree will look as follows:

- 'foo.py':
    - 'push':
        - 'pattern0'
    - 'pull':
        - 'pattern1'

Which can be represented in a Python dictionary as:\
{'foo.py': {'push': 'pattern0', 'pull': 'pattern1'}}

A command tree with no commands should still be represented by a command tree. This can be done with a dictionary as follows:\
{'foo.py': 'pattern0'}

After the command tree has been traversed, the pattern will be scanned against the remaining elements is sys.argv. This is best understood via logical expressions:
- {A B}: A and B
- [A B]: A or B
- {A|B}: A xor B
- [A|B]: A nand B

Where A and B are expressions. An expression can be one of the above or a flag with an optional argument. An argument is represented with a type enclosed in angle tags \<...>. The type will be automatically checked if it is recognised and assigned to the preceding flag. Only one argument can specified without a flag which must appear at the end of the pattern. It will be assigned to a itself instead of a flag.

A few example patterns are shown below:
- '-a \<INT> [-b -c {-d -e}]': The '-a' flag is required along with an integer. Arguments '-b' and '-c' are completely optional while '-d' and '-e' must both be present if at least one of them is present. Note that it would be valid not to pass in '-d' or '-e' as the required tags are within optional tags
- '[-a|-b] \<filename>': The '-a' and '-b' flags are optional but cannot both be present. The final argument passed in will be associated with 'filename' instead of a flag
- '-a -b -c|-d -e -f': Only '-a', '-b' and '-c' should appear or only '-d', '-e' and '-f' should appear
- '[-a {-b -c}|-d]': If '-d' appears, then no other flag can appear. Otherwise '-a' is completely optional while '-b' and '-c' must appear together

Combine this with the pattern tree then we get the full command tree that should be passed to the Interface. These look messy in code but are logical to understand. Below are a few examples to show you what they should look like:
- {'foo.py': {'push': '[-t \<INT> -f] {-q|-v} \<filename>', 'pull': '-o <PATH> {-q|-v} <url>'}}
- {'foo.py': '[-j -c] \<number>'}
- {'foo.py': {'bar': '-b <PATH>', 'spam': {'egg': '{-b|-s|-f|-p} [-s|-p]', 'ham': '[-t \<FLOAT>] \<outputfile>'}}}

## Defining Custom Types
Lorem ipsum
