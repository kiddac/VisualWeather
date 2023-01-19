#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _
from .plugin import cfg, dir_etc, autostart, icons_folder, interface_folder
from .vStaticText import StaticText

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import configfile, getConfigListEntry, ConfigText, ConfigSelection, ConfigYesNo
from Components.Pixmap import Pixmap
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

import os


class VisualWeather_Settings(ConfigListScreen, Screen):

    def __init__(self, session):
        Screen.__init__(self, session)

        self.session = session

        skin = interface_folder + "settings.xml"

        try:
            if os.path.exists("/var/lib/dpkg/status"):
                skin = interface_folder + "DreamOS/settings.xml"
        except:
            pass

        with open(skin, "r") as f:
            self.skin = f.read()

        self.setup_title = (_("Settings"))

        self.onChangedEntry = []

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

        self["iconset"] = Pixmap()

        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("Save"))

        self["VKeyIcon"] = Pixmap()
        self["VKeyIcon"].hide()
        self["HelpWindow"] = Pixmap()
        self["HelpWindow"].hide()

        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "cancel": self.cancel,
            "red": self.cancel,
            "green": self.save,
        }, -2)

        self.onFirstExecBegin.append(self.initConfig)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def cancel(self, answer=None):
        if answer is None:
            if self["config"].isChanged():
                self.session.openWithCallback(self.cancel, MessageBox, _("Really close without saving settings?"))
            else:
                self.close()
        elif answer:
            for x in self["config"].list:
                x[1].cancel()

            self.close()
        return

    def save(self):
        for x in self["config"].list:
            x[1].save()
        cfg.save()
        configfile.save()

        if not cfg.apikey.value:
            self.session.open(MessageBox, _("Please enter your apikey"), MessageBox.TYPE_WARNING)
            return

        if not cfg.location.value:
            self.session.open(MessageBox, _("Please enter your location"), MessageBox.TYPE_WARNING)
            return

        apipath = str(dir_etc) + "apikey.txt"
        with open(apipath, "w") as f:
            f.write(cfg.apikey.value)

        if cfg.location.value and cfg.apikey.value:
            autostart(0, self.session)

        self.close()

    def initConfig(self):
        self.cfg_apikey = getConfigListEntry(_("API key (sign up at visualcrossing.com for free personal API key)"), cfg.apikey)
        self.cfg_location = getConfigListEntry(_("Location: Local District / City / City, Country / Postal Code"), cfg.location)
        self.cfg_infobar = getConfigListEntry(_("Show on infobar or secondinfobar screen"), cfg.infobar)
        self.cfg_infobarsize = getConfigListEntry(_("Infobar widget size"), cfg.infobarsize)

        self.cfg_infobarcompactx = getConfigListEntry(_("Infobar compact weather widget X position"), cfg.infobarcompactx)
        self.cfg_infobarfullx = getConfigListEntry(_("Infobar full weather widget X position"), cfg.infobarfullx)
        self.cfg_secondinfobarcompactx = getConfigListEntry(_("SecondInfobar compact weather widget X position"), cfg.secondinfobarcompactx)
        self.cfg_secondinfobarfullx = getConfigListEntry(_("SecondInfobar full weather widget X position"), cfg.secondinfobarfullx)

        self.cfg_infobarcompacty = getConfigListEntry(_("Infobar compact weather widget Y position"), cfg.infobarcompacty)
        self.cfg_infobarfully = getConfigListEntry(_("Infobar full weather widget Y position"), cfg.infobarfully)
        self.cfg_secondinfobarcompacty = getConfigListEntry(_("SecondInfobar compact weather widget Y position"), cfg.secondinfobarcompacty)
        self.cfg_secondinfobarfully = getConfigListEntry(_("SecondInfobar full weather widget Y position"), cfg.secondinfobarfully)

        self.cfg_units = getConfigListEntry(_("Weather units"), cfg.units)
        self.cfg_skin = getConfigListEntry(_("Select skin *Restart GUI Required"), cfg.skin)
        self.cfg_iconset = getConfigListEntry(_("Weather icon set"), cfg.iconset)
        self.cfg_language = getConfigListEntry(_("Weather descriptions language"), cfg.language)
        self.cfg_main = getConfigListEntry(_("Show in main menu *Restart GUI Required"), cfg.main)
        self.cfg_developer = getConfigListEntry(_("Skin developer mode - allow all elements to be used in any screens. 15 day, full, compact."), cfg.developer)

        self.createSetup()

    def createSetup(self):
        self.list = []
        self.list.append(self.cfg_apikey)
        self.list.append(self.cfg_location)
        self.list.append(self.cfg_infobar)

        if cfg.infobar.value != "none":
            self.list.append(self.cfg_infobarsize)

            if cfg.infobar.value == "infobar":
                if cfg.infobarsize.value == "compact":
                    self.list.append(self.cfg_infobarcompactx)
                    self.list.append(self.cfg_infobarcompacty)

                elif cfg.infobarsize.value == "full":
                    self.list.append(self.cfg_infobarfullx)
                    self.list.append(self.cfg_infobarfully)

            if cfg.infobar.value == "secondinfobar":
                if cfg.infobarsize.value == "compact":
                    self.list.append(self.cfg_secondinfobarcompactx)
                    self.list.append(self.cfg_secondinfobarcompacty)

                elif cfg.infobarsize.value == "full":
                    self.list.append(self.cfg_secondinfobarfullx)
                    self.list.append(self.cfg_secondinfobarfully)

        self.list.append(self.cfg_units)
        self.list.append(self.cfg_skin)
        self.list.append(self.cfg_iconset)
        self.list.append(self.cfg_language)
        self.list.append(self.cfg_main)
        self.list.append(self.cfg_developer)

        iconpath = str(icons_folder) + str(cfg.iconset.value) + "/conditions/preview.png"

        if os.path.isfile(iconpath):
            try:
                if self["iconset"].instance:
                    self["iconset"].show()
                    self["iconset"].instance.setPixmapFromFile(iconpath)
            except Exception as e:
                print(e)
        else:
            self["iconset"].hide()

        self["config"].list = self.list
        self["config"].l.setList(self.list)
        self.handleInputHelpers()

    def handleInputHelpers(self):
        from enigma import ePoint
        currConfig = self["config"].getCurrent()

        if currConfig is not None:
            if isinstance(currConfig[1], ConfigText):
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(True)
                    except:
                        pass

                    try:
                        self["virtualKeyBoardActions"].setEnabled(True)
                    except:
                        pass
                    self["VKeyIcon"].show()

                if "HelpWindow" in self and currConfig[1].help_window and currConfig[1].help_window.instance is not None:
                    helpwindowpos = self["HelpWindow"].getPosition()
                    currConfig[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

            else:
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(False)
                    except:
                        pass

                    try:
                        self["virtualKeyBoardActions"].setEnabled(False)
                    except:
                        pass
                    self["VKeyIcon"].hide()

    def changedEntry(self):
        self.item = self["config"].getCurrent()
        for x in self.onChangedEntry:
            x()

        try:
            if isinstance(self["config"].getCurrent()[1], ConfigYesNo) or isinstance(self["config"].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass

    def getCurrentEntry(self):
        return self["config"].getCurrent() and self["config"].getCurrent()[0] or ""

    def getCurrentValue(self):
        return self["config"].getCurrent() and str(self["config"].getCurrent()[1].getText()) or ""
