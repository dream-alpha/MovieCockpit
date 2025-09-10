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

import os
import time
from pipes import quote
from enigma import eConsoleAppContainer
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from .Debug import logger
from .FileUtils import readFile
from .ConfigInit import sort_modes
from .Version import ID


class Sorting():

    def __init__(self):
        self.container = eConsoleAppContainer()

    def updateSortMode(self, adir, sort):
        logger.info("adir: %s, sort: %s", adir, sort)
        sort = "%s,%s" % (int(time.time()), sort)
        FileManager.getInstance(ID).update(adir, sort=sort)
        self.writeSortFile(adir, sort)

    def getSortMode(self, adir):
        logger.info("adir: %s", adir)
        return FileManager.getInstance(ID).getSortMode(adir)

    def writeSortFile(self, adir, sort):
        logger.info("adir: %s, sort: %s", adir, sort)
        cmd = "echo '%s' > %s" % (sort, os.path.join(quote(adir), ".sort"))
        self.container.execute(cmd)

    def readSortFile(self, adir):
        logger.info("adir: %s", adir)
        sort = readFile(os.path.join(adir, ".sort"))
        return sort

    def toggleSortMode(self, adir):
        logger.info("adir: %s", adir)
        sort_mode = self.getSortMode(adir)
        sort_mode = str((int(sort_mode) + 2) % len(sort_modes))
        self.updateSortMode(adir, sort_mode)
        return sort_mode

    def toggleSortOrder(self, adir):
        logger.info("adir: %s", adir)
        sort_mode = self.getSortMode(adir)
        mode, order = sort_modes[sort_mode][0]
        order = not order
        for mode_id, sort_mode in list(sort_modes.items()):
            if sort_mode[0] == (mode, order):
                sort_mode = mode_id
                self.updateSortMode(adir, sort_mode)
                break
        return sort_mode
