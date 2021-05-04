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
from datetime import datetime
from StyleTreeBase import StyleTreeBase


class StyleSkin(StyleTreeBase):
	def __init__(self, file_name=None):
		logger.info("file_name: %s", file_name)
		StyleTreeBase.__init__(self, file_name)
		self.read(file_name)

	def isStyled(self):
		return self.style_node is not None

	def read(self, file_name):
		logger.info("file_name: %s", file_name)
		self.replaces = []
		self.style_info = []
		self.style_node = None
		self.style_name = ""
		self.user_mtime = ""
		result = StyleTreeBase.read(self, file_name)
		logger.debug("result: %s", str(result))
		if result:
			test = self.root.findall("style")
			if len(test) == 1:
				self.style_node = test[0]
				logger.debug("style_node: %s", str(self.style_node))
				self.style_name = self.style_node.attrib.get("name", "")
				logger.debug("style_name: %s", str(self.style_name))
		return result

	def write(self, file_name):
		logger.info("file_name: %s, self.root: %s", file_name, self.root)
		if self.root is not None:
			self.applyAttributes(self.replaces)
			logger.debug("file_name: %s, self.replaces: %s", file_name, self.replaces)
			self.updateStyleInfo()
			StyleTreeBase.write(self, file_name + "~")
			logger.debug("file_name: %s", file_name)
			os.rename(file_name + "~", file_name)

	def updateStyleInfo(self):
		if self.style_node is None:
			self.style_node = ElementTree.Element("style")
			self.root.insert(0, self.style_node)

		self.style_node.clear()
		self.style_node.attrib["name"] = self.style_name if self.style_name else ""
# 		self.style_node.attrib["revision"] = __revision__
		self.style_node.attrib["time_stamp"] = str(datetime.now())
#	 	self.style_node.attrib["user_mtime"] = str(self.user_mtime)
		logger.debug("self.style_info: %s", self.style_info)
		for tag, key, value in self.style_info:
			elem = ElementTree.Element(tag)
			elem.attrib["name"] = key
			elem.attrib["value"] = value
			self.style_node.append(elem)

	def applyNodes(self, nodes):
		for node in nodes:
			self.applyNode(node)

	def __replaceNode(self, root, node, _tag, _name, _id):
		for index, child in enumerate(root):
			if child.tag == _tag:
				if child.attrib.get("name", "") == _name and child.attrib.get("id", "") == _id:
					logger.debug("replace tag: %s, name: %s, id: %s, index: %s", _tag, _name, _id, index)
					root[index] = node
					return True
		return False

	def applyNode(self, nodes):
		logger.debug("nodes: %s", str(nodes))
		if nodes is not None:
			for node in nodes:
				_tag = node.tag
				_name = node.attrib.get("name", "")
				_id = node.attrib.get("id", "")
				logger.debug("_tag: %s, _name: %s, _id: %s", _tag, _name, _id)
				if _tag == "attributes":
					self.replaces.extend(node)
					continue

				if _tag == "layout":
					for child in self.root.findall("layouts"):
						self.__replaceNode(child, node, _tag, _name, _id)
					continue

				found = self.__replaceNode(self.root, node, _tag, _name, _id)

				if not found and _tag == "screen":
					logger.debug("add tag: %s, name: %s, id: %s", _tag, _name, _id)
					self.root.append(node)
					found = True
				if not found:
					logger.debug("not found tag: %s, name: %s, id: %s", _tag, _name, _id)

	def applyAttributes(self, nodes):
		if nodes:
			to_replace = []
			for node in nodes:
				name = node.attrib.get("name", "")
				value = node.attrib.get("value", "")
				expect = node.attrib.get("expect", None)
				to_replace.append((name, value, expect, node.tag))
			logger.debug("replace: %s", str(to_replace))
			self.__replaceAttributes(self.root, to_replace)

	def __replaceAttributes(self, node, replace):
		for key in node.attrib.iterkeys():
			for name, value, expect, node_tag in replace:
				if expect is not None and expect != node.attrib[key]:
					continue
				if node_tag == "set" and key == name:
					node.attrib[key] = value
					continue
				if node.attrib[key].startswith(name):
					node.attrib[key] = node.attrib[key].replace(name, value)
					continue

		for x in node:
			self.__replaceAttributes(x, replace)

	def getConfig(self):
		d = dict()
		d["preset"] = dict()
		d["style"] = dict()
		if self.style_node is not None:
			for node in self.style_node:
				name = node.attrib.get("name", "")
				value = node.attrib.get("value", "")
				if name and value:
					d[node.tag][name] = value
		return d
