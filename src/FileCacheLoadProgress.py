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
from Version import ID
import os
from __init__ import _
from DelayTimer import DelayTimer
from FileCache import FileCache
from FileProgress import FileProgress
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit


class FileCacheLoadProgress(FileProgress):

	def __init__(self, session):
		logger.debug("__init__")
		FileProgress.__init__(self, session)
		self.skinName = "FileCacheLoadProgress"
		self.setTitle(_("File cache reload") + " ...")
		self.execution_list = []
		self.onShow.append(self.onDialogShow)

	def onDialogShow(self):
		logger.debug("...")
		DelayTimer(100, self.execFileCacheLoadProgress)

	def doFileOp(self, afile):
		path, file_type = afile
		self.file_name = os.path.basename(path)
		self.status = _("Please wait") + " ..."
		self.updateProgress()
		FileCache.getInstance().loadDatabaseFile(path, file_type)
		DelayTimer(10, self.nextFileOp)

	def execFileCacheLoadProgress(self):
		logger.info("...")
		self.status = _("Initializing") + " ..."
		self.updateProgress()
		FileCache.getInstance().clearDatabase()
		bookmarks = MountCockpit.getInstance().getMountedBookmarks(ID)
		self.execution_list = FileCache.getInstance().getDirsLoadList(bookmarks)
		self.total_files = len(self.execution_list)
		DelayTimer(10, self.nextFileOp)
