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
from Components.config import config
from FileCacheSQL import FILE_IDX_TYPE, FILE_IDX_PATH
from FileCache import FILE_TYPE_FILE
from MovieListUtils import createFileList
from RecordingUtils import isRecording
from Components.Task import Job, job_manager
from FileOpManagerTask import FileOpManagerTask
from FileOp import FileOp, FILE_OP_MOVE, FILE_OP_COPY
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit

instance = None


class FileOpManager(FileOp):

	def __init__(self):
		FileOp.__init__(self)
		self.callback = None

	@staticmethod
	def getInstance():
		global instance
		if instance is None:
			instance = FileOpManager()
		return instance

	def setCallback(self, callback):
		self.callback = callback

### jobs functions

	def getLockList(self):
		lock_list = {}
		jobs = self.getPendingJobs()
		for job in jobs:
			lock_list[job.name] = job.file_op
		logger.debug("lock_list: %s", str(lock_list))
		return lock_list

	def addJob(self, file_op, path, target_dir, file_type, callback):
		self.callback = callback
		job = Job(path)
		job.file_op = file_op
		jobs = job_manager.getPendingJobs()
		add = True
		for ajob in jobs:
			if ajob.name == job.name:
				add = False
				break
		if add:
			FileOpManagerTask(job, file_op, path, target_dir, file_type, self.callbackJob)
			job_manager.AddJob(job)

	def callbackJob(self, file_op, path, target_dir, file_type, error):
		logger.debug("path: %s, error: %s, callback: %s", path, error, self.callback)
		if self.callback:
			if error:
				job_manager.active_jobs = []
			self.callback(file_op, path, target_dir, file_type, error)

	def cancelJobs(self):
		logger.debug("...")
		job_manager.active_jobs = []
		job_manager.active_job.abort()

	def getPendingJobs(self):
		return job_manager.getPendingJobs()

### fileopmanager functions

	def doFileOp(self, file_op, path, target_dir, file_type, callback):
		logger.debug("file_op: %s, path: %s, target_dir: %s, file_type: %s", file_op, path, target_dir, file_type)
		if target_dir and (file_op == FILE_OP_COPY or (file_op == FILE_OP_MOVE and MountCockpit.getInstance().getMountPoint(ID, target_dir) != MountCockpit.getInstance().getMountPoint(ID, path))):
			self.addJob(file_op, path, target_dir, file_type, callback)
		else:
			self.execFileOp(file_op, path, target_dir, file_type, callback)

	def archive(self, callback):
		archive_source_dir = config.plugins.moviecockpit.archive_source_dir.value
		archive_target_dir = config.plugins.moviecockpit.archive_target_dir.value
		logger.info("archive_source_dir: %s, archive_target_dir: %s", archive_source_dir, archive_target_dir)
		if os.path.exists(archive_source_dir) and os.path.exists(archive_target_dir):
			file_list = createFileList(archive_source_dir, False)
			for afile in file_list:
				if afile[FILE_IDX_TYPE] == FILE_TYPE_FILE and not isRecording(afile[FILE_IDX_PATH]):
					logger.debug("path: %s", afile[FILE_IDX_PATH])
					self.addJob(FILE_OP_MOVE, afile[FILE_IDX_PATH], archive_target_dir, FILE_TYPE_FILE, callback)
		else:
			logger.error("archive_source_dir and/or archive_target_dir does not exist.")
