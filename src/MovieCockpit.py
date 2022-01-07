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


import os
from enigma import eTimer
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.COCServiceEvent import COCServiceEvent
from Components.Sources.COCDiskSpace import COCDiskSpace
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.TimerEdit import TimerEditList
from Screens.LocationBox import LocationBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.BoundFunction import boundFunction
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from Plugins.SystemPlugins.CacheCockpit.Recording import Recording
from Plugins.SystemPlugins.SocketCockpit.SocketCockpit import SocketCockpit
try:
	from Plugins.Extensions.TMDBCockpit.ScreenMain import ScreenMain
	tmdb_plugin = True
except ImportError:
	tmdb_plugin = False
from .Debug import logger
from .Version import ID
from .__init__ import _
from .CockpitContextMenu import CockpitContextMenu, MENU_FUNCTIONS, MENU_PLUGINS
from .RecordingUtils import isRecording, stopRecording
from .CutList import CutList
from .FileManagerUtils import FILE_OP_DELETE, FILE_OP_MOVE, FILE_OP_COPY, FILE_OP_LOAD, FILE_OP_ERROR_NONE, FILE_OP_ERROR_NO_DISKSPACE
from .FileManagerUtils import FILE_TYPE_DIR, FILE_TYPE_LINK, FILE_TYPE_DELETED, FILE_IDX_DIR, FILE_IDX_TYPE, FILE_IDX_PATH, FILE_IDX_EXT, FILE_IDX_NAME
from .ServiceUtils import ALL_VIDEO, getService
from .ConfigInit import sort_modes
from .MovieInfoEPG import MovieInfoEPG
from .CockpitPlayer import CockpitPlayer
from .MovieList import MovieList
from .ConfigScreen import ConfigScreen
from .MovieCockpitActions import Actions
from .FileManagerProgress import FileManagerProgress
from .SkinUtils import getSkinName
from .Loading import Loading
from .RecordingInfo import RecordingInfo
from .BufferingProgress import BufferingProgress
from .FileUtils import createDirectory


class MovieCockpitSummary(Screen):

	def __init__(self, session, parent):
		logger.info("...")
		Screen.__init__(self, session, parent)
		self.skinName = "MVCMovieCockpitSummary"
		self["lcd_pic_loading"] = Pixmap()
		self["background"] = Pixmap()


class MovieCockpit(Screen, HelpableScreen, Actions, CutList):

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

	color_buttons_level = property(attrgetter('_color_buttons_level', 0), attrsetter('_color_buttons_level'))
	return_path = property(attrgetter('_return_path', ""), attrsetter('_return_path'))
	return_dir = property(attrgetter('_return_dir', ""), attrsetter('_return_dir'))

	def __init__(self, session):
		if os.path.basename(self.return_dir) == "trashcan":
			self.return_dir = os.path.dirname(self.return_dir)
			self.return_path = ""
		logger.info("self.return_dir: %s, self.return_path: %s", self.return_dir, self.return_path)
		self["list"] = self.movie_list = MovieList()

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		Actions.__init__(self, self)
		CutList.__init__(self)

		self.skinName = getSkinName("MovieCockpit")
		self["actions"] = self.initActions(self)
		self["sort_mode"] = Label()
		self.loading = Loading(self, self.summaries)

		self["Service"] = COCServiceEvent(self.movie_list)
		self["DiskSpace"] = COCDiskSpace(self)

		self.last_service = None
		self.short_key = True  # used for long / short key press detection
		self.delay_timer = eTimer()
		self.delay_timer_conn = self.delay_timer.timeout.connect(self.updateInfoDelayed)

		self.onShow.append(self.onDialogShow)
		self.onHide.append(self.onDialogHide)
		self.movie_list.onSelectionChanged.append(self.selectionChanged)
		self.updateTitle()

	def onDialogShow(self):
		logger.info("self.return_path: %s", self.return_path)
		self.last_service = self.session.nav.getCurrentlyPlayingServiceReference()
		logger.info("self.last_service: %s", self.last_service.toString() if self.last_service else None)
		self.loading.start()
		FileManager.getInstance().onDatabaseLoaded(self.loadList)

	def loadList(self):
		logger.info("return_dir: %s, return_path: %s", self.return_dir, self.return_path)
		self.loading.stop()
		if not self.movie_list.file_list:
			logger.debug("file_list is empty")
			if config.plugins.moviecockpit.list_start_home.value:
				self.return_dir = MountCockpit.getInstance().getHomeDir(ID)
				self.return_path = ""
		logger.debug("return_dir: %s, return_path: %s", self.return_dir, self.return_path)
		self.movie_list.loadList(self.return_dir, self.return_path)
		self.setTrashcanActions(self, self.movie_list.getCurrentDir())
		self.updateInfo()

	def onDialogHide(self):
		logger.info("self.return_path: %s", self.return_path)
		FileManager.getInstance().onDatabaseLoaded()

	def createSummary(self):
		return MovieCockpitSummary

	def exit(self, reload_moviecockpit=False):
		logger.info("reload_moviecockpit: %s", reload_moviecockpit)
		self.delay_timer.stop()
		self.close(self.session, reload_moviecockpit)

	def goUp(self):
		if not self.short_key:
			self.short_key = True
		else:
			current_dir = self.movie_list.getCurrentDir()
			bookmarks = MountCockpit.getInstance().getMountedBookmarks(ID)
			if current_dir not in bookmarks:
				target_dir = os.path.dirname(current_dir)
				self.changeDir(target_dir, current_dir)
			else:
				self.goHome()

	def goHome(self):
		self.short_key = False
		self.changeDir(MountCockpit.getInstance().getHomeDir(ID))

	def openTimerList(self):
		self.session.open(TimerEditList)

	def toggleDateMount(self):
		config.plugins.moviecockpit.list_show_mount_points.value = not config.plugins.moviecockpit.list_show_mount_points.value
		config.plugins.moviecockpit.list_show_mount_points.save()
		self.movie_list.invalidateList()

	def showMovieInfoEPG(self):
		if not self.short_key:
			self.short_key = True
		else:
			afile = self.movie_list.getCurrentSelection()
			if afile and afile[FILE_IDX_EXT] in ALL_VIDEO:
				service = getService(afile[FILE_IDX_PATH], afile[FILE_IDX_NAME])
				self.session.openWithCallback(self.showMovieInfoEPGCallback, MovieInfoEPG, afile[FILE_IDX_NAME], service, self.movie_list, tmdb_plugin)
			else:
				self.session.open(
					MessageBox,
					_("No event info available"),
					MessageBox.TYPE_INFO
				)

	def showMovieInfoEPGCallback(self, result=""):
		if result == "tmdb":
			self.showMovieInfoTMDB()

	def showMovieInfoTMDB(self):
		self.short_key = False
		path = name = ""
		afile = self.movie_list.getCurrentSelection()
		if afile:
			if afile[FILE_IDX_EXT] in ALL_VIDEO:
				path = afile[FILE_IDX_PATH]
				name = afile[FILE_IDX_NAME]
			if afile[FILE_IDX_TYPE] == FILE_TYPE_DIR and afile[FILE_IDX_NAME] != "..":
				path = afile[FILE_IDX_PATH]
				name = afile[FILE_IDX_NAME]
			if path and name and tmdb_plugin:
				service = getService(path, name)
				self.session.openWithCallback(self.showMovieInfoTMDBCallback, ScreenMain, service, 1)
			else:
				self.session.open(
					MessageBox,
					_("TMDB plugin is not installed."),
					MessageBox.TYPE_INFO
				)
		else:
			self.session.open(
				MessageBox,
				_("No event info available"),
				MessageBox.TYPE_INFO
			)

	def showMovieInfoTMDBCallback(self, reload):
		logger.info("reload: %s", reload)
		if reload:
			afile = self.movie_list.getCurrentSelection()
			if afile:
				FileManager.getInstance().loadDatabaseFile(afile[FILE_IDX_PATH])

	def showRecordingInfo(self):
		afile = self.movie_list.getCurrentSelection()
		self.session.open(RecordingInfo, afile)

	def changeDir(self, target_dir, target_path=""):
		logger.debug("target_dir: %s, target_path: %s", target_dir, target_path)
		if not target_path:
			target_path = target_dir
		if target_dir:
			if os.path.basename(target_dir) == "..":
				target_dir = os.path.abspath(target_dir)
				target_path = os.path.dirname(target_path)
			self.movie_list.loadList(target_dir, target_path)
			self.setTrashcanActions(self, target_dir)

	def openBookmarks(self):
		self.selectDirectory(
			self.openBookmarksCallback,
			_("Bookmarks")
		)

	def openBookmarksCallback(self, path, _selection_list=None):
		logger.debug("path: %s", path)
		bookmarks = []
		for bookmark in config.plugins.moviecockpit.bookmarks.value:
			bookmarks.append(os.path.normpath(bookmark))
		config.plugins.moviecockpit.bookmarks.value = bookmarks[:]
		config.plugins.moviecockpit.bookmarks.save()
		MountCockpit.getInstance().registerBookmarks(ID, config.plugins.moviecockpit.bookmarks.value)
		if not MountCockpit.getInstance().getBookmark(ID, self.return_dir):
			self.return_dir = MountCockpit.getInstance().getHomeDir(ID)
		self.movie_list.loadList(self.return_dir, self.return_path)

	def toggleSelection(self):
		if not self.short_key:
			self.short_key = True
		else:
			self.movie_list.toggleSelection()

	def updateInfo(self):
		logger.debug("...")
		self.delay_timer.stop()
		self["Service"].newService(None)
		if self.movie_list.file_list:
			self.updateTitle()
			self.updateSortModeDisplay()
			self.delay_timer.start(int(config.plugins.moviecockpit.movie_description_delay.value), True)

	def updateInfoDelayed(self):
		logger.debug("...")
		afile = self.movie_list.getCurrentSelection()
		if afile:
			path = afile[FILE_IDX_PATH]
			name = afile[FILE_IDX_NAME]
			service = getService(path, name)
			self["Service"].newService(service)

	def updateTitle(self):
		title = "MovieCockpit"
		current_dir = self.movie_list.getCurrentDir()
		if current_dir:
			title_dir = ""
			title += " - "
			if "trashcan" in current_dir:
				title += _("trashcan")
			else:
				title += _("Videos")
				bookmarks = MountCockpit.getInstance().getMountedBookmarks(ID)
				for bookmark in bookmarks:
					if current_dir.startswith(bookmark):
						title_dir = current_dir[len(bookmark) + 1:]
				if title_dir:
					title += " - " + title_dir
		self.setTitle(title)

	def updateSortModeDisplay(self):
		logger.info("...")
		sort_mode = self.movie_list.getSortMode(self.return_dir)
		self["sort_mode"].setText(sort_modes[sort_mode][1])

	def toggleSortMode(self):
		self.movie_list.toggleSortMode(self.return_dir)
		self.movie_list.loadList(self.return_dir, self.return_path)
		self.updateSortModeDisplay()

	def toggleSortOrder(self):
		self.movie_list.toggleSortOrder(self.return_dir)
		self.movie_list.loadList(self.return_dir, self.return_path)
		self.updateSortModeDisplay()

	def resetProgress(self):
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			self.updateCutList(path, last=0)
		self.movie_list.loadList(self.return_dir, self.return_path)

	def selectAll(self):
		self.movie_list.selectAll()

	def unselectAll(self):
		self.short_key = False
		self.movie_list.unselectAll()

	def selectionChanged(self):
		afile = self.movie_list.getCurrentSelection()
		if afile:
			self.return_path = afile[FILE_IDX_PATH]
			self.return_dir = afile[FILE_IDX_DIR]
		logger.debug("self.return_dir: %s, self.return_path: %s", self.return_dir, self.return_path)
		self.updateInfo()

	def selectedEntry(self):
		afile = self.movie_list.getCurrentSelection()
		if afile:
			path = afile[FILE_IDX_PATH]
			if path not in FileManager.getInstance().getLockList():
				if afile[FILE_IDX_TYPE] in [FILE_TYPE_DIR, FILE_TYPE_LINK]:
					self.changeDir(path)
				else:
					self.openPlayer(path)
			else:
				self.showFileManagerProgress()

	def startPlayer(self):
		logger.info("...")
		Recording.getInstance().addBlock(self.service.getPath())
		self.session.openWithCallback(self.openPlayerCallback, CockpitPlayer, self.service, config.plugins.moviecockpit, self.showMovieInfoEPG, False, 0, None, self.movie_list)

	def openPlayer(self, path):
		logger.info("path: %s", path)
		self.service = getService(SocketCockpit.getInstance().getFile(path), self.movie_list.getFile(path)[FILE_IDX_NAME])
		if os.path.exists(self.service.getPath()):
			logger.debug("new_path: %s", self.service.getPath())
			delay = 5 if os.path.basename(self.service.getPath()) == "remote.ts" else 0
			if delay:
				self.session.openWithCallback(self.startPlayer, BufferingProgress, delay)
			else:
				self.startPlayer()
		else:
			self.session.open(
				MessageBox,
				_("Video file does not exist") + "\n" + path,
				MessageBox.TYPE_ERROR,
				10
			)

	def openPlayerCallback(self):
		logger.info("...")
		SocketCockpit.getInstance().stopFileClient()

	def openContextMenu(self):
		if not self.short_key:
			self.short_key = True
		else:
			self.session.open(
				CockpitContextMenu,
				self,
				MENU_FUNCTIONS,
				self.movie_list.getCurrentDir(),
				self.movie_list.getListStyles(),
				None
			)

	def openPluginsMenu(self):
		self.short_key = False
		self.session.open(
			CockpitContextMenu,
			self,
			MENU_PLUGINS,
			self.movie_list.getCurrentDir(),
			None,
			getService(self.return_path, self.movie_list.getFile(self.return_path)[FILE_IDX_NAME])
		)

	def openConfigScreen(self):
		self.session.openWithCallback(self.openConfigScreenCallback, ConfigScreen, config.plugins.moviecockpit)

	def openConfigScreenCallback(self, reload_moviecockpit=False):
		logger.debug("reload_moviecockpit: %s", reload_moviecockpit)
		if reload_moviecockpit:
			self.exit(True)

	def moveToSeriesDir(self):
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			Recording.getInstance().moveToSeriesDir(path)

	def createSeriesDir(self):
		dirname = ""
		afile = self.movie_list.getCurrentSelection()
		if afile:
			name = afile[FILE_IDX_NAME]
			dirname = Recording.getInstance().getSeriesDir(name)
		self.session.openWithCallback(self.createDir, VirtualKeyBoard, title=(_("Enter directory name:")), text=dirname)

	def createDir(self, dirname):
		logger.info("dirname: %s, return_path: %s", dirname, self.return_path)
		if dirname:
			adir = os.path.join(os.path.dirname(self.return_path), dirname)
			logger.debug("adir: %s", adir)
			createDirectory(adir)
			FileManager().loadDatabaseFile(adir)
			self.movie_list.updateSortMode(adir, "1")

	def reloadCache(self):
		self.session.openWithCallback(
			self.reloadCacheResponse,
			MessageBox,
			_("Do you really want to reload the SQL cache?"),
			MessageBox.TYPE_YESNO
		)

	def reloadCacheResponse(self, response):
		if response:
			FileManager.getInstance().loadDatabase()
			self.session.open(FileManagerProgress, FILE_OP_LOAD)

	def selectDirectory(self, callback, title):
		logger.debug("bookmarks: %s", config.plugins.moviecockpit.bookmarks.value)
		self.session.openWithCallback(
			callback,
			LocationBox,
			windowTitle=title,
			text=_("Select directory"),
			currDir=MountCockpit.getInstance().getHomeDir(ID),
			bookmarks=config.plugins.moviecockpit.bookmarks,
			autoAdd=False,
			editDir=True,
			inhibitDirs=["/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"],
			minFree=None
		)

	def stopRecordings(self):
		logger.info("...")
		self.file_ops_list = []
		self.file_delete_list = []
		self.recordings_to_stop = []
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			if isRecording(path):
				self.recordings_to_stop.append(path)
		if self.recordings_to_stop:
			self.stopRecordingsQuery()

	def stopRecordingsResponse(self, response):
		if response:
			for path in self.recordings_to_stop:
				Recording.getInstance().addBlock(path)
				stopRecording(path)
			self.deleteMoviesQuery()

	def stopRecordingsQuery(self):
		file_names = self.createMovieList(self.recordings_to_stop)
		self.session.openWithCallback(
			self.stopRecordingsResponse,
			MessageBox,
			_("Stop recording(s)") + "?\n" + file_names,
			MessageBox.TYPE_YESNO
		)

	def createMovieList(self, file_list):
		file_names = ""
		movies = len(file_list)
		for i, path in enumerate(file_list):
			if i >= 5 and movies > 5:  # only show first 5 entries in file_list
				file_names += " ..."
				break
			file_name = self.movie_list.getFile(path)[FILE_IDX_NAME]
			file_names += "\n" + file_name
		return file_names

	def deleteMovies(self):
		logger.info("...")
		self.file_ops_list = []
		self.file_delete_list = []
		self.recordings_to_stop = []
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			logger.debug("path: %s", path)
			if not path.endswith("trashcan") and not path.endswith(".."):
				afile = self.movie_list.getFile(path)
				if "/trashcan" in path or afile[FILE_IDX_TYPE] == FILE_TYPE_DELETED:
					if afile[FILE_IDX_TYPE] == FILE_TYPE_DIR:
						all_dirs = MountCockpit.getInstance().getVirtualDirs(ID, [path])
						for adir in all_dirs:
							self.file_ops_list.append((FILE_OP_DELETE, adir, None))
					else:
						self.file_ops_list.append((FILE_OP_DELETE, path, None))
					self.file_delete_list.append(path)
				else:
					bookmark = MountCockpit.getInstance().getBookmark(ID, path)
					if afile[FILE_IDX_TYPE] == FILE_TYPE_DIR:
						all_dirs = MountCockpit.getInstance().getVirtualDirs(ID, [path])
						for adir in all_dirs:
							bookmark = MountCockpit.getInstance().getBookmark(ID, adir)
							sub_dir = os.path.relpath(adir, bookmark)
							trashcan_path = os.path.dirname(os.path.join(bookmark, "trashcan", sub_dir))
							self.file_ops_list.append((FILE_OP_MOVE, adir, trashcan_path))
					else:
						sub_dir = os.path.relpath(path, bookmark)
						trashcan_path = os.path.dirname(os.path.join(bookmark, "trashcan", sub_dir))
						self.file_ops_list.append((FILE_OP_MOVE, path, trashcan_path))

				if isRecording(path):
					self.recordings_to_stop.append(path)

		if self.recordings_to_stop:
			self.stopRecordingsQuery()
		else:
			self.deleteMoviesQuery()

	def deleteMoviesQuery(self):
		if self.file_delete_list:
			file_names = self.createMovieList(self.file_delete_list)
			msg = _("Permanently delete the selected video file(s) or dir(s)") + "?\n" + file_names
			self.session.openWithCallback(
				self.deleteMoviesResponse,
				MessageBox,
				msg,
				MessageBox.TYPE_YESNO
			)
		else:
			self.deleteMoviesResponse(True)

	def deleteMoviesResponse(self, response):
		logger.debug("response: %s", response)
		if response:
			self.execFileOps(self.file_ops_list)
		else:
			self.movie_list.unselectAll()

	def restoreMovies(self):
		logger.info("...")
		file_ops_list = []
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			if not path.endswith("..") and not isRecording(path):
				afile = self.movie_list.getFile(path)
				if afile[FILE_IDX_TYPE] == FILE_TYPE_DIR:
					all_dirs = MountCockpit.getInstance().getVirtualDirs(ID, [path])
					for adir in all_dirs:
						target_dir = os.path.dirname(adir.replace("/trashcan", "", 1))
						file_ops_list.append((FILE_OP_MOVE, adir, target_dir))
				else:
					target_dir = os.path.dirname(path.replace("/trashcan", "", 1))
					file_ops_list.append((FILE_OP_MOVE, path, target_dir))
		self.execFileOps(file_ops_list)

	def moveMovies(self):
		logger.info("...")
		selection_list = self.movie_list.getSelectionList()
		if selection_list:
			self.selectDirectory(
				boundFunction(self.selectedTargetDir, FILE_OP_MOVE, selection_list),
				_("Move file(s)")
			)

	def copyMovies(self):
		logger.info("...")
		selection_list = self.movie_list.getSelectionList()
		if selection_list:
			self.selectDirectory(
				boundFunction(self.selectedTargetDir, FILE_OP_COPY, selection_list),
				_("Copy file(s)"),
			)

	def selectedTargetDir(self, file_op, selection_list, target_dir):
		logger.debug("file_op: %s, target_dir: %s", file_op, target_dir)
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
				for path in selection_list:
					if not path.endswith("trashcan") and not path.endswith(".."):
						if not isRecording(path):
							file_ops_list.append((file_op, path, os.path.normpath(target_dir)))
						else:
							active_recordings_list.append(path)
				self.execFileOps(file_ops_list)

				if active_recordings_list:
					file_names = self.createMovieList(active_recordings_list)
					msg = _("Can't move recordings") + "\n" + file_names if file_op == FILE_OP_MOVE else _("Can't copy recordings") + "\n" + file_names
					self.session.open(
						MessageBox,
						msg,
						MessageBox.TYPE_INFO
					)

	def archiveFiles(self):
		archive_source_dir = config.plugins.moviecockpit.archive_source_dir.value
		archive_target_dir = config.plugins.moviecockpit.archive_target_dir.value
		logger.debug("archive_source_dir: %s, archive_target_dir: %s", archive_source_dir, archive_target_dir)
		if os.path.exists(archive_source_dir) and os.path.exists(archive_target_dir):
			FileManager.getInstance().archive(callback=self.execFileOpCallback)
			self.showFileManagerProgress()
		else:
			self.session.open(
				MessageBox,
				_("Archive source and/or target directory does not exist, please configure directories in setup."),
				MessageBox.TYPE_INFO
			)

	def openTrashcan(self):
		self.changeDir(MountCockpit.getInstance().getHomeDir(ID) + "/trashcan")

	def emptyTrashcan(self):
		self.session.openWithCallback(
			self.emptyTrashcanResponse,
			MessageBox,
			_("Permanently delete all files in trashcan?"),
			MessageBox.TYPE_YESNO
		)

	def emptyTrashcanResponse(self, response):
		if response:
			FileManager.getInstance().purgeTrashcan(0, self.execFileOpCallback)

	def removeCutListMarkers(self):
		logger.info("...")
		selection_list = self.movie_list.getSelectionList()
		for path in selection_list:
			self.removeCutListMarks(path)
		self.movie_list.loadList(self.return_dir, self.return_path)

	def execFileOps(self, file_ops_list):
		logger.info("file_ops_list: %s", file_ops_list)
		for file_op, path, target_dir in file_ops_list:
			FileManager.getInstance().execFileOp(file_op, path, target_dir, self.execFileOpCallback)
		self.movie_list.loadList(self.return_dir, self.return_path)

	def execFileOpCallback(self, file_op, path, target_dir, error):
		logger.info("file_op: %s, path: %s, target_dir: %s, error: %s, self.return_path: %s", file_op, path, target_dir, error, self.return_path)
		if error == FILE_OP_ERROR_NONE:
			if file_op == FILE_OP_MOVE and path == self.return_path and not target_dir.endswith("trashcan"):
				self.return_path = os.path.join(target_dir, os.path.basename(path))
				logger.debug("changed self.return_path to: %s", self.return_path)
		self.movie_list.loadList(self.movie_list.load_dir, self.return_path)
		if error == FILE_OP_ERROR_NO_DISKSPACE:
			self.session.open(
				MessageBox,
				_("Not enough space in target directory for video file") + ":\n" + path,
				MessageBox.TYPE_ERROR,
				10
			)

	def showFileManagerProgress(self):
		self.session.open(FileManagerProgress)

	def getBookmarksSpaceInfo(self):
		return MountCockpit.getInstance().getBookmarksSpaceInfo(ID)

	def toggleShowDeletedMovies(self):
		logger.info("...")
		self.movie_list.toggleShowDeletedMovies()
