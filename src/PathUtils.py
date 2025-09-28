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
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from .Debug import logger


def getArchiveTarget(path, target_dir):
    logger.info("path: %s, target_dir: %s", path, target_dir)
    src_bookmark = MountCockpit.getInstance().getBookmark("MVC", path)
    src_sub_dir = os.path.dirname(os.path.relpath(path, src_bookmark))
    dst_bookmark = MountCockpit.getInstance().getBookmark("MVC", target_dir)
    target_dir = os.path.abspath(os.path.join(dst_bookmark, src_sub_dir))
    logger.debug("target_dir: %s", target_dir)
    return target_dir


def getMoveTarget(path, target_dir):
    logger.info("same bookmark - path: %s, target_dir: %s", path, target_dir)
    src_bookmark = MountCockpit.getInstance().getBookmark("MVC", path)
    dst_sub_dir = os.path.relpath(target_dir, src_bookmark)
    target_dir = os.path.abspath(os.path.join(src_bookmark, dst_sub_dir))
    logger.debug("target_dir: %s", target_dir)
    return target_dir


def getMoveToTrashcanTarget(path):
    logger.info("path: %s", path)
    src_bookmark = MountCockpit.getInstance().getBookmark("MVC", path)
    src_sub_dir = os.path.relpath(path, src_bookmark)
    target_dir = os.path.dirname(os.path.abspath(os.path.join(src_bookmark, "trashcan", src_sub_dir)))
    logger.debug("target_dir: %s", target_dir)
    return target_dir


def getMoveFromTrashcanTarget(path):
    logger.info("path: %s", path)
    target_dir = os.path.dirname(path.replace("/trashcan", ""))
    logger.debug("target_dir: %s", target_dir)
    return target_dir
