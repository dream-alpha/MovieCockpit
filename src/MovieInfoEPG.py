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


from Components.Sources.COCServiceEvent import COCServiceEvent
from Components.Button import Button
from Components.ActionMap import ActionMap
from Screens.Screen import Screen
from .__init__ import _
from .SkinUtils import getSkinName


class MovieInfoEPG(Screen):

    def __init__(self, session, name, service, movie_list, tmdb_plugin=None, mediathek_plugin=None):
        self.service = service
        Screen.__init__(self, session)
        self.setTitle(name)
        self.skinName = getSkinName("MovieInfoEPG")
        self["Service"] = COCServiceEvent(movie_list)
        self["Service"].newService(service)
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        if tmdb_plugin:
            self["key_yellow"].setText("TMDB" + " " + _("Info"))
        self["key_blue"] = Button("")
        if mediathek_plugin:
            self["key_blue"].setText("Mediathek" + " " + _("Download"))
        self["my_actions"] = ActionMap(
            ["OkCancelActions", "CockpitActions"],
            {
                "cancel": self.close,
                "ok": self.close,
                "RED": self.close,
                "YELLOW": self.yellow,
                "BLUE": self.blue,
            }
        )

    def yellow(self):
        self.close("tmdb")

    def blue(self):
        self.close("mediathek")
