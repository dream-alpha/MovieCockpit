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


from .__init__ import _
from .Debug import logger
from .PluginUtils import getPlugin, WHERE_COVER_DOWNLOAD


choices_cover_source = [
    ("tvh_id", "HÖRZU"),
    ("tvfa_id", "TV Für Alle"),
    ("tvs_id", "TVSpielfilm"),
    ("auto", _("automatic"))
]


def downloadCover(target_path, service_str, event_start_time, event_duration, source_id, callback):
    plugin = getPlugin(WHERE_COVER_DOWNLOAD)
    if plugin:
        logger.debug("plugin.name: %s", plugin.name)
        plugin(
            target_path,
            service_str,
            event_start_time,
            event_duration,
            source_id,
            callback
        )
