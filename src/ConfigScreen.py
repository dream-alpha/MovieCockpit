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


from Version import PLUGIN
from Debug import logger
from DebugInit import log_levels
import os
from __init__ import _
from Components.config import config, getConfigListEntry, configfile, ConfigText, ConfigPassword
from Components.Button import Button
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from enigma import eTimer, ePoint
from Components.ConfigList import ConfigListScreen
from Screens.Standby import TryQuitMainloop
from Debug import setLogLevel
from ConfigScreenInit import ConfigScreenInit
from collections import Callable


class ConfigScreen(ConfigScreenInit, ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "CockpitConfigScreen"
		ConfigScreenInit.__init__(self, session)

		if self.skinName == "NoSupport":
			actions = {
				"cancel": self.keyCancel,
			}
		else:
			actions = {
				"cancel": self.keyCancel,
				"red": self.keyCancel,
				"save": self.keySaveNew,
				"yellow": self.loadDefaultSettings,
				"next_section": self.bouquetPlus,
				"previous_section": self.bouquetMinus,
			}

		self["actions"] = ActionMap(
			["ColorActions", "SetupActions"],
			actions,
			-2  # higher priority
		)

		self["VirtualKB"] = ActionMap(
			["VirtualKeyboardActions"],
			{
				"showVirtualKeyboard": self.keyText,
			},
			-2  # higher priority
		)

		self["VirtualKB"].setEnabled(False)

		self["no_support"] = Label()
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save"))
		self["key_yellow"] = Button(_("Defaults"))
		self["key_blue"] = Button()
		self["help"] = StaticText()

		self.list = []
		ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
		self.needs_restart = False
		self.needs_style_update = False

		self.reload_timer = eTimer()
		self.reload_timer_conn = self.reload_timer.timeout.connect(self.createConfig)

		self["config"].selectionChanged = self.selectionChanged
		self["config"].onSelectionChanged.append(self.updateHelp)
# 	self["config"].onSelectionChanged.append(self.handleInputHelpers)

		self.setTitle(PLUGIN)

		if self.skinName != "NoSupport":
			self.createConfig()

	def selectionChanged(self):
		current = self["config"].getCurrent()
		if current and len(current) > 1:
			if self["config"].current != current:
				if self["config"].current:
					self["config"].current[1].onDeselect(self.session)
				if current:
					current[1].onSelect(self.session)
				self["config"].current = current
			for x in self["config"].onSelectionChanged:
				if x:
					x()

	def handleInputHelpers(self):
		self["VirtualKB"].setEnabled(False)
		if self["config"].getCurrent():
			if isinstance(self['config'].getCurrent()[1], (ConfigPassword, ConfigText)):
				self["VirtualKB"].setEnabled(True)
				if hasattr(self, "HelpWindow"):
					if self["config"].getCurrent()[1].help_window.instance:
						helpwindowpos = self["HelpWindow"].getPosition()
						self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

	def keyText(self):
		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].getValue())

	def VirtualKeyBoardCallback(self, callback=None):
		if callback:
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())

	def cancelConfirm(self, answer):
		if answer:
			for x in self["config"].list:
				if len(x) > 1:
					x[1].cancel()
			self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close()

	def bouquetPlus(self):
		self["config"].jumpToPreviousSection()

	def bouquetMinus(self):
		self["config"].jumpToNextSection()

	def createConfig(self):
		logger.debug("len(self.config_list): %s", len(self.config_list))
		self.list = []
		for i, conf in enumerate(self.config_list):
			# 0 entry text
			# 1 variable
			# 2 validation
			# 3 pressed ok
			# 4 setup level
			# 5 parent entries
			# 6 help text
			# config item must be valid for current usage setup level
			if config.usage.setup_level.index >= conf[4]:
				# parent entries must be true
				for parent in conf[5]:
					if parent < 0:
						if not self.config_list[i + parent][1].value:
							break
					elif parent > 0:
						if self.config_list[i - parent][1].value:
							break
				else:
					# loop fell through without a break
					if conf[0] == self.section:
						if len(self.list) > 1:
							self.list.append(getConfigListEntry("", config.plugins.moviecockpit.fake_entry, None, None, 0, [], ""))
						if conf[1] == "":
							self.list.append(getConfigListEntry("<DUMMY CONFIGSECTION>",))
						else:
							self.list.append(getConfigListEntry(conf[1],))
					else:
						self.list.append(getConfigListEntry(conf[0], conf[1], conf[2], conf[3], conf[4], conf[5], conf[6]))
		self["config"].setList(self.list)
		self.setTitle(_("Setup"))

	def loadDefaultSettings(self):
		self.session.openWithCallback(
			self.loadDefaultSettingsCallback,
			MessageBox,
			_("Loading default settings will overwrite all settings, really load them?"),
			MessageBox.TYPE_YESNO
		)

	def loadDefaultSettingsCallback(self, answer):
		if answer:
			for conf in self.config_list:
				if conf[0] != self.section:
					if hasattr(conf[1], "type"):
						if conf[1].type == "preset":
							config.plugins.moviecockpit.preset = ConfigText()
							config.plugins.moviecockpit.preset.value = ""
							config.plugins.moviecockpit.preset.save()
						if conf[1].type == "style":
							logger.debug("saving key: %s, value: %s", conf[1].conf_key, "default")
							config.plugins.moviecockpit.style[conf[1].conf_key] = ConfigText()
							config.plugins.moviecockpit.style[conf[1].conf_key].value = "default"
							logger.debug("stored_values: %s", str(config.plugins.moviecockpit.style.stored_values))
							config.plugins.moviecockpit.style.save()
					else:
						conf[1].value = conf[1].default
			self.createConfig()

	def changedEntry(self, _addNotifier=None):
		if self.reload_timer.isActive():
			self.reload_timer.stop()
		self.reload_timer.start(50, True)

	def updateHelp(self):
		cur = self["config"].getCurrent()
		self["help"].text = (cur[6] if cur else '')

	def dirSelected(self, adir):
		if adir:
			adir = os.path.normpath(adir)
			if self["config"].getCurrent()[2]:
				if self["config"].getCurrent()[2](adir):
					self["config"].getCurrent()[1].value = adir

	def keyOK(self):
		logger.debug("...")
		current = self["config"].getCurrent()
		if current and current[3]:
			current[3](current[1])

	def reloadConfig(self):
		logger.debug("...")
		ConfigScreenInit.__init__(self, self.session)
		self.changedEntry()

	def keySaveNew(self):
		logger.debug("...")
		save_value = True
		for i, conf in enumerate(self.config_list):
			logger.debug("i: %s, conf[0]: %s", i, conf[0])
			if conf[0] != self.section:
				if conf[1].isChanged():
					logger.debug("i: %s, conf[0]: %s isChanged", i, conf[0])
					if conf[2]:
						# execute value changed function
						logger.debug("execute value changed function")
						if not conf[2](conf[1]):
							logger.error("value function error: %s", conf[0])
							save_value = False
					# Check parent entries
					for parent in conf[5]:
						logger.debug("parent: %s, conf[5]: %s", str(parent), str(conf[5]))
						if self.config_list[i + parent][2]:
							# execute parent value changed function
							logger.debug("execute parent value changed function")
							if not self.config_list[i + parent][2](self.config_list[i + parent][1]):
								logger.error("parent value function error: %s", self.config_list[i + parent][2])
					if save_value:
						logger.debug("saving: %s", conf[0])
						if hasattr(conf[1], "type"):
							ConfigScreenInit.save(conf[1])
						else:
							conf[1].save()
		configfile.save()
		if not save_value:
			self.createConfig()
		else:
			if self.needs_style_update:
				if isinstance(self.updateStyle, Callable):
					self.updateStyle()
					self.restartGUI()
			elif self.needs_restart:
				self.restartGUI()
			else:
				self.close(True)

	def restartGUI(self):
		self.session.openWithCallback(self.restartGUIConfirmed, MessageBox, _("Some changes require a GUI restart") + "\n" + _("Restart GUI now?"), MessageBox.TYPE_YESNO)

	def restartGUIConfirmed(self, answer):
		if answer:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close(True)

	def setLogLevel(self, element):
		logger.debug("element: %s", element.value)
		setLogLevel(log_levels[element.value])
		return True

	def needsRestart(self, _element=None):
		logger.info("...")
		self.needs_restart = True
		return True

	def needsStyleUpdate(self, _element=None):
		logger.info("...")
		self.needs_style_update = True
		return True

	def openLocationBox(self, element):
		if element:
			path = os.path.normpath(element.value)
			self.session.openWithCallback(
				self.dirSelected,
				LocationBox,
				windowTitle=_("Bookmarks"),
				text=_("Select directory"),
				currDir=path + "/",
				bookmarks=config.plugins.moviecockpit.bookmarks,
				autoAdd=False,
				editDir=True,
				inhibitDirs=["/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/var"],
				minFree=None
			)

	def validatePath(self, element):
		if isinstance(element, str):
			adir = os.path.normpath(element)
		else:
			adir = os.path.normpath(element.value)
		valid = os.path.exists(adir)
		if not valid:
			self.session.open(MessageBox, _("Path does not exist") + ": " + adir, MessageBox.TYPE_ERROR)
		return valid
