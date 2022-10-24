#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _

from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigSelectionNumber, ConfigText
from enigma import eTimer, getDesktop, addFont
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar

import os
import shutil
import sys

pythonFull = float(str(sys.version_info.major) + "." + str(sys.version_info.minor))
pythonVer = sys.version_info.major

isDreambox = False
if os.path.exists("/usr/bin/apt-get"):
    isDreambox = True


screenwidth = getDesktop(0).size()

dir_etc = "/etc/enigma2/VisualWeather/"
dir_tmp = "/tmp/VisualWeather/"
dir_plugins = "/usr/lib/enigma2/python/Plugins/Extensions/VisualWeather/"

font_folder = "%svisual-fonts/" % (dir_plugins)

interface_folder = "%svisual-interface/" % (dir_plugins)
gfx_folder = "%svisual-gfx/" % (dir_plugins)
skins_folder = "%sskins/" % (dir_plugins)
icons_folder = "%sweather-icons/" % (dir_plugins)


iconfolders = os.listdir(icons_folder)
iconfolders.sort()

skinfolders = os.listdir(skins_folder)
skinfolders.sort()

weather_json = "%sdata.json" % (dir_etc)

languages = [
    ("de", "Deutsch"),
    ("en", "English"),
    ("es", "Español"),
    ("fi", "Suomi"),
    ("fr", "Français"),
    ("it", "Italiano"),
    ("pl", "Polski"),
    ("pt", "Português"),
    ("ru", "Pусский"),
    ("se", "svenska"),  # sv
    ("nl", "Nederlands"),
    ("tr", "Türkçe"),
    ("sr", "Српски"),  # rs
    ("ua", "Українська")
]

config.plugins.VisualWeather = ConfigSubsection()
cfg = config.plugins.VisualWeather


# check if apikey.txt file exists in specified location
if not os.path.isfile(dir_etc + "apikey.txt"):
    open(dir_etc + "apikey.txt", "a").close()

apikey = ""
with open(dir_etc + "apikey.txt", "r") as f:
    apikey = f.readline()


cfg.apikey = ConfigText(default=str(apikey), fixed_size=False)


cfg.location = ConfigText(default="", fixed_size=False)
cfg.infobar = ConfigSelection(default="none", choices=[("none", _("None")), ("infobar", _("InfoBar")), ("secondinfobar", _("SecondInfoBar"))])

cfg.infobarcompactx = ConfigSelectionNumber(0, 1920, 30, default=30, wraparound=True)
cfg.infobarcompacty = ConfigSelectionNumber(0, 1080, 30, default=30,  wraparound=True)
cfg.infobarfullx = ConfigSelectionNumber(0, 1920, 30, default=30, wraparound=True)
cfg.infobarfully = ConfigSelectionNumber(0, 1080, 30, default=30,  wraparound=True)

cfg.secondinfobarcompactx = ConfigSelectionNumber(0, 1920, 30, default=30, wraparound=True)
cfg.secondinfobarcompacty = ConfigSelectionNumber(0, 1080, 30, default=30,  wraparound=True)
cfg.secondinfobarfullx = ConfigSelectionNumber(0, 1920, 30, default=30, wraparound=True)
cfg.secondinfobarfully = ConfigSelectionNumber(0, 1080, 30, default=30,  wraparound=True)

cfg.infobarsize = ConfigSelection(default="full", choices=[("full", _("Full width widget")), ("compact", _("Compact widget"))])
cfg.units = ConfigSelection(default="uk", choices=[("us", _("US (°F, miles)")), ("metric", _("Metric (°C, km)")), ("uk", _("UK (°C, miles)"))])
cfg.iconset = ConfigSelection(default=iconfolders[0], choices=iconfolders)
cfg.skin = ConfigSelection(default=skinfolders[0], choices=skinfolders)
cfg.language = ConfigSelection(default="en", choices=languages)
cfg.main = ConfigYesNo(default=False)
cfg.developer = ConfigYesNo(default=False)


hdr = {"User-Agent": "Enigma2 - VisualWeather Plugin"}


# create folder for working files
if not os.path.exists(dir_etc):
    os.makedirs(dir_etc)

# delete temporary folder and contents
if os.path.exists(dir_tmp):
    shutil.rmtree("/tmp/VisualWeather")

# create temporary folder for downloaded files
if not os.path.exists(dir_tmp):
    os.makedirs(dir_tmp)

# check if weather.json file exists in specified location
if not os.path.isfile(weather_json):
    open(weather_json, "a").close()

infobarVisualWeatherInstance = None
infobarVisualWeatherDialog = None
autoStartTimer = None
_firstRun = True
session_ = None


def main(session, **kwargs):
    global session_
    session_ = session
    from . import main
    session_.open(main.VisualWeather_Main)
    return


def forecast(session, **Kwargs):
    from . import forecast
    session.open(forecast.VisualWeather_Forecast, False)
    return


def mainmenu(menu_id, **kwargs):
    if menu_id == "mainmenu":
        return [(_("15 day weather"), forecast, "15 day weather", 500)]
    else:
        return []


def extensionsmenu(session, **kwargs):
    global session_
    session_ = session
    from . import main
    session_.open(main.VisualWeather_Main)
    return


class AutoStartTimer:

    def __init__(self, session):
        self.session = session
        self.weathertimer = eTimer()

        if cfg.location.value and cfg.apikey.value:
            global _firstRun

            if _firstRun:
                self.runUpdate()
                _firstRun = False

            try:
                self.weathertimer_conn = self.weathertimer.timeout.connect(self.runUpdate)
            except:
                self.weathertimer.callback.append(self.runUpdate)

            self.weathertimer.start(15 * 60 * 1000, False)  # every 15 mins run download

    def runUpdate(self):
        print("*** running weather update ***")
        self.weathertimer.stop()
        from . import update
        update.VisualWeather_Update()
        self.weathertimer.start(15 * 60 * 1000, False)  # every 15 mins run download
        clearWidget(self.session)


class infobarVisualWeather:
    def __init__(self, session):
        self.session = session
        self.InfoBarInstance = None
        if cfg.infobar.value != "none":
            global infobarVisualWeatherDialog
            from . import forecast
            if not infobarVisualWeatherDialog:
                infobarVisualWeatherDialog = self.session.instantiateDialog(forecast.VisualWeather_Forecast, True)

            self.firstDelayTimer = eTimer()
            try:
                self.firstDelayTimer_conn = self.firstDelayTimer.timeout.connect(self.infoBarAppendShowHide)
            except:
                self.firstDelayTimer.callback.append(self.infoBarAppendShowHide)

            self.firstDelayTimer.start(500, True)
        else:
            return

    def infoBarAppendShowHide(self):
        self.InfoBarInstance = InfoBar.instance

        if cfg.infobar.value == "infobar":
            # add infobar widget
            try:
                self.InfoBarInstance.onShow.append(self.show_widget)
                self.InfoBarInstance.onHide.append(self.hide_widget)
            except Exception as e:
                print(e)

        elif cfg.infobar.value == "secondinfobar":
            # openpli
            if hasattr(self.InfoBarInstance, "actualSecondInfoBarScreen"):
                try:
                    self.InfoBarInstance.actualSecondInfoBarScreen.onShow.append(self.show_widget)
                    self.InfoBarInstance.actualSecondInfoBarScreen.onHide.append(self.hide_widget)
                except Exception as e:
                    print(e)

            elif hasattr(self.InfoBarInstance, "secondInfoBarScreen"):
                # openatv/openvix
                try:
                    self.InfoBarInstance.secondInfoBarScreen.onShow.append(self.show_widget)
                    self.InfoBarInstance.secondInfoBarScreen.onHide.append(self.hide_widget)
                except Exception as e:
                    print(e)

    def show_widget(self):
        if infobarVisualWeatherDialog and not infobarVisualWeatherDialog.shown:
            if cfg.infobar.value == "infobar":
                if (hasattr(self.InfoBarInstance, "actualSecondInfoBarScreen") and not self.InfoBarInstance.actualSecondInfoBarScreen.shown) \
                        or (hasattr(self.InfoBarInstance, "secondInfoBarScreen") and not self.InfoBarInstance.secondInfoBarScreen.shown):
                    infobarVisualWeatherDialog.show()

            elif cfg.infobar.value == "secondinfobar":
                if (hasattr(self.InfoBarInstance, "actualSecondInfoBarScreen") and self.InfoBarInstance.actualSecondInfoBarScreen.shown) \
                        or (hasattr(self.InfoBarInstance, "secondInfoBarScreen") and self.InfoBarInstance.secondInfoBarScreen.shown):
                    infobarVisualWeatherDialog.show()

    def hide_widget(self, element=None):
        if infobarVisualWeatherDialog and infobarVisualWeatherDialog.shown:
            infobarVisualWeatherDialog.hide()


def autostart(reason, session=None, **kwargs):
    global autoStartTimer
    global _firstRun

    if reason == 0:
        if session is not None:
            _firstRun = True
            autoStartTimer = AutoStartTimer(session)
    return


def clearWidget(session=None):
    global infobarVisualWeatherDialog
    global infobarVisualWeatherInstance

    if infobarVisualWeatherDialog:
        try:
            session.deleteDialog(infobarVisualWeatherDialog)
            infobarVisualWeatherDialog = None
        except Exception as e:
            print(e)

    if os.path.isfile(weather_json) and os.stat(weather_json).st_size != 0 and cfg.location.value and cfg.apikey.value and cfg.infobar.value:
        infobarVisualWeatherInstance = None
        infobarVisualWeatherDialog = None

        if infobarVisualWeatherInstance is None:
            infobarVisualWeatherInstance = infobarVisualWeather(session)


def Plugins(**kwargs):
    addFont(font_folder + "m-plus-rounded-1c-regular.ttf", "visualregular", 100, 0)
    addFont(font_folder + "m-plus-rounded-1c-medium.ttf", "visualbold", 100, 0)

    iconFile = "visual-gfx/plugin-icon.png"
    description = (_("Live weather forecasts by KiddaC"))
    pluginname = (_("VisualWeather"))

    main_menu = PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_MENU, fnc=mainmenu, needsRestart=True)

    extensions_menu = PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=extensionsmenu, needsRestart=True)

    result = [PluginDescriptor(name=pluginname, description=description, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
              PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconFile, fnc=main)]

    result.append(extensions_menu)

    if cfg.main.getValue() and os.path.isfile(weather_json) and os.stat(weather_json).st_size != 0 and cfg.location.value and cfg.apikey.value:
        result.append(main_menu)

    return result
