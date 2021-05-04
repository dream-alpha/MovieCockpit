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


from About import about
import os
from __init__ import _
from Components.config import config
from Components.ActionMap import HelpableActionMap
from Components.Sources.List import List
from Components.PluginComponent import plugins
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from FileCache import FileCache
from MovieList import MovieList
from Screens.HelpMenu import HelpableScreen
from Plugins.Plugin import PluginDescriptor
from Tools.BoundFunction import boundFunction


MENU_FUNCTIONS = 1
MENU_PLUGINS = 2


class MovieCockpitContextMenu(Screen, HelpableScreen):
	def __init__(self, session, csel, menu_mode, current_dir, service=None):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.csel = csel
		self.menu_mode = menu_mode
		self.current_dir = current_dir
		self.service = service
		self.skinName = "MovieCockpitContextMenu"
		self["title"] = StaticText()
		self["menu"] = List()

		self["actions"] = HelpableActionMap(
			self,
			"CockpitActions",
			{
				"EXIT":	(self.close,			_("Exit")),
				"OK":	(self.ok,			_("Select function")),
				"RED":	(self.close,			_("Cancel")),
				"MENU":	(self.csel.openConfigScreen,	_("Open setup")),
			},
			-1
		)

		menu = []
		if self.menu_mode == MENU_FUNCTIONS:
			self.setTitle(_("Select function"))

			if self.current_dir and not MountCockpit.getInstance().isBookmark(os.path.realpath(self.current_dir)):
				menu.append((_("Home"), (boundFunction(self.csel.changeDir, FileCache.getInstance().getHomeDir()), True)))
				menu.append((_("Directory up"), (boundFunction(self.csel.changeDir, self.current_dir + "/.."), True)))

			menu.append((_("Select all"), (self.csel.selectAll, True)))

			menu.append((_("Delete"), (self.csel.deleteMovies, True)))
			menu.append((_("Move"), (self.csel.moveMovies, True)))
			menu.append((_("Copy"), (self.csel.copyMovies, True)))

			if config.plugins.moviecockpit.trashcan_enable.value:
				menu.append((_("Empty trashcan"), (self.csel.emptyTrashcan, False)))
				menu.append((_("Open trashcan"), (self.csel.openTrashcan, True)))

			menu.append((_("Remove cutlist marker"), (self.csel.removeCutListMarker, True)))

			menu.append((_("Bookmarks"), (self.csel.openBookmarks, False)))

			for list_style in range(len(MovieList.list_styles)):
				menu.append((_(MovieList.list_styles[list_style][1]), (boundFunction(self.csel.movie_list.setListStyle, list_style), True)))

			if config.plugins.moviecockpit.archive_enable.value:
				menu.append((_("Archive"), (self.csel.archiveFiles, True)))
			menu.append((_("Reload cache"), (self.csel.reloadCache, False)))
			menu.append((_("Setup"), (self.csel.openConfigScreen, False)))
			menu.append((_("About"), (boundFunction(about, self.session), False)))
		elif self.menu_mode == MENU_PLUGINS:
			self.setTitle(_("Select plugin"))
			if self.service is not None:
				for plugin in plugins.getPlugins(PluginDescriptor.WHERE_MOVIELIST):
					menu.append((plugin.description, boundFunction(self.execPlugin, plugin)))

		self["menu"].setList(menu)

	def execPlugin(self, plugin):
		plugin(session=self.session, service=self.service)

	def ok(self):
		current_entry = self["menu"].getCurrent()
		if self.menu_mode == MENU_FUNCTIONS:
			current_entry[1][0]()  # execute function
			if current_entry[1][1]:
				self.close()
		else:
			current_entry[1]()  # execute plugin
