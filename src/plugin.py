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


import os
from Debug import logger
from __init__ import _
from Version import ID, VERSION
from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar
from Tools.BoundFunction import boundFunction
from FileCache import FileCache
from Recording import Recording
from SkinUtils import initPluginSkinPath, loadPluginSkin
from Trashcan import Trashcan
from ConfigScreen import ConfigScreen
from ConfigScreenInit import ConfigScreenInit
from Debug import createLogFile
from StyleOps import applyPluginStyle
from MovieCockpit import MovieCockpit
import Screens.Standby
import Standby
from FileOpManager import FileOpManager
from FileUtils import deleteFile, touchFile
from ConfigInit import ConfigInit
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Plugins.SystemPlugins.MountCockpit.MountUtils import getBookmarkSpaceInfo


def initBookmarks():
	logger.info("...")
	bookmarks = []
	for video_dir in config.movielist.videodirs.value:
		bookmarks.append(os.path.normpath(video_dir))
	logger.debug("bookmarks: %s", bookmarks)
	return bookmarks


def openSettings(session, **__):
	logger.info("...")
	session.open(ConfigScreen)


def openMovieCockpit(session, **__):
	logger.info("...")
	session.openWithCallback(reloadMovieCockpit, MovieCockpit)


def reloadMovieCockpit(session=None, reload_moviecockpit=False):
	if reload_moviecockpit:
		logger.info("...")
		openMovieCockpit(session)


def enteringStandby(reason):
	logger.info("reason: %s, count: %d", reason, config.misc.standbyCounter.value)
	if Screens.Standby.inStandby and config.misc.standbyCounter.value == 1 and config.plugins.moviecockpit.archive_enable.value:
		Screens.Standby.inStandby.onClose.append(leavingStandby)
		used_percent, _used, _free = getBookmarkSpaceInfo(config.plugins.moviecockpit.archive_target_dir.value)
		if used_percent <= 90:
			FileOpManager.getInstance().archive(None)


def leavingStandby():
	logger.info("...")
	if config.misc.standbyCounter.value == 1 and config.plugins.moviecockpit.archive_enable.value:
		file_op_manager = FileOpManager.getInstance()
		jobs = len(file_op_manager.getPendingJobs())
		if jobs:
			file_op_manager.cancelJobs()


def autostart(reason, **kwargs):
	if reason == 0:  # startup
		if "session" in kwargs:
			logger.info("+++ Version: %s starts...", VERSION)
			logger.info("reason: %s", reason)
			session = kwargs["session"]
			touchFile("/etc/enigma2/.mvc")
			launch_key = config.plugins.moviecockpit.launch_key.value
			if launch_key == "showMovies":
				InfoBar.showMovies = boundFunction(openMovieCockpit, session)
			elif launch_key == "showTv":
				InfoBar.showTv = boundFunction(openMovieCockpit, session)
			elif launch_key == "showRadio":
				InfoBar.showRadio = boundFunction(openMovieCockpit, session)
			elif launch_key == "openQuickbutton":
				InfoBar.openQuickbutton = boundFunction(openMovieCockpit, session)
			elif launch_key == "startTimeshift":
				InfoBar.startTimeshift = boundFunction(openMovieCockpit, session)
			ConfigScreenInit.setEPGLanguage(config.plugins.moviecockpit.epglang)
			MountCockpit.getInstance().registerBookmarks(ID, config.plugins.moviecockpit.bookmarks.value)
			Recording()
			FileCache.getInstance()
			Trashcan.getInstance()
			initPluginSkinPath()
			applyPluginStyle()
			loadPluginSkin("skin.xml")
	elif reason == 1:  # shutdown
		logger.info("--- shutdown")
		if not os.path.exists("/etc/enigma2/.moviecockpit"):
			FileCache.getInstance().closeDatabase()
		deleteFile("/etc/enigma2/.mvc")
	else:
		logger.info("reason not handled: %s", reason)


def Plugins(**__):
	logger.info("+++ Plugins")
	ConfigInit()
	if not config.plugins.moviecockpit.bookmarks.value:
		config.plugins.moviecockpit.bookmarks.value = initBookmarks()
	if os.path.exists("/etc/enigma2/.mvc"):
		createLogFile()
	config.misc.standbyCounter.addNotifier(enteringStandby, initial_call=False)

	Screens.Standby.TryQuitMainloop = Standby.TryQuitMainloop

	descriptors = []
	descriptors.append(
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_SESSIONSTART,
				PluginDescriptor.WHERE_AUTOSTART
			],
			fnc=autostart))

	if config.plugins.moviecockpit.extmenu_settings.value:
		descriptors.append(
			PluginDescriptor(
				name="MovieCockpit" + " - " + _("Setup"),
				description=_("Open setup"),
				icon="MovieCockpit.svg",
				where=[
					PluginDescriptor.WHERE_PLUGINMENU,
					PluginDescriptor.WHERE_EXTENSIONSMENU
				],
				fnc=openSettings
			)
		)

	if config.plugins.moviecockpit.extmenu_plugin.value:
		descriptors.append(
			PluginDescriptor(
				name="MovieCockpit",
				description=_("Manage recordings"),
				icon="MovieCockpit.svg",
				where=[
					PluginDescriptor.WHERE_PLUGINMENU,
					PluginDescriptor.WHERE_EXTENSIONSMENU
				],
				fnc=openMovieCockpit
			)
		)
	return descriptors
