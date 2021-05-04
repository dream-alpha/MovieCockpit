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
from __init__ import _
from enigma import eTimer
from FileProgress import FileProgress
from FileOp import FILE_OP_DELETE, FILE_OP_MOVE, FILE_OP_COPY
from FileOpManager import FileOpManager

ACTIVITY_TIMER_DELAY = 1000


class FileOpManagerProgress(FileProgress):

	def __init__(self, session):
		logger.debug("...")
		FileProgress.__init__(self, session)
		self.skinName = "FileOpManagerProgress"
		self.setTitle(_("File operation(s)") + " ...")
		self.activity_timer = eTimer()
		self.activity_timer_conn = self.activity_timer.timeout.connect(self.doActivityTimer)
		self.onShow.append(self.onDialogShow)
		self.request_cancel = False
		self.cancelled = False

	def onDialogShow(self):
		logger.debug("...")
		self.execFileOpManagerProgress()

	def cancel(self):
		if self.cancelled or not self.total_files:
			self.exit()
		else:
			logger.debug("trigger")
			self.request_cancel = True
			FileOpManager.getInstance().cancelJobs()

	def exit(self):
		if self.cancelled or not self.total_files:
			logger.debug("close")
			self.close()

	def toggleHide(self):
		if self.total_files and not self.request_cancel:
			self.close(True)

	def checkJobs(self):
		file_name = ""
		file_op = FILE_OP_DELETE
		progress = 0
		jobs = FileOpManager.getInstance().getPendingJobs()
		if jobs:
			job = jobs[0]
			file_name = os.path.basename(job.name)
			file_op = job.file_op
			progress = job.progress
		logger.debug("len(jobs): %d, file_name: %s, file_op: %d, progress: %d", len(jobs), file_name, file_op, progress)
		return len(jobs), file_name, file_op, progress

	def updateProgress(self):
		logger.debug("...")
		self["operation"].setText(self.msg)
		self["name"].setText(self.op_msg)
		self["slider1"].setValue(self.file_progress)
		self["status"].setText(self.status)

	def doActivityTimer(self):
		logger.debug("...")
		self.total_files, self.file_name, self.file_op, self.file_progress = self.checkJobs()
		self.msg = _("Remaining files") + ": %d" % self.total_files
		if self.request_cancel:
			self["key_red"].hide()
			self["key_blue"].hide()
			if self.total_files:
				self["key_green"].hide()
				self.status = _("Cancelling") + "..."
				self.activity_timer.start(ACTIVITY_TIMER_DELAY, True)
			else:
				self["key_green"].show()
				self.op_msg = ""
				self.status = _("Cancelled") + "."
				self.cancelled = True
		else:
			if self.total_files:
				self.status = _("Please wait") + " ..."
				self.op_msg = {FILE_OP_DELETE: _("Deleting"), FILE_OP_MOVE: _("Moving"), FILE_OP_COPY: _("Copying")}[self.file_op]
				self.op_msg += ": " + self.file_name
				self.activity_timer.start(ACTIVITY_TIMER_DELAY, True)
			else:
				self["key_red"].hide()
				self["key_blue"].hide()
				self["key_green"].show()
				self.op_msg = ""
				self.status = _("Done") + "."
				self.file_progress = 0
				self.op_msg = _("No file operation in process")
		self.updateProgress()

	def execFileOpManagerProgress(self):
		self.doActivityTimer()
