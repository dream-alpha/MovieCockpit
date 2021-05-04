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
from xml.etree import ElementTree
from datetime import datetime
from Components.config import config
from StyleTreeBase import StyleTreeBase
from StyleItem import StyleItem


class Style(StyleTreeBase):
	def __init__(self, file_name=None):
		StyleTreeBase.__init__(self, file_name)

	def checkDependency(self, _depend):
		return

	def hasStyle(self):
		logger.debug("%s", str(self.root is not None))
		return self.root is not None

	def printInfo(self):
		groups = self.getGroup()
		for key1 in sorted(groups):
			logger.debug("printInfo: key1: %s", key1)
			for key2 in sorted(groups[key1]):
				logger.debug("key2:   %s", key2)
				for _key3 in sorted(groups[key1][key2]):
					logger.debug("    %s", _key3)

	def getStyleNodes(self):
		alist = []
		for node in self.root:
			if node.tag in ("presets", "sorted", "depends"):
				continue
			for style in node.findall("style"):
				item = StyleItem(style, node)
				logger.debug("item.getParentName: %s", str(item.getParentName()))
				logger.debug("item.getName: %s", str(item.getName()))
				logger.debug("item.getValue: %s", str(item.getValue()))
				alist.append(item)
		return alist

	def getStyleNode(self, key, value):
		styles = self.getStyleNodes()
		for style in styles:
			n = style.getName()
			v = style.getValue()
			if n == key and v == value:
				logger.debug("key: %s, value: %s", key, value)
				return style
		return None

	def getSkinNode(self, key, value):
		style = self.getStyleNode(key, value)
		if style:
			return style.getSkinNode()
		logger.debug("not skin, key: %s, value: %s", key, value)
		return None

	def getGroup(self):
		d = dict()
		styles = self.getStyleNodes()
		for style in styles:
			if self.checkDependency is not None and not self.checkDependency(style.getDepend()):
				continue
			p = style.getParentName()
			n = style.getName()
			v = style.getValue()
			if p not in d:
				d[p] = dict()
			if n not in d[p]:
				d[p][n] = dict()
			d[p][n][v] = style.getSkinNode()
		return d

	def getDefault(self):
		d = dict()
		logger.debug("getDefault: dict(): %s", str(d))
		for node1 in self.root.findall("presets"):
			for default in node1.findall("default"):
				for node2 in default:
					name = node2.attrib.get("name", "")
					value = node2.attrib.get("value", "")
					if name and value:
						d[name] = value
		return d

	def getPreset(self):
		d = dict()
		for node in self.root.findall("presets"):
			for styles in node.findall("style"):
				p = styles.attrib.get("name", "")
				n = styles.attrib.get("value", "")
				if p not in d:
					d[p] = dict()
				if n not in d[p]:
					d[p][n] = dict()
				for s in styles:
					v = s.attrib.get("name", "")
					value = s.attrib.get("value", "")
					d[p][n][v] = value
		return d

	def getPresetPreview(self, name, value, default=None):
		if name:
			for node in self.root.findall("presets"):
				for styles in node.findall("style"):
					for s in styles:
						n = s.attrib.get("name", "")
						v = s.attrib.get("value", "")
						if n == name and v == value:
							if "preview" in styles.attrib:
								return styles.attrib.get("preview", "")
							return default
		return default

	def getPreview(self, name, value, default=None):
		if name:
			for node in self.root:
				for styles in node.findall("style"):
					n = styles.attrib.get("name", "")
					v = styles.attrib.get("value", "")
					if n == name and v == value:
						if "preview" in styles.attrib:
							return styles.attrib.get("preview", "")
						return default
		return default

	def getDepends(self):
		d = dict()
		for node in self.root:
			for styles in node.findall("depend"):
				n = styles.attrib.get("name", "")
				v = styles.attrib.get("value", "")
				if n and v:
					d[n] = v
		return d

	def getSorted(self):
		d = dict()
		for nodes in self.root.findall("sorted"):
			for node in nodes:
				i = node.attrib.get("id", "")
				n = node.attrib.get("name", "")
				if n and i:
					d[n] = int(i)
		return d

	def sort(self, styles):
		s = self.getSorted()
		k = styles.keys()
		lx = sorted(k, key=lambda x: s.get(x, x))
		return lx

	def checkPresets(self):
		errors = []
		count = 0
		preset = self.getPreset()
		node = ElementTree.Element("presets")
		for key1 in sorted(preset):
			logger.debug("key1: %s", key1)
			for key2 in sorted(preset[key1]):
				root = ElementTree.Element("style")
				root.attrib["name"] = key1
				root.attrib["value"] = key2
				element = None
				for key3 in sorted(preset[key1][key2]):
					logger.debug("%s = %s", str(key2), preset[key1][key2][key3])
					test = self.getSkinNode(key3, preset[key1][key2][key3])
					if test is None:
						count += 1
						text = str.format('name="{0}" value="{1}"', key3, preset[key1][key2][key3])
						if text not in errors:
							errors.append(text)
						logger.debug("text: %s", text)
						element = ElementTree.Element("style")
						element.attrib["name"] = key3
						element.attrib["value"] = preset[key1][key2][key3]
						root.append(element)
				if element is not None:
					node.append(root)

		if count > 0:
			info = ElementTree.Element("info")
			node.insert(0, info)
			info.attrib["description"] = "{0} error(s) in presets found!".format(count)
			info.attrib["time_stamp"] = str(datetime.now())
			for text in errors:
				info.append(ElementTree.Comment(text))
			logger.debug("%s errors found", count)
			self.indent(node)
			return ElementTree.tostring(node)
		return ""

	def getSkinComponents(self):
		defaults = self.getDefault()
		style_info = []
		nodes = []
		for key in sorted(config.plugins.moviecockpit.preset):
			value = config.plugins.moviecockpit.preset[key].getValue()
			style_info.append(("preset", key, value))
		for key in sorted(config.plugins.moviecockpit.style):
			value = config.plugins.moviecockpit.style[key].getValue()
			node = self.getSkinNode(key, value)
			if node is None and key in defaults:
				logger.debug("no style key: %s, value: %s", key, value)
				value = defaults[key]
				node = self.getSkinNode(key, value)
				if node is None:
					logger.debug("not found key: %s, value: %s", key, value)
					continue
				logger.debug("use default key: %s, value: %s", key, value)
			nodes.append(node)
			style_info.append(("style", key, value))
		return (nodes, style_info)
