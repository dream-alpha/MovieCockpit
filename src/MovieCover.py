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
from SkinUtils import getSkinPath
from PixmapDisplay import PixmapDisplay
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit


class MovieCover(PixmapDisplay):

	def __init__(self):
		PixmapDisplay.__init__(self)

	def getCoverPath(self, path):
		logger.debug("path: %s", path)
		bookmarks = MountCockpit.getInstance().getMountedBookmarks(ID)
		cover_path = os.path.splitext(path)[0] + ".jpg"
		if config.plugins.moviecockpit.cover_flash.value:
			for bookmark in bookmarks:
				if cover_path.startswith(bookmark):
					cover_path = config.plugins.moviecockpit.cover_bookmark.value + cover_path[len(bookmark):]
					break
		cover_file_name, cover_ext = os.path.splitext(cover_path)
		backdrop_path = cover_file_name + ".backdrop" + cover_ext
		logger.debug("cover_path: %s, backdrop_path: %s", cover_path, backdrop_path)
		return cover_path, backdrop_path

	def showCover(self, pixmap, path, no_cover_path=None):
		logger.info("path: %s", path)
		_file_name, ext = os.path.splitext(path)
		cover_path = None
		if path and ext and ext != "..":
			cover_path, _backdrop_path = self.getCoverPath(path)
			no_cover_path = getSkinPath("images/no_cover.svg")
		return self.showImage(pixmap, cover_path, no_cover_path)

	def showBackdrop(self, pixmap, path, no_backdrop_path=None):
		logger.info("path: %s", path)
		_file_name, ext = os.path.splitext(path)
		backdrop_path = None
		if path and ext and ext != "..":
			_cover_path, backdrop_path = self.getCoverPath(path)
			no_backdrop_path = getSkinPath("images/no_backdrop.svg")
		return self.showImage(pixmap, backdrop_path, no_backdrop_path)

	def showImage(self, pixmap, path, default_path):
		logger.info("path: %s", path)
		if path and not os.path.exists(path):
			path = None
			if config.plugins.moviecockpit.cover_fallback.value:
				if default_path and os.path.exists(default_path):
					path = default_path
		logger.info("path %s", path)
		if path:
			pixmap.instance.show()
			self.displayPixmap(pixmap, path)
			return True
		pixmap.instance.hide()
		return False
