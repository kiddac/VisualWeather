#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _


from .plugin import interface_folder, gfx_folder, weather_json
from .vStaticText import StaticText
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap

import os


class VisualWeather_Main(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = interface_folder + "menu.xml"
        with open(skin, "r") as f:
            self.skin = f.read()

        self.list = []
        self.drawList = []
        self.playlists_all = []
        self["list"] = List(self.drawList, enableWrapAround=True)

        self.setup_title = _("Options")

        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("OK"))

        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "red": self.quit,
            "green": self.__next__,
            "ok": self.__next__,
            "cancel": self.quit,
            "menu": self.settings,

        }, -2)

        self.onFirstExecBegin.append(self.start)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def start(self, answer=None):
        self.createSetup()

    def createSetup(self):
        self.list = []
        self.list.append([1, _("Weather setup")])
        if os.path.isfile(weather_json) and os.stat(weather_json).st_size != 0:
            self.list.append([2, _("15 day weather forecast")])

        self.drawList = []
        self.drawList = [buildListEntry(x[0], x[1]) for x in self.list]
        self["list"].setList(self.drawList)

    def settings(self):
        from . import settings
        self.session.openWithCallback(self.start, settings.VisualWeather_Settings)

    def forecast(self):
        from . import forecast
        self.session.openWithCallback(self.start, forecast.VisualWeather_Forecast, False)

    def __next__(self):
        index = self["list"].getCurrent()[0]

        if self["list"].getCurrent():
            if index == 1:
                self.settings()
            if index == 2:
                self.forecast()

    def quit(self, data=None):
        self.close()


def buildListEntry(index, title):
    png = None

    if index == 1:
        png = LoadPixmap(str(gfx_folder) + "settings.png")
    if index == 2:
        png = LoadPixmap(str(gfx_folder) + "weather.png")

    return (index, str(title), png)
