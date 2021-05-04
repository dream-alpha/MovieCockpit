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
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from enigma import eTimer, eSize
from ServiceReference import ServiceReference
from Screens.TimerEdit import TimerEditList
from Screens.LocationBox import LocationBox
from Tools.BoundFunction import boundFunction
from enigma import getDesktop
from Components.Sources.MVCServiceEvent import MVCServiceEvent
from ServiceCenter import ServiceCenter
from MovieCockpitContextMenu import MovieCockpitContextMenu
from RecordingUtils import isRecording, stopRecording
from CutList import updateCutList, removeCutListMarks
from FileOp import FILE_OP_DELETE, FILE_OP_MOVE, FILE_OP_COPY, FILE_OP_ERROR_NONE, FILE_OP_ERROR_NO_DISKSPACE
from FileCacheSQL import FILE_IDX_PATH, FILE_IDX_TYPE, FILE_IDX_EXT, FILE_IDX_NAME
from FileCache import FileCache, FILE_TYPE_DIR
from FileCacheLoadProgress import FileCacheLoadProgress
from ServiceUtils import EXT_VIDEO
from ConfigInit import sort_modes
from MovieInfoEPG import MovieInfoEPG
from MovieInfoTMDB import MovieInfoTMDB
from CockpitPlayer import CockpitPlayer
from MovieList import MovieList
from MovieCockpitContextMenu import MENU_FUNCTIONS, MENU_PLUGINS
from MovieListUtils import getService4Path, getFile4Path, createFileList
from ConfigScreen import ConfigScreen
from MovieCockpitActions import Actions
from FileOpManager import FileOpManager
from FileOpManagerProgress import FileOpManagerProgress
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from SkinUtils import getSkinName


instance = None


class MovieCockpitSummary(Screen):

	def __init__(self, session, parent):
		logger.info("...")
		Screen.__init__(self, session, parent)
		self.skinName = "MovieCockpitSummary"


class MovieCockpit(Screen, HelpableScreen, Actions):

	# define static member variables
	def attrgetter(self, default=None):
		attr = self

		def get_any(_self):
			return getattr(MovieCockpit, attr, default)
		return get_any

	def attrsetter(self):
		attr = self

		def set_any(_self, value):
			setattr(MovieCockpit, attr, value)
		return set_any

	color_buttons_level = property(fget=attrgetter('_color_buttons_level', 0), fset=attrsetter('_color_buttons_level'))
	return_path = property(fget=attrgetter('_return_path', None), fset=attrsetter('_return_path'))
	current_sort_mode = property(fget=attrgetter('_current_sort_mode', None), fset=attrsetter('_current_sort_mode'))

	@staticmethod
	def getInstance():
		return instance

	def __init__(self, session, *__):
		logger.info("self.return_path: %s", self.return_path)

		self["list"] = self.movie_list = MovieList(self.current_sort_mode)

		global instance
		instance = self

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		Actions.__init__(self, self)

		self.skinName = getSkinName("MovieCockpit")
		self["actions"] = self.initActions(self, self.return_path, self.skinName != "NoSupport")
		self["mini_tv"] = Pixmap()
		self.enable_mini_tv = False
		self["Service"] = MVCServiceEvent(ServiceCenter.getInstance())
		self.last_service = None
		self["no_support"] = Label()
		self["sort_mode"] = Label()
		self.short_key = True  # used for long / short key press detection
		self.delay_timer = eTimer()
		self.delay_timer_conn = self.delay_timer.timeout.connect(self.updateInfoDelayed)

		self.onShow.append(self.onDialogShow)
		self.onHide.append(self.onDialogHide)
		self.movie_list.onSelectionChanged.append(self.selectionChanged)

		FileOpManager.getInstance().setCallback(self.doFileOpCallback)
		self.updateTitle()

	def onDialogShow(self):
		logger.info("self.return_path: %s", self.return_path)
		logger.debug("self[\"mini_tv\"].instance: %s", self["mini_tv"].instance.size().width())
		self.show()
		self.enable_mini_tv = self["mini_tv"].instance.size().width() > -1
		self.last_service = self.session.nav.getCurrentlyPlayingServiceReference()
		logger.info("self.last_service: %s", self.last_service.toString() if self.last_service else None)
		current_dir = FileCache.getInstance().getHomeDir()
		if not self.movie_list.file_list:
			if not config.plugins.moviecockpit.list_start_home.value and self.return_path:
				current_dir = os.path.dirname(self.return_path)
			self.movie_list.loadList(current_dir, self.return_path)
		else:
			MovieList.lock_list = FileOpManager.getInstance().getLockList()

	def onDialogHide(self):
		logger.info("self.return_path: %s", self.return_path)
		if self.enable_mini_tv:
			self.pigWorkaround()
			self.session.nav.playService(self.last_service)
		self.hide()

	def pigWorkaround(self):
		self.session.nav.stopService()
		desktop_size = getDesktop(0).size()
		self.instance.resize(eSize(*(desktop_size.width(), desktop_size.height())))

	def createSummary(self):
		return MovieCockpitSummary

	def exit(self, reload_moviecockpit=False):
		logger.info("reload_moviecockpit: %s", reload_moviecockpit)
		self.hide()
		self.delay_timer.stop()
		FileOpManager.getInstance().setCallback(None)
		self.close(self.session, reload_moviecockpit)

### key functions

	def goHome(self):
		self.changeDir(FileCache.getInstance().getHomeDir())
		self.movie_list.moveTop()

	def openTimerList(self):
		self.session.open(TimerEditList)

	def toggleDateMount(self):
		config.plugins.moviecockpit.movie_mount_points.value = not config.plugins.moviecockpit.movie_mount_points.value
		config.plugins.moviecockpit.movie_mount_points.save()
		self.movie_list.invalidateList()

	def showMovieInfoEPG(self):
		if not self.short_key:
			self.short_key = True
		else:
			path = self.movie_list.getCurrentPath()
			logger.debug("path: %s", path)
			epg_available = False
			if path and self.movie_list.getCurrentSelection()[FILE_IDX_EXT] in EXT_VIDEO:
				service = getService4Path(self.movie_list.file_list, path)
				if service:
					event = ServiceCenter.getInstance().info(service).getEvent()
					if event:
						epg_available = True
						self.session.open(MovieInfoEPG, event, ServiceReference(service))
			if not epg_available:
				self.session.open(
					MessageBox,
					_("No EPG info available"),
					MessageBox.TYPE_INFO
				)

	def showMovieInfoTMDB(self):
		self.short_key = False
		path = self.movie_list.getCurrentPath()
		afile = getFile4Path(self.movie_list.file_list, path)
		if afile and afile[FILE_IDX_EXT] in EXT_VIDEO:
			name = afile[FILE_IDX_NAME]
			self.session.open(MovieInfoTMDB, path, name)

	def changeDir(self, target_dir):
		logger.debug("target_dir: %s", target_dir)
		if target_dir:
			if os.path.basename(target_dir) == "..":
				# open parent folder
				target_dir = os.path.abspath(target_dir)
			self.movie_list.loadList(target_dir, self.return_path)
			self.setTrashcanActions(self, target_dir)

	def openBookmarks(self):
		self.selectDirectory(
			self.openBookmarksCallback,
			_("Bookmarks")
		)

	def openBookmarksCallback(self, path):
		logger.debug("path: %s", path)
		MountCockpit.getInstance().registerBookmarks(ID, config.plugins.moviecockpit.bookmarks.value)
		current_dir = self.movie_list.getCurrentDir()
		mount_point = MountCockpit.getInstance().getMountPoint(ID, current_dir)
		if not mount_point:
			current_dir = FileCache.getInstance().getHomeDir()
		self.movie_list.loadList(current_dir, self.return_path)

	def toggleSelection(self):
		if not self.short_key:
			self.short_key = True
		else:
			self.movie_list.toggleSelection()
			self.movie_list.moveDown()

	### display functions

	def updateInfo(self):
		logger.debug("...")
		if self.movie_list.file_list:
			self.resetInfo()
			self.updateTitle()
			self.updateSortModeDisplay()
			self.delay_timer.start(int(config.plugins.moviecockpit.movie_description_delay.value), True)

	def updateInfoDelayed(self):
		logger.debug("...")
		path = self.movie_list.getCurrentPath()
		if path:
			service = getService4Path(self.movie_list.file_list, path)
			self["Service"].newService(service)

	def resetInfo(self):
		logger.debug("...")
		self.delay_timer.stop()
		self["Service"].newService(None)

	def updateTitle(self):
		title = "MovieCockpit"
		current_dir = self.movie_list.getCurrentDir()
		if current_dir:
			title += " - "
			title += _("trashcan") if os.path.basename(current_dir) == "trashcan" else _("Recordings")
		self.setTitle(title)

	def updateSortModeDisplay(self):
		self["sort_mode"].setText(_("Sort mode") + ": " + sort_modes[MovieList.current_sort_mode][1])

	### sort functions

	def toggleSortMode(self):
		self.movie_list.toggleSortMode()
		self.updateInfoSortModeDisplay()

	def toggleSortOrder(self):
		self.movie_list.toggleSortOder()
		self.updateSortModeDisplay()

	### progress functions

	def resetProgress(self):
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			updateCutList(path, play=0)
		self.movie_list.loadList(self.movie_list.getCurrentDir(), self.return_path)

	### select functions

	def selectAll(self):
		self.movie_list.selectAll()

	def unselectAll(self):
		self.short_key = False
		self.movie_list.unselectAll()

	def selectionChanged(self):
		logger.debug("...")
		return_path = self.movie_list.getCurrentPath()
		if return_path:
			self.return_path = return_path
		self.updateInfo()

	def selectedEntry(self):
		path = self.movie_list.getCurrentPath()
		if path:
			if path not in MovieList.lock_list:
				if self.movie_list.getCurrentSelection()[FILE_IDX_TYPE] == FILE_TYPE_DIR:
					self.changeDir(path)
				else:
					if os.path.exists(path):
						if self.enable_mini_tv:
							self.pigWorkaround()
						self.openPlayer(path)
					else:
						self.session.open(
							MessageBox,
							_("Video filex  does not exist") + "\n" + path,
							MessageBox.TYPE_ERROR,
							10
						)
			else:
				self.showFileOpManagerProgress()

	### player

	def playerCallback(self, reload_moviecockpit):
		logger.info("reload_moviecockpit: %s", reload_moviecockpit)
		if not reload_moviecockpit:
			self.exit(reload_moviecockpit)
		else:
			logger.info("return_path: %s", self.return_path)
			self.movie_list.loadList(self.movie_list.getCurrentDir(), self.return_path)

	def openPlayer(self, path):
		logger.info("path: %s", path)
		self.session.openWithCallback(
			self.playerCallback,
			CockpitPlayer,
			getService4Path(self.movie_list.file_list, path),
		)

	### context menu

	def openContextMenu(self):
		if not self.short_key:
			self.short_key = True
		else:
			self.session.open(
				MovieCockpitContextMenu,
				self,
				MENU_FUNCTIONS,
				self.movie_list.getCurrentDir(),
				None
			)

	def openPluginsMenu(self):
		self.short_key = False
		self.session.open(
			MovieCockpitContextMenu,
			self,
			MENU_PLUGINS,
			self.movie_list.getCurrentDir(),
			getService4Path(self.movie_list.file_list, self.return_path)
		)

	### config

	def openConfigScreen(self):
		self.session.openWithCallback(self.openConfigScreenCallback, ConfigScreen)

	def openConfigScreenCallback(self, reload_moviecockpit=False):
		logger.debug("reload_moviecockpit: %s", reload_moviecockpit)
		if reload_moviecockpit:
			self.exit(True)

	### cache

	def reloadCache(self):
		self.session.openWithCallback(
			self.reloadCacheConfirmed,
			MessageBox,
			_("Do you really want to reload the SQL cache?"),
			MessageBox.TYPE_YESNO
		)

	def reloadCacheConfirmed(self, answer):
		if answer:
			self.session.openWithCallback(self.reloadCacheCallback, FileCacheLoadProgress)

	def reloadCacheCallback(self):
		logger.debug("...")
		reload_dir = FileCache.getInstance().getHomeDir()
		if self.return_path:
			reload_dir = os.path.dirname(self.return_path)
		self.movie_list.loadList(reload_dir, self.return_path)

### movie ops

	### utils

	def selectDirectory(self, callback, title):
		logger.debug("bookmarks: %s", config.plugins.moviecockpit.bookmarks.value)
		self.session.openWithCallback(
			callback,
			LocationBox,
			windowTitle=title,
			text=_("Select directory"),
			currDir=FileCache.getInstance().getHomeDir(),
			bookmarks=config.plugins.moviecockpit.bookmarks,
			autoAdd=False,
			editDir=True,
			inhibitDirs=["/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"],
			minFree=None
		)

	### recording

	def stopRecordings(self):
		self.file_ops_list = []
		self.file_delete_list = []
		self.file_move_list = []
		self.recordings_to_stop = []
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			if isRecording(path):
				self.recordings_to_stop.append(path)
		if self.recordings_to_stop:
			self.stopRecordingsQuery()

	def stopRecordingsConfirmed(self, answer):
		if answer:
			for path in self.recordings_to_stop:
				stopRecording(path)
			self.deleteMoviesQuery()

	def stopRecordingsQuery(self):
		file_names = self.createMovieList(self.recordings_to_stop)
		self.session.openWithCallback(
			self.stopRecordingsConfirmed,
			MessageBox,
			_("Stop recording(s)") + "?\n" + file_names,
			MessageBox.TYPE_YESNO
		)

	### file I/O functions

	### utils

	def createMovieList(self, file_list):
		file_names = ""
		movies = len(file_list)
		for i, path in enumerate(file_list):
			if i >= 5 and movies > 5:  # only show first 5 entries in file_list
				file_names += " ..."
				break
			file_name = os.path.basename(path)
			file_names += "\n" + file_name
		return file_names

	### Delete

	def deleteMovies(self):
		self.file_ops_list = []
		self.file_delete_list = []
		self.file_move_list = []
		self.recordings_to_stop = []
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			logger.debug("path: %s", path)
			file_type = getFile4Path(self.movie_list.file_list, path)[FILE_IDX_TYPE]
			directory = os.path.dirname(path)
			if not config.plugins.moviecockpit.trashcan_enable.value or os.path.basename(directory) == "trashcan":
				self.file_ops_list.append((FILE_OP_DELETE, path, None, file_type))
				self.file_delete_list.append(path)
			else:
				trashcan_path = MountCockpit.getInstance().getBookmark(ID, path) + "/trashcan"
				self.file_ops_list.append((FILE_OP_MOVE, path, trashcan_path, file_type))
				self.file_move_list.append(path)

			if isRecording(path):
				self.recordings_to_stop.append(path)

		if self.recordings_to_stop:
			self.stopRecordingsQuery()
		else:
			self.deleteMoviesQuery()

	def deleteMoviesQuery(self, _answer=True):
		if self.file_delete_list:
			file_names = self.createMovieList(self.file_delete_list)
			msg = _("Permanently delete the selected video file(s) or dir(s)") + "?\n" + file_names
			self.session.openWithCallback(
				self.deleteMoviesConfirmed,
				MessageBox,
				msg,
				MessageBox.TYPE_YESNO
			)
		else:
			self.deleteMoviesConfirmed(True)

	def deleteMoviesConfirmed(self, answer):
		logger.debug("answer: %s", answer)
		if answer:
			self.execFileOps(self.file_ops_list)
		else:
			self.movie_list.unselectAll()

	###  restore

	def restoreMovies(self):
		file_ops_list = []
		selection_list = self.movie_list.getSelectionList()
		if selection_list:
			for path in selection_list:
				if not isRecording(path):
					file_type = getFile4Path(self.movie_list.file_list, path)[FILE_IDX_TYPE]
					trashcan_dir = os.path.dirname(path)
					movie_dir = os.path.dirname(trashcan_dir)
					file_ops_list.append((FILE_OP_MOVE, path, os.path.normpath(movie_dir), file_type))
			logger.debug("file_ops_list: %s", file_ops_list)
			self.execFileOps(file_ops_list)

	###  move

	def moveMovies(self):
		if self.movie_list.getSelectionList():
			self.selectDirectory(
				boundFunction(self.selectedTargetDir, FILE_OP_MOVE),
				_("Move file(s)")
			)

	### copy

	def copyMovies(self):
		if self.movie_list.getSelectionList():
			self.selectDirectory(
				boundFunction(self.selectedTargetDir, FILE_OP_COPY),
				_("Copy file(s)"),
			)

	### move or copy

	def selectedTargetDir(self, file_op, target_dir):
		logger.debug("...")
		if target_dir:
			if not MountCockpit.getInstance().getMountPoint(ID, target_dir):
				self.session.open(
					MessageBox,
					target_dir + " " + _("is not mounted"),
					MessageBox.TYPE_ERROR
				)
			else:
				active_recordings_list = []
				file_ops_list = []
				selection_list = self.movie_list.getSelectionList()
				for path in selection_list:
					if not isRecording(path):
						file_type = getFile4Path(self.movie_list.file_list, path)[FILE_IDX_TYPE]
						file_ops_list.append((file_op, path, os.path.normpath(target_dir), file_type))
						logger.debug("file_ops_list: %s", file_ops_list)
						self.execFileOps(file_ops_list)
					else:
						active_recordings_list.append(path)
				if active_recordings_list:
					file_names = self.createMovieList(active_recordings_list)
					msg = _("Can't move recordings") + "\n" + file_names if file_op == FILE_OP_MOVE else _("Can't copy recordings") + "\n" + file_names
					self.session.open(
						MessageBox,
						msg,
						MessageBox.TYPE_INFO
					)
		self.movie_list.unselectAll()

	# archive

	def archiveFiles(self):
		archive_source_dir = config.plugins.moviecockpit.archive_source_dir.value
		archive_target_dir = config.plugins.moviecockpit.archive_target_dir.value
		logger.debug("archive_source_dir: %s, archive_target_dir: %s", archive_source_dir, archive_target_dir)
		if os.path.exists(archive_source_dir) and os.path.exists(archive_target_dir):
			FileOpManager.getInstance().archive(self.doFileOpCallback)
			self.showFileOpManagerProgress()
		else:
			self.session.open(
				MessageBox,
				_("Archive source and/or target directory does not exist, please configure directories in setup."),
				MessageBox.TYPE_INFO
			)

	# trashcan

	def openTrashcan(self):
		logger.debug("...")
		self.changeDir(FileCache.getInstance().getHomeDir() + "/trashcan")

	def emptyTrashcan(self):
		self.session.openWithCallback(
			self.emptyTrashcanConfirmed,
			MessageBox,
			_("Permanently delete all files in trashcan?"),
			MessageBox.TYPE_YESNO
		)

	def emptyTrashcanConfirmed(self, answer):
		if answer:
			file_ops_list = []
			file_list = createFileList(FileCache.getInstance().getHomeDir() + "/trashcan")
			for afile in file_list:
				path = afile[FILE_IDX_PATH]
				file_type = afile[FILE_IDX_TYPE]
				file_ops_list.append((FILE_OP_DELETE, path, None, file_type))
			logger.debug("file_ops_list: %s", file_ops_list)
			self.execFileOps(file_ops_list)

	### cutlist

	def removeCutListMarker(self):
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			removeCutListMarks(path)
			self.movie_list.unselectPath(path)
		logger.debug("removed marker")

	### file ops

	def execFileOps(self, file_ops_list):
		logger.info("file_ops_list: %s", file_ops_list)
		if file_ops_list:
			for file_op, path, target_dir, file_type in file_ops_list:
				FileOpManager.getInstance().doFileOp(file_op, path, target_dir, file_type, self.doFileOpCallback)
			MovieList.lock_list = FileOpManager.getInstance().getLockList()
			self.movie_list.invalidateList()
		else:
			self.movie_list.unselectAll()

	def doFileOpCallback(self, file_op, path, target_dir, file_type, error):
		logger.info("file_op: %s, path: %s, target_dir: %s, file_type: %s, error: %s", file_op, path, target_dir, file_type, error)
		if error == FILE_OP_ERROR_NONE:
			self.movie_list.loadList(os.path.dirname(self.return_path), self.return_path)
		else:
			self.movie_list.unselectPath(path)
			self.movie_list.invalidateList()
			if error == FILE_OP_ERROR_NO_DISKSPACE:
				self.session.open(
					MessageBox,
					_("Not enough space in target directory for video file") + ":\n" + path,
					MessageBox.TYPE_ERROR,
					10
				)

	def showFileOpManagerProgress(self):
		self.session.openWithCallback(self.showFileOpManagerProgressCallback, FileOpManagerProgress)

	def showFileOpManagerProgressCallback(self, leave_moviecockpit=False):
		logger.debug("leave_moviecockpit: %s", leave_moviecockpit)
		if leave_moviecockpit:
			self.exit()

### bookmark utils

	def getBookmarksSpaceInfo(self):
		return MountCockpit.getInstance().getBookmarksSpaceInfo(ID)
