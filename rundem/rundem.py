#!/usr/bin/env python3

"""
Copyright 2021 missing-semi-colon <https://github.com/missing-semi-colon>

This file is part of rundem.

rundem is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

rundem is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with rundem. If not, see <https://www.gnu.org/licenses/>.
"""

import curses
import os
import sys
import shutil
# Custom modules
from curses_screens import ScriptMenu
from utils import is_script

EXAMPLE_SCRIPT_PATH = "/etc/rundem/example"

script_indicator = "+"
script_seperator = " // "

filepath = None


def handle_args() -> bool:
	"""
	Handles command line arguments

	Returns:
		Wether to continue running the program after returning from this
		function
	"""
	idx = 1
	while len(sys.argv) > idx:
		arg = sys.argv[idx]
		if arg == "-h":
			show_params()
			return False
		elif arg == "-c":
			if len(sys.argv) > idx + 1:
				set_scripts_path(sys.argv[idx + 1])
				idx += 1
			else:
				raise ValueError("No path provided to the '-c' argument")
				return False
		elif arg == "-i":
			if len(sys.argv) > idx + 1:
				global script_indicator
				script_indicator = sys.argv[idx + 1]
				idx += 1
			else:
				raise ValueError("No indicator passed to the '-i' argument")
				return False
		elif arg == "-s":
			if len(sys.argv) > idx + 1:
				global script_seperator
				script_seperator = sys.argv[idx + 1]
				idx += 1
			else:
				raise ValueError("No seperator provided to the '-s' argument")
				return False
		else:
			raise ValueError(f"Unkown argument: '{arg}'")
			return False
		idx += 1
	return True

def show_params() -> None:
	""" Displays possible command line arguments """
	print("Usage: rundem [OPTION...]\n")
	print("Options")
	print("-h              Shows this help text")
	print("-c PATH         Use the runners file at PATH rather than the default")
	print("-i INDICATOR    Specify the line prefix used in the file to indicate if it is a script")
	print("-s SEPERATOR    Specify the string used to seperate the display text from the command")

def set_scripts_path(path: str) -> None:
	global filepath
	filepath = os.path.abspath(path)

def check_scripts_path() -> None:
	""" If the scripts file's path is not set, sets it to a default path """
	if filepath == None or filepath == "":
		config_dir = os.environ.get("XDG_CONFIG_HOME")
		if config_dir == None:
			home = os.environ.get("HOME")
			if home == None:
				raise ValueError("HOME environment variable not set")
			config_dir = home + "/.config"
		base_dir = config_dir + "/rundem"
		set_scripts_path(base_dir + "/runners")

def make_scripts_file_if_needed() -> None:
	"""
	Creates the scripts file at `filepath` if it does not exist and copies the
	example file into it
	"""
	base_dir = "/".join(filepath.split("/")[:-1])
	os.makedirs(base_dir, exist_ok=True)
	if not os.path.isfile(filepath):
		if os.path.isfile(EXAMPLE_SCRIPT_PATH):
			shutil.copy(EXAMPLE_SCRIPT_PATH, filepath)
		else:
			with open(filepath, "a") as file:
				pass

def process_file(filepath: str) -> list:
	"""
	Args:
		filepath: path to the runners file

	Returns:
		List of lists. Index 0 of each sublist contains the text to display in
		the menu and index 1 contains the command to run, or there is no index 1
		if no command is associated with the text

	There are 2 ways each line in the file could be formatted:
	1.
	<script_indicator><TEXT><script_seperator><COMMAND>
	Where `TEXT` is the text shown in the menu and does not contain
	`script_seperator` and `COMMAND` is the command to run.

	2.
	<TEXT>
	Where `TEXT` does not start with `script_indicator`. This can be used to
	visibly seperate groups of scripts.
	"""
	items = []
	with open(filepath, "r") as file:
		line_num = 0
		for line in file:
			line_num += 1
			if is_script(script_indicator, line):
				seperator_pos = line.find(script_seperator)
				if seperator_pos == -1:
					msg = f"{filepath} is incorrectly formatted on line "
					msg += f"{line_num}. Expected a command but none given"
					raise RuntimeError(msg)
				name = line[:seperator_pos]
				script = line[seperator_pos + len(script_seperator):].rstrip("\n")
				items.append([name, script])
			else:
				items.append([line])
	return items

if __name__ == "__main__":
	cont = handle_args()
	if cont:
		check_scripts_path()
		make_scripts_file_if_needed()

		items = process_file(filepath)
		s = ScriptMenu(items, script_indicator)

		current_screen = s
		while current_screen:
			try:
				current_screen.start()
			except KeyboardInterrupt as e:
				pass
			next_screen = current_screen.get_return_to()
			current_screen.clear_return_to()
			current_screen = next_screen
