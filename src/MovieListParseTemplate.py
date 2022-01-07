#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
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


import six
from .Debug import logger
from .FileUtils import readFile
from .SkinUtils import getSkinPath, getScalingFactor
try:
	import pprint
	pp = pprint.PrettyPrinter(indent=4, width=120)
except ImportError:
	pp = None


template_path = getSkinPath("MovieListTemplate.py")
scaling_factor = getScalingFactor()


def MultiContentEntryProgressPixmap(pos, size, png, foreColor, percent, borderWidth):
	return "MultiContentEntryProgressPixmap(" + "pos=" + str(pos) + ", size=" + str(size) + ", percent=" + str(percent) + ", png=" + str(png)\
		+ ", foreColor=" + ("0x%x" % foreColor) + ", borderWidth=" + str(borderWidth) + ")"


def MultiContentEntryText(pos, size, font, flags, text, color, color_sel):
	return "MultiContentEntryText(" + "pos=" + str(pos) + ", size=" + str(size) + ", font=" + str(font) + ", flags=" + str(flags)\
		+ ", text=" + str(text) + ", color=" + ("0x%x" % color) + ", color_sel=" + ("0x%x" % color_sel) + ")"


def MultiContentEntryPixmapAlphaBlend(pos, size, png):
	return "MultiContentEntryPixmapAlphaBlend(" + "pos=" + str(pos) + ", size=" + str(size) + ", png=" + str(png) + ")"


def gFont(font_name, font_size):
	return "gFont(\"" + font_name + "\"," + str(font_size) + ")"


def parseTemplate(template_string):

	def scale(number):
		if isinstance(number, int):
			result = int(round(scaling_factor * number))
		elif isinstance(number, tuple):
			result = (int(round(scaling_factor * number[0])), int(round(scaling_factor * number[1])))
		else:
			result = number
		return result

	def parseListStyles(list_styles, row_height, line_height):
		for index, list_style in six.iteritems(list_styles):
			row_height[index] = scale(list_style[2])
			line_height[index] = row_height[index] / list_style[3]

	# just for parsing, no real values, used by eval
	RT_HALIGN_LEFT = ""		# noqa: F841 pylint: disable=W0612
	RT_HALIGN_RIGHT = ""		# noqa: F841 pylint: disable=W0612
	RT_HALIGN_CENTER = ""		# noqa: F841 pylint: disable=W0612
	yoffs = 0			# noqa: F841 pylint: disable=W0612
	start = 0			# noqa: F841 pylint: disable=W0612
	spacer = 0			# noqa: F841 pylint: disable=W0612
	date_width = 0			# noqa: F841 pylint: disable=W0612
	length_width = 0		# noqa: F841 pylint: disable=W0612
	progress_width = 0		# noqa: F841 pylint: disable=W0612
	width = 0			# noqa: F841 pylint: disable=W0612
	bar_size = (0, 0)		# noqa: F841 pylint: disable=W0612
	icon_size = (0, 0)		# noqa: F841 pylint: disable=W0612
	picon_size = (0, 0)		# noqa: F841 pylint: disable=W0612
	font_sizes = [0, 0, 0]          # noqa: F841 pylint: disable=W0612
	row_height = [0, 0, 0, 0, 0]
	line_height = [0, 0, 0, 0, 0]
	font_height = [0, 0, 0]

	template = eval(template_string)

	template_attributes = template["template_attributes"]
	fonts = template_attributes["font_sizes"]
	scaled_fonts = [scale(fonts[0]), scale(fonts[1]), scale(fonts[2])]
	font_height = [scale(fonts[0] + 3), scale(fonts[1] + 3), scale(fonts[2] + 3)]
	template_attributes["font_sizes"] = scaled_fonts
	list_styles = template["list_styles"]
	parseListStyles(list_styles, row_height, line_height)
	template_attributes["row_height"] = row_height
	template_attributes["line_height"] = line_height
	template_attributes["font_height"] = font_height
	template_attributes["start"] = scale(template_attributes["start"])
	template_attributes["spacer"] = scale(template_attributes["spacer"])
	template_attributes["bar_size"] = scale(template_attributes["bar_size"])
	template_attributes["icon_size"] = scale(template_attributes["icon_size"])
	template_attributes["picon_size"] = scale(template_attributes["picon_size"])
	template_attributes["date_width"] = scale(template_attributes["date_width"])
	template_attributes["length_width"] = scale(template_attributes["length_width"])
	template_attributes["progress_width"] = scale(template_attributes["progress_width"])
	template_attributes["yoffs"] = scale(template_attributes["yoffs"])
	logger.info("list_styles: %s", str(list_styles))
	logger.info("template_attributes: %s", str(template_attributes))
	# print_template()
	return list_styles, template_attributes


def print_template():
	logger.debug("print movie list template...")
	data_string = readFile(template_path)
	if data_string:
		_list_styles, template_attributes = parseTemplate(data_string)

		RT_HALIGN_LEFT = "RT_HALIGN_LEFT"			  # noqa: F841 pylint: disable=W0612
		RT_HALIGN_RIGHT = "RT_HALIGN_RIGHT"			  # noqa: F841 pylint: disable=W0612
		RT_HALIGN_CENTER = "RT_HALIGN_CENTER"			  # noqa: F841 pylint: disable=W0612
		width = 1200 - 15					  # noqa: F841 pylint: disable=W0612
		start = template_attributes["start"]			  # noqa: F841 pylint: disable=W0612
		spacer = template_attributes["spacer"]			  # noqa: F841 pylint: disable=W0612
		bar_size = template_attributes["bar_size"]		  # noqa: F841 pylint: disable=W0612
		icon_size = template_attributes["icon_size"]		  # noqa: F841 pylint: disable=W0612
		picon_size = template_attributes["picon_size"]		  # noqa: F841 pylint: disable=W0612
		date_width = template_attributes["date_width"]		  # noqa: F841 pylint: disable=W0612
		length_width = template_attributes["length_width"]	  # noqa: F841 pylint: disable=W0612
		progress_width = template_attributes["progress_width"]	  # noqa: F841 pylint: disable=W0612
		yoffs = template_attributes["yoffs"]			  # noqa: F841 pylint: disable=W0612
		font_height = template_attributes["font_height"]	  # noqa: F841 pylint: disable=W0612
		row_height = template_attributes["row_height"]		  # noqa: F841 pylint: disable=W0612
		lines_per_row = template_attributes["lines_per_row"]	  # noqa: F841 pylint: disable=W0612
		line_height = template_attributes["line_height"]	  # noqa: F841 pylint: disable=W0612

		if pp:
			pp.pprint(eval(data_string))
		else:
			logger.debug(eval(data_string))
	logger.debug("Done.")
