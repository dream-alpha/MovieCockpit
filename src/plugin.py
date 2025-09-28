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


from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Screens.InfoBar import InfoBar
from Tools.BoundFunction import boundFunction
from .__init__ import _
from .Debug import logger
from .Version import ID, VERSION
from .SkinUtils import loadPluginSkin
from .ConfigScreenInit import ConfigScreenInit
from .MovieCockpit import MovieCockpit
from .ConfigInit import ConfigInit


def openMovieCockpit(session, **__):
    logger.info("...")
    session.openWithCallback(
        reloadMovieCockpit, MovieCockpit, InfoBar.instance)


def reloadMovieCockpit(session, reload_moviecockpit=False):
    if reload_moviecockpit:
        logger.info("...")
        openMovieCockpit(session)


def autoStart(reason, **kwargs):
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            session = kwargs["session"]
            InfoBar.showMovies = boundFunction(openMovieCockpit, session)
            ConfigScreenInit.setEPGLanguage(
                config.plugins.moviecockpit.epglang)
            MountCockpit.getInstance().registerBookmarks(
                ID, config.plugins.moviecockpit.bookmarks.value)
            loadPluginSkin("skin.xml")
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")


def Plugins(**__):
    ConfigInit()

    descriptors = [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART,
            ],
            fnc=autoStart
        ),
        PluginDescriptor(
            name="MovieCockpit",
            description=_("Manage recordings"),
            icon="MovieCockpit.svg",
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
            ],
            fnc=openMovieCockpit
        )
    ]
    return descriptors
