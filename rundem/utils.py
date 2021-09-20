#!/usr/bin/env python3

def is_script(indicator: str, item: str) -> bool:
	""" Returns whether `item` contains a script """
	return item.startswith(indicator)
