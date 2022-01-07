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


import glob
from enigma import eTimer
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from .Debug import logger
from .SkinUtils import getSkinName, getSkinPath


class BufferingProgressSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent)
		self.skinName = getSkinName("BufferingProgressSummary")
		self["lcd_pic"] = Pixmap()


class BufferingProgress(Screen):

	def __init__(self, session, delay):
		logger.debug("delay: %s", delay)
		Screen.__init__(self, session)
		self.skinName = getSkinName("BufferingProgress")
		self.onShow.append(self.onDialogShow)
		self.update_timer = eTimer()
		self.update_timer_conn = self.update_timer.timeout.connect(self.updateBufferingProgress)
		self.spinner_pic_index = 0
		self.spinner_pics = len(glob.glob(resolveFilename(SCOPE_PLUGINS, "Extensions/TimeshiftCockpit/skin/images/spinner/*.png")))
		self.spinner_pic_delay = int(delay * 1000 / self.spinner_pics)
		self["pic"] = Pixmap()
		logger.debug("spinner_pics: %s, spinner_pic_delay: %s", self.spinner_pics, self.spinner_pic_delay)

	def createSummary(self):
		return BufferingProgressSummary

	def onDialogShow(self):
		logger.debug("...")
		self["pic"].instance.setShowHideAnimation("")
		self.summaries[0]["lcd_pic"].instance.setShowHideAnimation("")
		self.updateBufferingProgress()

	def updateBufferingProgress(self):
		self.spinner_pic_index += 1
		path = getSkinPath("images/spinner/wait%s.png" % self.spinner_pic_index)
		logger.debug("path: %s", path)
		self["pic"].instance.setPixmap(LoadPixmap(path, cached=False))
		self.summaries[0]["lcd_pic"].instance.setPixmap(LoadPixmap(path, cached=False))

		if self.spinner_pic_index < self.spinner_pics:
			self.update_timer.start(self.spinner_pic_delay, True)
		else:
			self.close()
