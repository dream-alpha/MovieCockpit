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


from enigma import eServiceEvent
from Components.config import config
from .Debug import logger
from .__init__ import _


class ConfigScreenInit():

    def __init__(self, _csel, _session):
        logger.info("...")
        self.section = 400 * "¯"
        # text, config, on save, on ok, e2 usage level, depends on rel parent, description
        self.config_list = [
            (self.section, _("GENERAL"), None, None, 0, [], ""),
            (_("Show bookmark content on start"), config.plugins.moviecockpit.list_start_home, None, None, 0, [], _("Select whether bookmark content is to be displayed at plugin start or the last directory.")),
            (_("Automatic cleanup of timers list"), config.plugins.moviecockpit.timer_autoclean, None, None, 0, [], _("Select whether completed recording timers should be deleted automatically.")),
            (self.section, _("PLAYBACK"), None, None, 0, [], ""),
            (_("Resume video at last position"), config.plugins.moviecockpit.movie_resume_at_last_pos, None, None, 0, [], _("Select whether video should be resumed at last stop position.")),
            (_("Video start at"), config.plugins.moviecockpit.movie_start_position, None, None, 0, [], _("Select at which position video is started at.")),
            (self.section, _("DISPLAY"), None, None, 0, [], ""),
            (_("Default sort mode"), config.plugins.moviecockpit.list_sort, None, None, 0, [], _("Select the start mode to be used at startup.")),
            (_("Show directories information"), config.plugins.moviecockpit.directories_info, None, None, 0, [], _("Select which information should be displayed for directories.")),
            (_("Show mount points"), config.plugins.moviecockpit.list_show_mount_points, None, None, 0, [], _("Select whether to show mount_points or not.")),
            (_("Watching in progress percent"), config.plugins.moviecockpit.movie_watching_percent, None, None, 0, [], _("Select percentage for videos that areconsidered being watched.")),
            (_("Finished watching percent"), config.plugins.moviecockpit.movie_finished_percent, None, None, 0, [], _("Select percentage for videos that areconsidered finished.")),
            (_("Default color for video"), config.plugins.moviecockpit.color, None, None, 0, [], _("Select the color for video.")),
            (_("Default color for highlighted video"), config.plugins.moviecockpit.color_sel, None, None, 0, [], _("Select the color for videos that are highlighted.")),
            (_("Default color for recording"), config.plugins.moviecockpit.recording_color, None, None, 0, [], _("Select the color for recording.")),
            (_("Default color for highlighted recording"), config.plugins.moviecockpit.recording_color_sel, None, None, 0, [], _("Select the color for highlighted recording.")),
            (_("Default color for selected video"), config.plugins.moviecockpit.selection_color, None, None, 0, [], _("Select the color for selected video.")),
            (_("Default color for highlighted selected video"), config.plugins.moviecockpit.selection_color_sel, None, None, 0, [], _("Select the color for selected and highlighted video.")),
            (self.section, _("RECORDING COVERS"), None, None, 0, [], ""),
            (_("Download cover automatically for recording"), config.plugins.moviecockpit.cover_auto_download, None, None, 0, [], _("Select whether a cover should be automatically downloaded when recording a movie.")),
            (_("Cover source"), config.plugins.moviecockpit.cover_source, None, None, 0, [-1], _("Select the cover source.")),
            (_("Show fallback cover"), config.plugins.moviecockpit.cover_fallback, None, None, 0, [], _("Select whether a \"no cover available\" cover should be displayed when no cover is available.")),
            (self.section, _("TRASHCAN"), None, None, 0, [], ""),
            (_("Show trashcan directory"), config.plugins.moviecockpit.trashcan_show, None, None, 0, [], _("Select whether the trashcan should be displayed in the video list.")),
            (_("Show trashcan information"), config.plugins.moviecockpit.trashcan_info, None, None, 0, [-1], _("Select the trashcan information to be shown.")),
            (_("Enable auto trashcan cleanup"), config.plugins.moviecockpit.trashcan_clean, None, None, 0, [], _("Select whether the trashcan should be cleaned automatically.")),
            (_("File retention period in trashcan"), config.plugins.moviecockpit.trashcan_retention, None, None, 0, [-1], _("Select how many days the files should be kept in the trashcan before they are cleaned automatically.")),
            (self.section, _("LANGUAGE"), None, None, 0, [], ""),
            (_("Preferred EPG language"), config.plugins.moviecockpit.epglang, self.needsRestart, None, 0, [], _("Select the preferred EPG language.")),
            (self.section, _("ARCHIVE"), None, None, 0, [], ""),
            (_("Enable"), config.plugins.moviecockpit.archive_enable, None, None, 0, [], _("Select whether archiving should be activated.")),
            (_("Source"), config.plugins.moviecockpit.archive_source_dir, self.validatePath, self.openLocationBox, 0, [-1], _("Select the source bookmark for archiving.")),
            (_("Target"), config.plugins.moviecockpit.archive_target_dir, self.validatePath, self.openLocationBox, 0, [-2], _("Select the target bookmark for archiving.")),
            (self.section, _("CACHE"), None, None, 0, [], ""),
            (_("Cache directory"), config.plugins.moviecockpit.database_directory, self.validatePath, self.openLocationBox, 0, [], _("Select directory for cache database file.")),
            (self.section, _("DEBUG"), None, None, 0, [], ""),
            (_("Log level"), config.plugins.moviecockpit.debug_log_level, self.setLogLevel, None, 0, [], _("Select debug log level.")),
        ]

    def needsRestart(self, _element):
        return True

    def validatePath(self, _element):
        return True

    def openLocationBox(self, _element):
        return True

    def setLogLevel(self, _element):
        return True

    @staticmethod
    def setEPGLanguage(element):
        logger.debug("epglang: %s", element.value)
        eServiceEvent.setEPGLanguage(element.value)
        return True
