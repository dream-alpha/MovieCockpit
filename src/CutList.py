#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
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


import six.moves.cPickle as cPickle
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from .Debug import logger
from .CutListUtils import packCutList, replaceLast, removeMarks
from .FileUtils import writeFile
from .FileManagerUtils import FILE_IDX_CUTS
from .Version import ID


class CutList():

    def __init__(self):
        return

    def updateCutList(self, path, last):
        logger.info("path: %s, last: %s", path, last)
        cut_list = replaceLast(self.readCutList(path), last)
        self.writeCutList(path, cut_list)

    def removeCutListMarks(self, path):
        cut_list = removeMarks(self.readCutList(path))
        logger.info("path: %s, cut_list: %s", path, cut_list)
        self.writeCutList(path, cut_list)

    def readCutList(self, path):
        cut_list = []
        afile = FileManager.getInstance(ID).getFile("table1", path)
        if afile and afile[FILE_IDX_CUTS]:
            cut_list = cPickle.loads(afile[FILE_IDX_CUTS])
        logger.info("cut_list: %s", cut_list)
        return cut_list

    def writeCutList(self, path, cut_list):
        logger.info("path: %s, cut_list: %s", path, cut_list)
        data = packCutList(cut_list)
        writeFile(path + ".cuts", data)
        data = cPickle.dumps(cut_list)
        FileManager.getInstance(ID).update(path, cuts=data)
