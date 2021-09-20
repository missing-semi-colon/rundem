# rundem
rundem (an amalgamation of "run" and "them") allows you to run listed commands from a curses-like interface. Useful if you have scripts that should be run regularly and require user input, such as password protected backups, as you only need to remember to run one command (rundem) and it will list all of your commands/scripts.

## Features
- Run commands
- Non-destructively edit commands before running

## Configuring
The runners file, located at either $XDG_CONFIG_HOME/rundem/runners or ~/.config/rundem/runners, contains the commands you want to be able to run in rundem. The location of this file can also be specified with the `-c` option.

Each line must be formatted as follows:

\<INDICATOR>\<TEXT>\<SEPERATOR>\<COMMAND>

Where:

- INDICATOR is a string (by default it is '+') and it indicates that the line contains a command
- TEXT is any text you want that doesn't contain SEPERATOR
- SEPERATOR is a string (by default it is ' // ') and seperates the command from the rest of the line
- COMMAND is the command that will be run

INDICATOR and SEPERATOR can be changed through the command-line options `-i` and `-s` respectively.

A line could also be formatted as:

\<TEXT>

Where TEXT does not start with INDICATOR. This is useful for visibly seperating groups of commands.
