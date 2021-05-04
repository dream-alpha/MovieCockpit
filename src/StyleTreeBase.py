#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2021 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


from Debug import logger
import os
from xml.etree import ElementTree


class StyleTreeBase():
	def __init__(self, file_name=None):
		#logger.info("...")
		self.read(file_name)

	def read(self, file_name):
		#logger.info("file_name: %s", file_name)
		self.tree = None
		self.root = None
		if file_name and os.path.exists(file_name):
			self.tree = ElementTree.parse(file_name)
			self.root = self.tree.getroot()
			return True
		logger.error("file does not exist: %s", file_name)
		return False

	def indent(self, elem, level=0, more_sibs=False):
		#logger.info("...")
		t = "	"
		i = "\n"
		if level:
			i += (level - 1) * t
		num_kids = len(elem)
		if num_kids:
			if not elem.text or not elem.text.strip():
				elem.text = i + t
				if level:
					elem.text += t
			count = 0
			for kid in elem:
				self.indent(kid, level + 1, count < num_kids - 1)
				count += 1
			if not elem.tail or not elem.tail.strip():
				elem.tail = i
				if more_sibs:
					elem.tail += t
		else:
			if level and (not elem.tail or not elem.tail.strip()):
				elem.tail = i
				if more_sibs:
					elem.tail += t

	def write(self, file_name):
		#logger.info("filename: %s", file_name)
		self.indent(self.root)
		self.tree.write(file_name, encoding="utf-8")
