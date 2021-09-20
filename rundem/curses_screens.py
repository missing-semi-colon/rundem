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
import subprocess as subp
from os import environ, remove as remove_file
# Custom modules
from curses_base_screen import Screen
from utils import is_script


class ScriptMenu(Screen):
	"""
	Attrs:
		scripts: a list where each element is a command if the respective item
			in `self.items` (see the Screen class) is associated with a command
			otherwise `None`
		script_indicator: the string prefixed to all script items
	"""
	def __init__(self, items: list, script_indicator: str) -> None:
		self.scripts = [item[1] if len(item) >= 2 else None for item in items]
		self.script_indicator = script_indicator
		Screen.__init__(self, [item[0] for item in items])

	def _setup(self) -> None:
		"""
		Overridden

		Setup curses
		"""
		self.height, self.width = self.stdscr.getmaxyx()

		curses.start_color()
		# Normal: #0
		# Selected normal
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
		# Script
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
		# Selected script
		curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)

	def _select(self, key: int) -> bool:
		"""
		Overridden

		Checks if the selected item is a script, if it is then handles the
		user's input (run the script or edit the script)

		Args:
			key: curses key-code for the key pressed

		Returns:
			True if the current screen should end as a result of selecting the
			item, False otherwise
		"""
		selected_idx = self.top + self.current
		script = self.scripts[selected_idx]
		if script == None:
			# Selected item is not a script
			return False

		# If ENTER was pressed (may be a newline or carriage return)
		if key == 10 or key == 13:
			script_screen = ScriptRunner(script)
			self.set_return_to(script_screen)
			script_screen.set_return_to(self)
			return True
		# If 'e' was pressed
		elif key == 101:
			edit_screen = ScriptEditor(script)
			self.set_return_to(edit_screen)
			edit_screen.set_return_to(self)
			return True
		else:
			return False

	def _display(self) -> None:
		"""
		Overridden

		Display the items on the window
		"""
		self.stdscr.erase()
		for idx, item in enumerate(self.items[self.top:self.top + self.height]):
			text = item
			color_pair_num = 0
			if (not is_script(self.script_indicator, item)) and idx != self.current:
				color_pair_num = 0
			elif (not is_script(self.script_indicator, item)) and idx == self.current:
				color_pair_num = 1
			elif is_script(self.script_indicator, item) and idx != self.current:
				# Removes SCRIPT_INDICATOR from the start of the text
				text = item[len(self.script_indicator):]
				color_pair_num = 2
			elif is_script(self.script_indicator, item) and idx == self.current:
				# Removes SCRIPT_INDICATOR from the start of the text
				text = item[len(self.script_indicator):]
				color_pair_num = 3
			self.stdscr.addstr(idx, 0, text, curses.color_pair(color_pair_num))
		self.stdscr.refresh()

class ScriptRunner:
	"""
	Attrs:
		script: the command that will be executed given the user's confirmation
	"""
	def __init__(self, script: str) -> None:
		self.script = script
		self.return_to = None

	def start(self) -> None:
		subp.Popen(["clear", "-x"]).wait()

		run = None
		while True:
			print("Execute the following command?")
			print(f"`{self.script}`")
			run = input("(Y/n) ")
			if run == "" or run.lower() == "y":
				print()
				try:
					# Need shell=True to allow full shell functionality such as:
					# support for && and ||
					subp.Popen(self.script, shell=True).wait()
					input("\nCOMPLETE: press ENTER to return")
				except KeyboardInterrupt as e:
					input("\nINTERRUPTED: press ENTER to return")
				break
			if run.lower() == "n":
				break

	def set_return_to(self, screen) -> None:
		self.return_to = screen

	def clear_return_to(self) -> None:
		self.return_to = None

	def get_return_to(self) -> object:
		return self.return_to

class ScriptEditor:
	"""
	Attrs:
		script: the command that will be modified by the user
	"""
	def __init__(self, script: str) -> None:
		self.script = script
		self.return_to = None

	def start(self) -> None:
		# Create a temporary file for the changes to be saved to and read from
		tmp_filename_bytes = subp.check_output([
				"mktemp",
				"--tmpdir",
				"rundem-tmp-runner.XXXXXX" ])
		tmp_filename = tmp_filename_bytes.decode("utf-8").strip()
		with open(tmp_filename, "w") as file:
			file.write(self.script)
		editor = environ.get("EDITOR", "nano")
		subp.run([editor, tmp_filename])

		tmp_script = ""
		with open(tmp_filename, "r") as file:
			tmp_script = file.readline().strip()
		try:
			remove_file(tmp_filename)
		except:
			pass

		script_screen = ScriptRunner(tmp_script)
		script_screen.set_return_to(self.get_return_to())
		self.set_return_to(script_screen)

	def set_return_to(self, screen) -> None:
		self.return_to = screen

	def clear_return_to(self) -> None:
		self.return_to = None

	def get_return_to(self) -> object:
		return self.return_to
