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
from time import time
from datetime import datetime
import six.moves.cPickle as cPickle
from ServiceReference import ServiceReference
from Components.config import config
from Components.GUIComponent import GUIComponent
from Components.TemplatedMultiContentComponent import TemplatedMultiContentComponent
from Tools.LoadPixmap import LoadPixmap
from enigma import eListbox, eSize
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from skin import parseColor, parseFont, parseSize
from .Debug import logger
from .Version import ID
from .__init__ import _
from .CutListUtils import ptsToSeconds, getCutListLast
from .SkinUtils import getSkinPath, getScalingFactor
from .FileManagerUtils import FILE_TYPE_FILE, FILE_TYPE_DIR, FILE_TYPE_LINK
from .FileManagerUtils import FILE_IDX_TYPE, FILE_IDX_DIR, FILE_IDX_PATH, FILE_IDX_FILENAME, FILE_IDX_NAME, FILE_IDX_EVENT_START_TIME, FILE_IDX_LENGTH, FILE_IDX_DESCRIPTION, FILE_IDX_SERVICE_REFERENCE, FILE_IDX_CUTS
from .FileManagerUtils import file_op_msg
from .FileUtils import readFile
from .MovieListTemplateAttributes import scaleTemplateAttributes
from .ConfigInit import sort_modes
from .Sorting import Sorting
from .ServiceCenter import ServiceCenter
from .ServiceUtils import getPicon
from .RecordingUtils import isRecording, isDownloadRecording
from .JobUtils import getPendingJob


class MovieList(TemplatedMultiContentComponent, Sorting, ServiceCenter):

    COMPONENT_ID = ""
    default_template = readFile(getSkinPath("MovieListTemplate.py"))
    GUI_WIDGET = eListbox

    def __init__(self):
        logger.debug("...")
        Sorting.__init__(self)
        ServiceCenter.__init__(self, self)
        self.file_list = []
        self.selection_list = []
        self.lock_list = {}
        self.list_styles = {}
        self.file_list_index = {}
        self.load_dir = ""
        self.skinAttributes = None
        TemplatedMultiContentComponent.__init__(self)
        self.l.setBuildFunc(self.buildMovieListEntry)

        self.show_dirs = False
        self.insert_dirs = False
        self.recursive = False
        self.list_content = config.plugins.moviecockpit.list_content.value
        self.setListContent()

        self.color = parseColor(config.plugins.moviecockpit.color.value).argb()
        self.color_sel = parseColor(
            config.plugins.moviecockpit.color_sel.value).argb()
        self.recording_color = parseColor(
            config.plugins.moviecockpit.recording_color.value).argb()
        self.recording_color_sel = parseColor(
            config.plugins.moviecockpit.recording_color_sel.value).argb()
        self.selection_color = parseColor(
            config.plugins.moviecockpit.selection_color.value).argb()
        self.selection_color_sel = parseColor(
            config.plugins.moviecockpit.selection_color_sel.value).argb()

        self.pic_back = LoadPixmap(getSkinPath(
            "images/back.svg"), cached=True, size=eSize(24, 24))
        self.pic_directory = LoadPixmap(getSkinPath(
            "images/dir.svg"), cached=True, size=eSize(24, 24))
        self.pic_link = LoadPixmap(getSkinPath(
            "images/link.svg"), cached=True, size=eSize(24, 24))
        self.pic_movie_default = LoadPixmap(getSkinPath(
            "images/movie_default.svg"), cached=True, size=eSize(24, 24))
        self.pic_movie_watching = LoadPixmap(getSkinPath(
            "images/movie_watching.svg"), cached=True, size=eSize(24, 24))
        self.pic_movie_finished = LoadPixmap(getSkinPath(
            "images/movie_finished.svg"), cached=True, size=eSize(24, 24))
        self.pic_movie_rec = LoadPixmap(getSkinPath(
            "images/movie_rec.svg"), cached=True, size=eSize(24, 24))
        self.pic_bookmark = LoadPixmap(getSkinPath(
            "images/bookmark.svg"), cached=True, size=eSize(24, 24))
        self.pic_trashcan = LoadPixmap(getSkinPath(
            "images/trashcan.svg"), cached=True, size=eSize(24, 24))
        self.pic_movie_deleted = LoadPixmap(getSkinPath(
            "images/deleted.svg"), cached=True, size=eSize(24, 24))

        self.onSelectionChanged = []

    def postWidgetCreate(self, instance):
        instance.setWrapAround(True)
        instance.setContent(self.l)
        self.selectionChanged_conn = instance.selectionChanged.connect(
            self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        self.selectionChanged_conn = None

    def setListStyle(self, list_style):
        self.list_style = list_style
        config.plugins.moviecockpit.list_style.value = list_style
        config.plugins.moviecockpit.list_style.save()
        self.setTemplate(self.list_styles[list_style][0])
        self.invalidateList()

    def toggleListStyle(self):
        index = self.list_style
        list_style = (index + 1) % len(self.list_styles)
        self.setListStyle(list_style)

    def getListStyles(self):
        return self.list_styles

    def setListContent(self):
        config.plugins.moviecockpit.list_content.value = self.list_content
        config.plugins.moviecockpit.list_content.save()
        self.show_dirs = self.recursive = self.insert_dirs = False
        if self.list_content == 0:
            self.show_dirs = False
            self.recursive = False
            self.insert_dirs = False
        elif self.list_content == 1:
            self.show_dirs = True
            self.recursive = False
            self.insert_dirs = False
        elif self.list_content == 2:
            self.show_dirs = False
            self.recursive = True
            self.insert_dirs = False
        elif self.list_content == 3:
            self.show_dirs = False
            self.recursive = False
            self.insert_dirs = True
        logger.debug("list_content: %s, show_dirs: %s, recursive: %s",
                     self.list_content, self.show_dirs, self.recursive)

    def nextListContent(self):
        self.list_content = self.list_content + 1 if self.list_content < 3 else 0
        self.setListContent()
        self.loadList()

    def previousListContent(self):
        self.list_content = self.list_content - 1 if self.list_content else 3
        self.setListContent()
        self.loadList()

    def selectionChanged(self):
        logger.debug("...")
        for function in self.onSelectionChanged:
            function()

    # move functions

    def moveUp(self, n=1):
        for _i in range(int(n)):
            self.instance.moveSelection(self.instance.moveUp)

    def moveDown(self, n=1):
        for _i in range(int(n)):
            self.instance.moveSelection(self.instance.moveDown)

    def pageUp(self):
        self.instance.moveSelection(self.instance.pageUp)

    def pageDown(self):
        self.instance.moveSelection(self.instance.pageDown)

    def moveTop(self):
        self.instance.moveSelection(self.instance.moveTop)

    def moveEnd(self):
        self.instance.moveSelection(self.instance.moveEnd)

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def moveToPath(self, path):
        index = self.getFileIndex(path)
        self.moveToIndex(index)
        return index

    def moveBouquetPlus(self):
        self.moveTop()

    def moveBouquetMinus(self):
        self.moveEnd()

    def moveToInitialSelection(self, selection_path):
        logger.info("selection_path: %s", selection_path)
        index = self.moveToPath(selection_path)
        if index < 0:
            if self.list_content == 3:
                if config.plugins.moviecockpit.trashcan_show.value:
                    index = 1
                else:
                    index = 0
                self.moveToIndex(index)
            else:
                while index < len(self.file_list) - 1:
                    if self.file_list[index][FILE_IDX_TYPE] != FILE_TYPE_FILE:
                        index += 1
                    else:
                        self.moveToIndex(index)
                        break
                else:
                    afile = self.getCurrentSelection()
                    if afile and afile[FILE_IDX_FILENAME] == ".." and len(self.file_list) > 1:
                        self.moveToIndex(1)

    # selection functions

    def getSelectionList(self):
        if not self.selection_list:
            # if no selections were made, add the current cursor position
            path = self.getCurrentPath()
            if path and not path.endswith("..") and path not in self.lock_list:
                self.selectPath(path)
        selection_list = self.selection_list[:]
        return selection_list

    def selectPath(self, path):
        logger.debug("path: %s", path)
        if path and not path.endswith("..") and path not in self.selection_list:
            self.selection_list.append(path)
            index = self.getFileIndex(path)
            if index > -1:
                self.invalidateEntry(index)

    def unselectPath(self, path):
        logger.debug("path: %s", path)
        if path in self.selection_list:
            self.selection_list.remove(path)
            index = self.getFileIndex(path)
            if index > -1:
                self.invalidateEntry(index)

    def selectAll(self):
        logger.debug("...")
        for afile in self.file_list:
            self.selectPath(afile[FILE_IDX_PATH])

    def unselectAll(self):
        logger.debug("...")
        selection_list = self.selection_list[:]
        for path in selection_list:
            self.unselectPath(path)

    def toggleSelection(self):
        path = self.getCurrentPath()
        logger.debug("path: %s", path)
        logger.debug("selection_list: %s", self.selection_list)
        if path in self.selection_list and path not in self.lock_list:
            self.unselectPath(path)
        else:
            self.selectPath(path)
        self.moveDown()

    # list functions

    def getCurrentPath(self):
        path = ""
        current_selection = self.l.getCurrentSelection()
        if current_selection:
            path = current_selection[FILE_IDX_PATH]
        return path

    def getCurrentDir(self):
        directory = ""
        current_selection = self.l.getCurrentSelection()
        if current_selection:
            directory = current_selection[FILE_IDX_DIR]
        logger.debug("directory: %s", directory)
        return directory

    def getFile(self, path):
        afile = []
        if not path:
            path = self.getCurrentPath()
        index = self.getFileIndex(path)
        if index > -1:
            afile = self.file_list[index]
        return afile

    def getFileIndex(self, path):
        logger.info("path: %s", path)
        index = self.file_list_index.get(path, -1)
        return index

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def getCurrentSelection(self):
        return self.l.getCurrentSelection()

    def invalidateList(self):
        self.lock_list = FileManager.getInstance(ID).getLockList()
        self.l.invalidate()

    def invalidateEntry(self, i):
        if i > -1:
            self.l.invalidateEntry(i)

    def filterDirList(self, dir_list):
        logger.info("...")
        filtered_list = []
        for adir in dir_list:
            path = adir[FILE_IDX_PATH]
            if self.list_content == 3 and not path.endswith("..") and "trashcan" not in path:
                if FileManager.getInstance(ID).getCountSize(path)[0] == 0:
                    logger.debug("skipping: %s", path)
                    continue
                if FileManager.getInstance(ID).getCountSize(path)[0] == 1:
                    alist = FileManager.getInstance(ID).getFileList(path)
                    if alist:
                        filtered_list.append(alist[0])
                        continue
            filtered_list.append(adir)
        return filtered_list

    def sortList(self, file_list, sort_mode, sort_order):
        logger.debug("sort_mode: %s, sort_order: %s", sort_mode, sort_order)

        if sort_mode == "date":
            if not sort_order:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_EVENT_START_TIME], x[FILE_IDX_NAME].lower()), reverse=True)
            else:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_EVENT_START_TIME], x[FILE_IDX_NAME].lower()))

        elif sort_mode == "alpha":
            if not sort_order:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_NAME].lower(), -x[FILE_IDX_EVENT_START_TIME]))
            else:
                file_list.sort(key=lambda x: (
                    x[FILE_IDX_NAME].lower(), x[FILE_IDX_EVENT_START_TIME]), reverse=True)

        return file_list

    def createListIndex(self, load_dir, file_list):
        all_load_dirs = MountCockpit.getInstance(
        ).getVirtualDirs(ID, [load_dir])
        file_list_index = {}
        for index, afile in enumerate(file_list):
            if afile[FILE_IDX_TYPE] == FILE_TYPE_DIR:
                for adir in all_load_dirs:
                    file_list_index[os.path.join(
                        adir, afile[FILE_IDX_FILENAME])] = index
            else:
                file_list_index[afile[FILE_IDX_PATH]] = index
        return file_list_index

    def loadList(self, load_dir=None, selection_path=None):
        logger.info("load_dir: %s, selection_path: %s",
                    load_dir, selection_path)
        if load_dir is None:
            load_dir = self.getCurrentDir()
        if self.recursive and "trashcan" not in load_dir:
            load_dir = MountCockpit.getInstance().getHomeDir(ID)
        if selection_path is None:
            selection_path = self.getCurrentPath()

        logger.info("load_dir: %s, selection_path: %s",
                    load_dir, selection_path)
        self.lock_list = FileManager.getInstance(ID).getLockList()
        self.selection_list = []
        header_list = []
        file_list = []
        dir_list = []
        if load_dir in MountCockpit.getInstance().getMountedBookmarks(ID):
            if config.plugins.moviecockpit.trashcan_show.value:
                trashcan_dir = os.path.join(load_dir, "trashcan")
                trashcan_file = list(FileManager.getInstance(
                    ID).newDirData(trashcan_dir, FILE_TYPE_DIR))
                trashcan_file[FILE_IDX_NAME] = _("trashcan")
                header_list.append(tuple(trashcan_file))
        elif load_dir:
            up_dir = os.path.join(load_dir, "..")
            up = FileManager.getInstance(ID).newDirData(up_dir, FILE_TYPE_DIR)
            header_list.append(up)
        if self.show_dirs:  # or os.path.basename(load_dir) == "trashcan":
            dir_list = FileManager.getInstance(ID).getDirList(load_dir)
            header_list += self.sortList(dir_list, "alpha", False)
        file_list = FileManager.getInstance(
            ID).getFileList(load_dir, self.recursive)
        if self.insert_dirs:
            file_list += self.filterDirList(
                FileManager.getInstance(ID).getDirList(load_dir))

        current_sort_mode = self.getSortMode(load_dir)
        sort_mode, sort_order = sort_modes[current_sort_mode][0]
        self.file_list = header_list + \
            self.sortList(file_list, sort_mode, sort_order)
        self.l.setList(self.file_list)
        self.file_list_index = self.createListIndex(load_dir, self.file_list)
        self.moveToInitialSelection(selection_path)
        self.load_dir = load_dir

    # skin functions

    def applySkin(self, desktop, parent):
        attribs = []
        value_attributes = [
        ]
        size_attributes = [
        ]
        font_attributes = [
        ]
        color_attributes = [
        ]

        if self.skinAttributes:
            for (attrib, value) in self.skinAttributes:
                if attrib in value_attributes:
                    setattr(self, attrib, int(value))
                elif attrib in size_attributes:
                    setattr(self, attrib, parseSize(value, ((1, 1), (1, 1))))
                elif attrib in font_attributes:
                    setattr(self, attrib, parseFont(value, ((1, 1), (1, 1))))
                elif attrib in color_attributes:
                    setattr(self, attrib, parseColor(value).argb())
                else:
                    attribs.append((attrib, value))
        self.skinAttributes = attribs

        self.list_styles = eval(readFile(getSkinPath("MovieListStyles.py")))
        template_attributes = eval(
            readFile(getSkinPath("MovieListAttributes.py")))
        template_attributes = scaleTemplateAttributes(
            self.list_styles, template_attributes, getScalingFactor())
        self.setListStyle(config.plugins.moviecockpit.list_style.value)

        logger.debug("self.skinAttributes: %s", self.skinAttributes)
        GUIComponent.applySkin(self, desktop, parent)

        template_attributes["width"] = self.l.getItemSize(
        ).width() - template_attributes["start"]

        bar_size = template_attributes["bar_size"]
        logger.debug("bar_size: %s", bar_size)
        self.pic_progress_bar = LoadPixmap(getSkinPath(
            "images/progcl.svg"), cached=True, size=eSize(bar_size[0], bar_size[1]))
        self.pic_rec_progress_bar = LoadPixmap(getSkinPath(
            "images/rec_progcl.svg"), cached=True, size=eSize(bar_size[0], bar_size[1]))
        self.applyTemplate(additional_locals=template_attributes)

    # list build function

    def buildMovieListEntry(self, *afile):

        def getDateText(path, file_type, date):
            logger.debug("path: %s, file_type: %s, date: %s",
                         path, file_type, date)
            count = 0
            date_text = ""
            if path in self.lock_list:
                file_op = self.lock_list[path]
                date_text = file_op_msg[file_op]
            else:
                if file_type in [FILE_TYPE_FILE]:
                    if config.plugins.moviecockpit.list_show_mount_points.value:
                        words = path.split("/")
                        if len(words) > 3 and words[1] == "media":
                            date_text = words[2]
                    else:
                        if date:
                            date_text = datetime.fromtimestamp(date).strftime(
                                config.plugins.moviecockpit.movie_date_format.value)
                else:
                    if os.path.basename(path) == "trashcan":
                        info_value = config.plugins.moviecockpit.trashcan_info.value
                    else:
                        info_value = config.plugins.moviecockpit.directories_info.value
                    if os.path.basename(path) == "..":
                        date_text = _("up")
                    else:
                        if info_value == "D":
                            if os.path.basename(path) == "trashcan":
                                date_text = _("trashcan")
                            else:
                                date_text = _("directory")
                        else:
                            count, size = FileManager.getInstance(
                                ID).getCountSize(path)
                            count_text = "%d" % count

                            size /= (1024 * 1024 * 1024)  # GB
                            size_text = "%.0f GB" % size
                            if size >= 1024:
                                size_text = "%.1f TB" % (size / 1024)

                            if info_value == "C":
                                date_text = "(%s)" % count_text
                            elif info_value == "S":
                                date_text = "(%s)" % size_text
                            elif info_value == "CS":
                                date_text = "(%s/%s)" % (count_text, size_text)
            logger.debug("count: %s, date_text: %s", count, date_text)
            return date_text

        def getProgress(is_recording, path, event_start_time, length, cuts):
            logger.debug("path: %s", path)
            progress = 0
            if isDownloadRecording(path):
                job = getPendingJob("MTC", path)
                progress = job.getProgress()
            else:
                if is_recording:
                    last = time() - event_start_time
                else:
                    # get last position from cut file
                    cut_list = cPickle.loads(cuts) if cuts else []
                    logger.debug("cut_list: %s", cut_list)
                    last = ptsToSeconds(getCutListLast(cut_list))
                    logger.debug("last: %s", last)

                if length > 0 and last > 0:
                    last = min(last, length)
                    progress = int(round(float(last) / float(length), 2) * 100)

            logger.debug("progress: %s, path: %s, length: %s, is_recording: %s",
                         progress, path, length, is_recording)
            return progress

        def getFileIcon(path, file_type, progress, is_recording):
            pixmap = None
            if file_type == FILE_TYPE_FILE:
                pixmap = self.pic_movie_default
                if is_recording:
                    pixmap = self.pic_movie_rec
                else:
                    if progress >= int(config.plugins.moviecockpit.movie_finished_percent.value):
                        pixmap = self.pic_movie_finished
                    elif progress >= int(config.plugins.moviecockpit.movie_watching_percent.value):
                        pixmap = self.pic_movie_watching
            elif file_type == FILE_TYPE_LINK:
                pixmap = self.pic_link
            elif file_type == FILE_TYPE_DIR:
                pixmap = self.pic_directory
                if os.path.basename(path) == "trashcan":
                    pixmap = self.pic_trashcan
                elif os.path.basename(path) == "..":
                    pixmap = self.pic_back
            return pixmap

        def getColor(path, _file_type, is_recording):
            color = self.color
            color_sel = self.color_sel
            if path in self.selection_list or path in self.lock_list:
                color = self.selection_color
                color_sel = self.selection_color_sel
            else:
                if is_recording:
                    color = self.recording_color
                    color_sel = self.recording_color_sel
            return color, color_sel

        logger.debug("list_style: %s", self.list_styles[self.list_style][0])

        path = afile[FILE_IDX_PATH]
        file_type = afile[FILE_IDX_TYPE]
        event_start_time = afile[FILE_IDX_EVENT_START_TIME]
        name = afile[FILE_IDX_NAME]
        length = afile[FILE_IDX_LENGTH]
        description = afile[FILE_IDX_DESCRIPTION]
        service_reference = afile[FILE_IDX_SERVICE_REFERENCE]
        cuts = afile[FILE_IDX_CUTS]

        self.lock_list = FileManager.getInstance(ID).getLockList()

        service = ServiceReference(service_reference)
        service_name = service.getServiceName() if service is not None else ""
        is_recording = isRecording(path)
        color, color_sel = getColor(path, file_type, is_recording)
        progress = getProgress(is_recording, path, event_start_time,
                               length, cuts) if file_type in [FILE_TYPE_FILE] else -1
        progress_string = str(progress) + "%" if progress >= 0 else ""
        progress_bar = self.pic_rec_progress_bar if is_recording else self.pic_progress_bar
        length_string = str(length / 60) + " " + \
            _("min") if file_type in [FILE_TYPE_FILE] else ""
        picon = getPicon(service_reference) if file_type in [
            FILE_TYPE_FILE] else None
        name = _(name) if name == "trashcan" else name
        date_text = getDateText(path, file_type, event_start_time)
        file_icon = getFileIcon(path, file_type, progress, is_recording)
        tags = ""

        res = [
            None,
            name,				  # 1: name
            tags,				  # 2: tags
            service_name,			  # 3: service name
            description,			  # 4: short description
            date_text,			  # 5: event start time
            length_string,			  # 6: length
            color,				  # 7: color
            color_sel,			  # 8: color_sel
            progress,			  # 9: progress percent (-1 = don't show)
            progress_string,		  # 10: progress (xx%)
            progress_bar,			  # 11: progress bar png
            file_icon,			  # 12: status icon png
            picon,				  # 13: picon png
        ]

        # logger.debug("self.res: %s", res)
        return res
