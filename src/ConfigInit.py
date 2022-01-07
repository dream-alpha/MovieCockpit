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
from Components.config import config, ConfigSet, ConfigDirectory, ConfigNumber, ConfigSelection, ConfigSelectionNumber, ConfigYesNo, ConfigSubsection, ConfigNothing, NoSave
from Components.Language import language
from .Debug import logger, log_levels, initLogging
from .__init__ import _
from .Autoselect639Language import Autoselect639Language


def langListEPG():
	lang_list = language.getLanguageList()
	alist = []
	for item in lang_list:
		alist.append((item[0][:5], item[1][0]))
	# logger.debug("alist: %s", str(alist))
	return alist


# date format is implemented using datetime.strftime
choices_date = [
	("%d.%m.%Y",		_("DD.MM.YYYY")),
	("%a %d.%m.%Y",		_("WD DD.MM.YYYY")),

	("%d.%m.%Y %H:%M",	_("DD.MM.YYYY HH:MM")),
	("%a %d.%m.%Y %H:%M",	_("WD DD.MM.YYYY HH:MM")),

	("%d.%m. %H:%M",	_("DD.MM. HH:MM")),
	("%a %d.%m. %H:%M",	_("WD DD.MM. HH:MM")),

	("%Y/%m/%d",		_("YYYY/MM/DD")),
	("%a %Y/%m/%d",		_("WD YYYY/MM/DD")),

	("%Y/%m/%d %H:%M",	_("YYYY/MM/DD HH:MM")),
	("%a %Y/%m/%d %H:%M",	_("WD YYYY/MM/DD HH:MM")),

	("%m/%d %H:%M",		_("MM/DD HH:MM")),
	("%a %m/%d %H:%M",	_("WD MM/DD HH:MM"))
]


choices_dir_info = [
	("",	_("off")),
	("D",	_("Description")),	  # Description
	("C",	_("(#)")),		  # Count
	("CS",	_("(#/GB)")),		  # Count/Size
	("S",	_("(GB)"))		  # Size
]


sort_modes = {
	"0": (("date", False),	_("Date sort down")),
	"1": (("date", True), 	_("Date sort up")),
	"2": (("alpha", False),	_("Alpha sort up")),
	"3": (("alpha", True),	_("Alpha sort down"))
}


choices_sort = [(k, v[1]) for k, v in list(sort_modes.items())]


choices_color_recording = [
	("#ff1616", _("red")),
	("#ff3838", _("light red")),
	("#8B0000", _("dark red"))
]


choices_color_selection = [
	("#ffffff", _("white")),
	("#cccccc", _("light grey")),
	("#bababa", _("grey")),
	("#666666", _("dark grey")),
	("#000000", _("black"))
]


choices_color_mark = [
	("#cccc00", _("dark yellow")),
	("#ffff00", _("yellow"))
] + choices_color_selection


choices_cover_source = [
	("tvs_id", "TV Spielfilm"),
	("tvm_id", "TV Movie"),
	("tvh_id", "HÖRZU"),
	("tvfa_id", "TV Für Alle"),
	("auto", _("automatic"))
]


def checkList(cfg):
	for choices in cfg.choices.choices:
		if cfg.value == choices[0]:
			return
	for choices in cfg.choices.choices:
		if cfg.default == choices[0]:
			cfg.value = cfg.default
			return
	cfg.value = cfg.choices.choices[0][0]


def initBookmarks():
	logger.info("...")
	bookmarks = []
	for video_dir in config.movielist.videodirs.value:
		bookmarks.append(os.path.normpath(video_dir))
	logger.debug("bookmarks: %s", bookmarks)
	return bookmarks


class ConfigInit():

	def __init__(self):
		logger.info("...")
		auto_lang_list = Autoselect639Language().getTranslatedChoicesDictAndSortedListAndDefaults()[1]
		config.plugins.moviecockpit = ConfigSubsection()
		config.plugins.moviecockpit.fake_entry = NoSave(ConfigNothing())
		config.plugins.moviecockpit.timer_autoclean = ConfigYesNo(default=False)
		config.plugins.moviecockpit.cover_auto_download = ConfigYesNo(default=False)
		config.plugins.moviecockpit.cover_fallback = ConfigYesNo(default=True)
		config.plugins.moviecockpit.cover_language = ConfigSelection(default=language.getActiveLanguage()[:2], choices=auto_lang_list)
		config.plugins.moviecockpit.cover_size = ConfigSelection(default="w500", choices=["w92", "w185", "w500", "original"])
		config.plugins.moviecockpit.backdrop_size = ConfigSelection(default="w1280", choices=["w300", "w780", "w1280", "original"])
		config.plugins.moviecockpit.cover_source = ConfigSelection(default="tvs_id", choices=choices_cover_source)
		config.plugins.moviecockpit.epglang = ConfigSelection(default=language.getActiveLanguage(), choices=langListEPG())
		config.plugins.moviecockpit.list_start_home = ConfigYesNo(default=True)
		config.plugins.moviecockpit.movie_description_delay = ConfigNumber(default=200)
		config.plugins.moviecockpit.list_show_mount_points = ConfigYesNo(default=False)
		config.plugins.moviecockpit.movie_watching_percent = ConfigSelectionNumber(0, 30, 1, default=10)
		config.plugins.moviecockpit.movie_finished_percent = ConfigSelectionNumber(50, 100, 1, default=90)
		config.plugins.moviecockpit.movie_date_format = ConfigSelection(default="%d.%m.%Y %H:%M", choices=choices_date)
		config.plugins.moviecockpit.movie_resume_at_last_pos = ConfigYesNo(default=True)
		config.plugins.moviecockpit.movie_start_position = ConfigSelection(default="event_start", choices=[("beginning", _("beginning")), ("first_mark", _("first mark")), ("event_start", _("event start"))])
		config.plugins.moviecockpit.trashcan_clean = ConfigYesNo(default=True)
		config.plugins.moviecockpit.trashcan_retention = ConfigSelectionNumber(0, 30, 1, default=3)
		config.plugins.moviecockpit.trashcan_show = ConfigYesNo(default=True)
		config.plugins.moviecockpit.trashcan_info = ConfigSelection(default="CS", choices=choices_dir_info)
		config.plugins.moviecockpit.list_content = ConfigNumber(default=1)
		config.plugins.moviecockpit.directories_info = ConfigSelection(default="CS", choices=choices_dir_info)
		config.plugins.moviecockpit.color = ConfigSelection(default="#bababa", choices=choices_color_selection)
		config.plugins.moviecockpit.color_sel = ConfigSelection(default="#ffffff", choices=choices_color_selection)
		config.plugins.moviecockpit.recording_color = ConfigSelection(default="#ff1616", choices=choices_color_recording)
		config.plugins.moviecockpit.recording_color_sel = ConfigSelection(default="#ff3838", choices=choices_color_recording)
		config.plugins.moviecockpit.selection_color = ConfigSelection(default="#cccc00", choices=choices_color_mark)
		config.plugins.moviecockpit.selection_color_sel = ConfigSelection(default="#ffff00", choices=choices_color_mark)
		config.plugins.moviecockpit.list_sort = ConfigSelection(default="0", choices=choices_sort)
		config.plugins.moviecockpit.list_style = ConfigNumber(default=3)
		config.plugins.moviecockpit.debug_log_level = ConfigSelection(default="INFO", choices=list(log_levels.keys()))
		config.plugins.moviecockpit.archive_enable = ConfigYesNo(default=False)
		config.plugins.moviecockpit.archive_source_dir = ConfigDirectory(default="/media/hdd/movie")
		config.plugins.moviecockpit.archive_target_dir = ConfigDirectory(default="/media/hdd/movie")

		config.plugins.moviecockpit.bookmarks = ConfigSet([], [])
		if not config.plugins.moviecockpit.bookmarks.value:
			config.plugins.moviecockpit.bookmarks.value = initBookmarks()
			config.plugins.moviecockpit.bookmarks.save()

		checkList(config.plugins.moviecockpit.epglang)
		initLogging()
