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
from Components.config import config, ConfigText
from Tools.Directories import fileExists
from Style import Style
from StyleConfigUtils import loadConfig
from shutil import copy2
from SkinUtils import getSkinPath
from StyleSkin import StyleSkin


def applyPluginStyle():
	is_skin_styled = checkStyled(getSkinPath("skin.xml"))
	logger.info("is_skin_styled: %s", is_skin_styled)
	if is_skin_styled:
		loadStyleConfigFromSkin()
	else:
		loadConfig(config.plugins.moviecockpit.style)
		loadConfig(config.plugins.moviecockpit.preset)
		style = loadStyle(getSkinPath("styles.xml"))
		writeStyle(style, getSkinPath("skin.xml"))


def loadStyleConfigFromSkin():
	logger.info("...")
	conf = getSkinConfig(getSkinPath("skin.xml"))
	for key1 in sorted(conf):
		for key2 in sorted(conf[key1]):
			logger.info("key1: %s, key2: %s, conf: %s", key1, key2, str(conf[key1][key2]))
	for key, value in conf["preset"].iteritems():
		config.plugins.moviecockpit.preset[key] = ConfigText()
		config.plugins.moviecockpit.preset[key].value = value
	config.plugins.moviecockpit.preset.save()
	for key, value in conf["style"].iteritems():
		config.plugins.moviecockpit.style[key] = ConfigText()
		config.plugins.moviecockpit.style[key].value = value
	config.plugins.moviecockpit.style.save()


def getSkinConfig(file_name):
	logger.debug("file_name: %s", file_name)
	if checkStyled(file_name):
		skin = StyleSkin(file_name)
		return skin.getConfig()
	return dict()


def backupSkin():
	src = getSkinPath("skin.xml")
	dst = getSkinPath("skin_org.xml")
	logger.debug("src: %s", src)
	logger.debug("dst: %s", dst)
	dst_path = os.path.dirname(dst)
	if not os.path.exists(dst_path):
		os.makedirs(dst_path)

	if not fileExists(dst) or not checkStyled(src):
		logger.debug("backing up...")
		copy2(src, dst)

	return dst


def restoreSkin():
	dst = getSkinPath("skin.xml")
	src = getSkinPath("skin_org.xml")
	logger.debug("src: %s", src)
	logger.debug("dst: %s", dst)
	config.plugins.moviecockpit.preset.clear()
	config.plugins.moviecockpit.style.clear()
	copy2(src, dst)


def loadStyle(file_name):
	style = Style(file_name)
	style.printInfo()
	return style


def writeStyle(style, file_name):
	logger.debug("file_name %s", file_name)
	logger.debug("%s", str("#" * 80))

	nodes, style_info = style.getSkinComponents()
	for _x in style_info:
		logger.debug("%s", str(_x))

	logger.debug("%s", str("-" * 80))

	backup = backupSkin()

	skin = StyleSkin(backup)
# skin.user_mtime = getStyleUserFileMTime()

# comparing = config.plugins.moviecockpit.debug.value
# if comparing:
	skin.write(file_name.replace(".xml", "_src.xml"))

	skin.style_info = style_info
	skin.applyNodes(nodes)
	skin.write(file_name)

# if comparing:
	skin.write(file_name.replace(".xml", "_dst.xml"))
	logger.debug("%s", str("#" * 80))


def checkStyled(path):
	line_count = 0
	with open(path, "r") as f:
		for line in f:
			if "<style " in line:
				return True
			line_count += 1
			if line_count > 10:
				break
	return False
