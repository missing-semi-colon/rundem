#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2021 missing-semi-colon <https://github.com/missing-semi-colon>
Copyright (c) 2018 mingrammer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
mingrammer's code that was used to provide the basic menu functionality can be found here:
https://github.com/mingrammer/python-curses-scroll-example/blob/4c4188154cb924e96539ae7011419d1910d71775/tui.py
"""

import curses


class Screen:
	"""
	Attrs:
		items: List of strings to be displayed
		stdscr: A curses window
		width: The width of `stdscr`
		height: The height of `stdscr`
		top: Number of the item at the top of the window
		item_count: Total number of items
		current: Current highlighted line number (0 to `height` - 1)

		┌--------------------------------------┐
		|1. Item                               |
		|--------------------------------------| <- start of visible window
		|2. Item                               | <- top = 1
		|3. Item                               |
		|4./Item///////////////////////////////| <- current = 2
		|5. Item                               |
		|6. Item                               |
		|7. Item                               |
		|8. Item                               | <- height = 7
		|--------------------------------------| <- end of visible window
		|9. Item                               |
		|10. Item                              | <- item_count = 10
		|                                      |
		|                                      |
		└--------------------------------------┘
	"""

	UP = -1
	DOWN = 1

	def __init__(self, items: list) -> None:
		self.items = items

		self.stdscr = None
		self.width = 0
		self.height = 0
		self.top = 0
		self.item_count = len(self.items)
		self.current = 0
		self.return_to = None

	def start(self) -> None:
		""" Start running the UI """
		curses.wrapper(self._run)

	def set_return_to(self, screen) -> None:
		self.return_to = screen

	def clear_return_to(self) -> None:
		self.return_to = None

	def get_return_to(self) -> object:
		return self.return_to

	def _setup(self) -> None:
		""" Setup curses """
		self.height, self.width = self.stdscr.getmaxyx()

		curses.start_color()
		# Not selected: #0
		# Selected
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

	def _run(self, stdscr: curses.window) -> None:
		""" Handle user input and draw the UI """
		self.stdscr = stdscr
		self._setup()
		self._display()

		key = 0
		while key != ord('q'):
			key = self.stdscr.getch()
			if key == curses.KEY_UP:
				self._scroll(self.UP)
			elif key == curses.KEY_DOWN:
				self._scroll(self.DOWN)
			elif key == curses.KEY_PPAGE:
				self._page(self.UP)
			elif key == curses.KEY_NPAGE:
				self._page(self.DOWN)
			elif key == curses.KEY_LEFT:
				self._to_end(self.UP)
			elif key == curses.KEY_RIGHT:
				self._to_end(self.DOWN)
			elif key == curses.KEY_RESIZE:
				self._setup()
			elif self._select(key) == True:
				break

			self._display()

	def _scroll(self, direction: int) -> None:
		""" Scrolling 1 line at a time """
		if direction == self.UP:
			if self.current > 0:
				self.current += self.UP
			else:
				self.top += self.UP
		else:
			if self.current < self.height - 1:
				self.current += self.DOWN
			else:
				self.top += self.DOWN

		# Prevent scrolling past the first or last items
		self._clamp_top()
		self._clamp_current()

	def _page(self, direction: int) -> None:
		""" Scrolling 1 page at a time """
		if direction == self.UP:
			# If the first item is visible, then set the cursor's position to it
			if self.top == 0:
				self.current = 0
			# Otherwise scroll up by the screen size
			else:
				self.top += self.UP * self.height
		elif direction == self.DOWN:
			# If the last item is visible, then set the cursor's position to it
			if self.top >= self.item_count - self.height:
				self.current = self.item_count - 1
			# Otherwise scroll down by the screen size
			else:
				self.top += self.DOWN * self.height

		# Prevent scrolling past the first or last items
		self._clamp_top()
		self._clamp_current()

	def _to_end(self, direction: int) -> None:
		""" Moves the cursor to the top or bottom of the window """
		visible_item_count = self._get_visible_item_count()
		if visible_item_count == 0:
			self.current = 0
		else:
			side = (direction + 1) // 2
			self.current = side * (visible_item_count - 1)

	def _select(self, key) -> bool:
		"""
		Override this.
		Called when an item is selected.

		Args:
			key: curses key-code for the key pressed

		Returns:
			True if the current screen should end as a result of selecting the
			item, False otherwise
		"""
		pass

	def _display(self) -> None:
		""" Display the items on window """
		self.stdscr.erase()
		for idx, item in enumerate(self.items[self.top:self.top + self.height]):
			color_pair_num = 0
			if idx == self.current:
				color_pair_num = 1
			self.stdscr.addstr(
				idx, 0,
				str(item)[:self.width - 1],
				curses.color_pair(color_pair_num) )
		self.stdscr.refresh()

	def _get_visible_item_count(self) -> int:
		""" Returns the number of items in the window """
		return min(self.height, self.item_count - self.top)

	def _clamp_top(self) -> None:
		""" Keeps self.top within a valid range """
		self.top = clamp(self.top, 0, max(0, self.item_count - self.height))

	def _clamp_current(self) -> None:
		""" Keeps self.current within a valid range """
		visible_item_count = self._get_visible_item_count()
		if visible_item_count == 0:
			self.current == 0
		else:
			self.current = clamp(self.current, 0, visible_item_count - 1)

def clamp(val: float, minimum: float, maximum: float) -> float:
	if maximum < minimum:
		raise ValueError("maximum is less than minumum")
		return
	return min(maximum, max(minimum, val))


if __name__ == '__main__':
	items = [f"{num + 1}. Item" for num in range(100)]
	screen = Screen(items)
	screen.start()
