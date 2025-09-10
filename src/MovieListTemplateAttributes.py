#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
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
from Debug import logger


def scaleTemplateAttributes(list_styles, template_attributes, scaling_factor):

    def scale(number):
        if isinstance(number, int):
            result = int(round(scaling_factor * number))
        elif isinstance(number, list):
            result = []
            for item in number:
                result.append(scale(item))
        elif isinstance(number, tuple):
            result = []
            for item in number:
                result.append(scale(item))
            result = tuple(result)
        else:
            result = number
        return result

    row_height = [-1] * len(list_styles)
    line_height = [-1] * len(list_styles)
    for index, list_style in six.iteritems(list_styles):
        row_height[index] = list_style[2]
        line_height[index] = list_style[2] / list_style[3]
    template_attributes["row_height"] = row_height
    template_attributes["line_height"] = line_height
    template_attributes = scale(template_attributes)

    logger.info("template_attributes: %s", template_attributes)
    return template_attributes
