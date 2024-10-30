#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _
from .plugin import weather_json, cfg, icons_folder, skins_folder
from .vStaticText import StaticText
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from decimal import Decimal
from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

import datetime
import json
import os


def remove_exponent(d):
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()


class VisualWeather_Forecast(Screen):
    def __init__(self, session, infobarskin=False):

        Screen.__init__(self, session)

        self.infobarskin = infobarskin

        self.session = session

        if cfg.infobar.value == "infobar":
            if cfg.infobarsize.value == "compact":
                self.xpos = int(cfg.infobarcompactx.value)
                self.ypos = int(cfg.infobarcompacty.value)

            elif cfg.infobarsize.value == "full":
                self.xpos = int(cfg.infobarfullx.value)
                self.ypos = int(cfg.infobarfully.value)

        if cfg.infobar.value == "secondinfobar":
            if cfg.infobarsize.value == "compact":
                self.xpos = int(cfg.secondinfobarcompactx.value)
                self.ypos = int(cfg.secondinfobarcompacty.value)

            elif cfg.infobarsize.value == "full":
                self.xpos = int(cfg.secondinfobarfullx.value)
                self.ypos = int(cfg.secondinfobarfully.value)

        if not self.infobarskin:
            skin = str(skins_folder) + str(cfg.skin.value) + "/forecast.xml"
        else:
            if cfg.infobarsize.value == "full":
                skin = str(skins_folder) + str(cfg.skin.value) + "/infobar.xml"
            else:
                skin = str(skins_folder) + str(cfg.skin.value) + "/infobarcompact.xml"

        with open(skin, "r") as f:
            self.skin = f.read()

        self.setup_title = _("Visual Weather")
        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("OK"))

        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "cancel": self.cancel,
            "red": self.cancel,
            "green": self.cancel,
            "ok": self.cancel
        }, -2)

        self.icon_path = "%s%s/" % (icons_folder, cfg.iconset.value)

        # 15 day / full / compact
        self["location"] = StaticText()
        self["conditions"] = StaticText()
        self["temp"] = StaticText()
        self["feelslike"] = StaticText()
        self["tempmax"] = StaticText()
        self["tempmin"] = StaticText()
        self["icon"] = Pixmap()
        self["tempmax-icon"] = Pixmap()
        self["tempmin-icon"] = Pixmap()
        self["precipprob"] = StaticText()
        self["precipprob-icon"] = Pixmap()

        # not compact
        if not self.infobarskin or cfg.infobarsize.value == "full" or cfg.developer.value:
            self["description"] = StaticText()
            self["sunrise"] = StaticText()
            self["sunset"] = StaticText()
            self["humidity"] = StaticText()
            self["uvindex"] = StaticText()
            self["pressure"] = StaticText()
            self["moonphase"] = StaticText()
            self["windspeed"] = StaticText()
            self["datetime"] = StaticText()
            self["sunrise-icon"] = Pixmap()
            self["sunset-icon"] = Pixmap()
            self["moon-icon"] = Pixmap()
            self["wind-icon"] = Pixmap()
            self["humidity-icon"] = Pixmap()
            self["uvindex-icon"] = Pixmap()
            self["pressure-icon"] = Pixmap()

        # only 15 day
        if not self.infobarskin or cfg.developer.value:
            for x in range(15):
                icon = "day" + str(x) + "-icon"
                weekday = "day" + str(x) + "-weekday"
                tempmax = "day" + str(x) + "-tempmax"
                tempmin = "day" + str(x) + "-tempmin"
                precipprob = "day" + str(x) + "-precipprob"
                precipicon = "day" + str(x) + "-precip-icon"

                hicon = "hour" + str(x) + "-icon"
                htime = "hour" + str(x) + "-time"
                htemp = "hour" + str(x) + "-temp"
                hprecipprob = "hour" + str(x) + "-precipprob"
                hprecipicon = "hour" + str(x) + "-precip-icon"

                self[icon] = Pixmap()
                self[weekday] = StaticText()
                self[tempmax] = StaticText()
                self[tempmin] = StaticText()
                self[precipprob] = StaticText()
                self[precipicon] = Pixmap()

                self[hicon] = Pixmap()
                self[htime] = StaticText()
                self[htemp] = StaticText()
                self[hprecipprob] = StaticText()
                self[hprecipicon] = Pixmap()

        self.firstDelayTimer = eTimer()
        try:
            self.firstDelayTimer_conn = self.firstDelayTimer.timeout.connect(self.processdata)
        except:
            self.firstDelayTimer.callback.append(self.processdata)
        self.firstDelayTimer.start(100, True)

        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def cancel(self, data=None):
        self.close()

    def initvariable(self):

        self.processdata()

    def processdata(self):
        self.weather = None

        if os.path.isfile(weather_json) and os.stat(weather_json).st_size != 0:
            try:
                with open(weather_json, "r") as f:
                    self.weather = json.load(f)
            except:
                pass

        if not self.weather:
            self.session.openWithCallback(self.cancel, MessageBox, _("No data or invalid location.\nPlease check your weather location in settings."), type=MessageBox.TYPE_ERROR, timeout=5)
        else:
            if cfg.units.value == "us":
                windunit = " mph"
            elif cfg.units.value == "metric":
                windunit = " kph"
            elif cfg.units.value == "uk":
                windunit = " mph"

            try:
                self.location = self.weather["resolvedAddress"].split(',')[0]
            except:
                self.location = self.weather["address"]

            self.description = self.weather["description"]

            # get current conditions
            self.current_conditions = self.weather["currentConditions"]["conditions"]
            self.current_icon = str(self.icon_path) + "conditions/" + str(self.weather["currentConditions"]["icon"]) + ".png"
            self.current_temp = str(int(round(self.weather["currentConditions"]["temp"]))) + "°"
            self.current_feelslike = _("Feels like ") + str(int(round(self.weather["currentConditions"]["feelslike"]))) + "°"

            self.current_tempmax = str(int(round(self.weather["days"][0]["tempmax"]))) + "°"
            self.current_tempmin = str(int(round(self.weather["days"][0]["tempmin"]))) + "°"

            self.current_sunset = self.weather["currentConditions"]["sunset"][:-3]
            self.current_sunrise = self.weather["currentConditions"]["sunrise"][:-3]

            self.current_time = self.weather["currentConditions"]["datetime"][:-3]
            self.current_datetimeEpoch = self.weather["currentConditions"]["datetimeEpoch"]
            self.current_datetime = datetime.datetime.fromtimestamp(self.current_datetimeEpoch)
            self.current_weekday = self.current_datetime.strftime('%a')

            self.current_pressure = str(int(round(self.weather["currentConditions"]["pressure"]))) + " mb"

            self.current_precipprob = "0 %"

            for hour in self.weather["days"][0]["hours"]:
                if int(hour["datetimeEpoch"]) >= int(self.weather["currentConditions"]["datetimeEpoch"]):
                    self.current_precipprob = str(remove_exponent(Decimal(str(hour["precipprob"])))) + " %"
                    break

            self.current_humidity = str(int(round(self.weather["currentConditions"]["humidity"]))) + " %"

            # uv index
            self.current_uvindex = int(self.weather["currentConditions"]["uvindex"])
            self.current_uvindextext = _("Low")

            if self.current_uvindex > 2 and self.current_uvindex < 6:
                self.current_uvindextext = _("Moderate")

            elif self.current_uvindex >= 6 and self.current_uvindex < 8:
                self.current_uvindextext = _("High")

            elif self.current_uvindex >= 8 and self.current_uvindex < 11:
                self.current_uvindextext = _("Very High")

            elif self.current_uvindex >= 11:
                self.current_uvindextext = _("Extreme")

            # moonphase
            self.current_moonphase = self.weather["currentConditions"]["moonphase"]
            self.current_moonphase_text = _("New Moon")
            self.current_moonphase_icon = "moon-new-moon"

            if self.current_moonphase > 0 and self.current_moonphase <= 0.23:
                self.current_moonphase_text = _("Waxing Crescent")
                self.current_moonphase_icon = "moon-waxing-crescent"

            elif self.current_moonphase >= 0.24 and self.current_moonphase <= 0.25:
                self.current_moonphase_text = _("First Quarter")
                self.current_moonphase_icon = "moon-first-quarter"

            elif self.current_moonphase >= 0.26 and self.current_moonphase <= 0.48:
                self.current_moonphase_text = _("Waxing Gibbous")
                self.current_moonphase_icon = "moon-waxing-gibbous"

            elif self.current_moonphase >= 0.49 and self.current_moonphase <= 0.50:
                self.current_moonphase_text = _("Full Moon")
                self.current_moonphase_icon = "moon-full-moon"

            elif self.current_moonphase >= 0.51 and self.current_moonphase <= 0.73:
                self.current_moonphase_text = _("Waning Gibbous")
                self.current_moonphase_icon = "moon-waning-gibbous"

            elif self.current_moonphase >= 0.74 and self.current_moonphase <= 0.75:
                self.current_moonphase_text = _("Last Quarter")
                self.current_moonphase_icon = "moon-last-quarter"

            elif self.current_moonphase >= 0.76 and self.current_moonphase <= 0.99:
                self.current_moonphase_text = _("Waning Crescent")
                self.current_moonphase_icon = "moon-waning-crescent"

            self.current_moonphase_png = str(self.icon_path) + "moon/%s.png" % (self.current_moonphase_icon)

            # wind
            self.current_windspeed = str(int(round(self.weather["currentConditions"]["windspeed"]))) + str(windunit)
            self.current_winddir = float(self.weather["currentConditions"]["winddir"])

            #fall back icon
            self.current_wind_icon = "n"

            if self.current_winddir <= 11.25 or self.current_winddir >= 348.76:
                self.current_wind_icon = "n"

            elif self.current_winddir >= 11.26 and self.current_winddir <= 33.75:
                self.current_wind_icon = "nne"

            elif self.current_winddir >= 33.76 and self.current_winddir <= 56.25:
                self.current_wind_icon = "ne"

            elif self.current_winddir >= 56.26 and self.current_winddir <= 78.75:
                self.current_wind_icon = "ene"

            elif self.current_winddir >= 78.76 and self.current_winddir <= 101.25:
                self.current_wind_icon = "e"

            elif self.current_winddir >= 101.26 and self.current_winddir <= 123.75:
                self.current_wind_icon = "ese"

            elif self.current_winddir >= 123.76 and self.current_winddir <= 146.25:
                self.current_wind_icon = "se"

            elif self.current_winddir >= 146.26 and self.current_winddir <= 168.75:
                self.current_wind_icon = "sse"

            elif self.current_winddir >= 168.76 and self.current_winddir <= 191.25:
                self.current_wind_icon = "s"

            elif self.current_winddir >= 191.26 and self.current_winddir <= 213.75:
                self.current_wind_icon = "ssw"

            elif self.current_winddir >= 213.76 and self.current_winddir <= 236.25:
                self.current_wind_icon = "sw"

            elif self.current_winddir >= 236.26 and self.current_winddir <= 258.75:
                self.current_wind_icon = "wsw"

            elif self.current_winddir >= 258.76 and self.current_winddir <= 281.25:
                self.current_wind_icon = "w"

            elif self.current_winddir >= 281.26 and self.current_winddir <= 303.75:
                self.current_wind_icon = "wnw"

            elif self.current_winddir >= 303.76 and self.current_winddir <= 326.25:
                self.current_wind_icon = "nw"

            elif self.current_winddir >= 326.26 and self.current_winddir <= 348.75:
                self.current_wind_icon = "nnw"

            self.current_wind_png = str(self.icon_path) + "wind/wind-%s.png" % (self.current_wind_icon)

            self.current()

            if not self.infobarskin or cfg.developer.value:
                self.hours()
                self.days()

    def hours(self):
        index = 0
        for hour in self.weather["days"][0]["hours"]:
            datetimeEpoch = hour["datetimeEpoch"]
            hour_datetime = datetime.datetime.fromtimestamp(datetimeEpoch)
            if hour_datetime < datetime.datetime.now():
                continue

            hour_datetime = str(hour["datetime"])[:-3]
            icon = str(self.icon_path) + "conditions/" + str(hour["icon"]) + ".png"
            temp = str(int(round(hour["temp"]))) + "°"
            if hour["precipprob"]:
                precipprob = str(int(round(hour["precipprob"]))) + " %"
            else:
                precipprob = "0 %"

            entry1 = "hour" + str(index) + "-icon"
            entry2 = "hour" + str(index) + "-time"
            entry3 = "hour" + str(index) + "-temp"
            entry4 = "hour" + str(index) + "-precipprob"
            entry5 = "hour" + str(index) + "-precip-icon"

            if self[entry1].instance:
                self[entry1].instance.setPixmapFromFile(icon)

            self[entry2].setText(hour_datetime)
            self[entry3].setText(temp)
            self[entry4].setText(precipprob)

            if self[entry5].instance:
                self[entry5].instance.setPixmapFromFile(str(self.icon_path) + "others/precipprob-sm.png")

            index += 1

            if index == 15:
                break

        if index < 15:

            for hour in self.weather["days"][1]["hours"]:
                hour_datetime = str(hour["datetime"])[:-3]
                icon = str(self.icon_path) + "conditions/" + str(hour["icon"]) + ".png"
                temp = str(int(round(hour["temp"]))) + "°"
                if hour["precipprob"]:
                    precipprob = str(int(round(hour["precipprob"]))) + " %"
                else:
                    precipprob = "0 %"

                entry1 = "hour" + str(index) + "-icon"
                entry2 = "hour" + str(index) + "-time"
                entry3 = "hour" + str(index) + "-temp"
                entry4 = "hour" + str(index) + "-precipprob"
                entry5 = "hour" + str(index) + "-precip-icon"

                if self[entry1].instance:
                    self[entry1].instance.setPixmapFromFile(icon)

                self[entry2].setText(hour_datetime)
                self[entry3].setText(temp)
                self[entry4].setText(precipprob)

                if self[entry5].instance:
                    self[entry5].instance.setPixmapFromFile(str(self.icon_path) + "others/precipprob-sm.png")

                index += 1

                if index == 15:
                    break

    def days(self):
        index = 0
        for day in self.weather["days"]:
            datetimeEpoch = day["datetimeEpoch"]
            day_datetime = datetime.datetime.fromtimestamp(datetimeEpoch)
            weekday = day_datetime.strftime('%a')
            icon = str(self.icon_path) + "conditions/" + str(day["icon"]) + ".png"

            tempmax = str(int(round(day["tempmax"]))) + "°"
            tempmin = str(int(round(day["tempmin"]))) + "°"

            if day["precipprob"]:
                precipprob = str(int(round(day["precipprob"]))) + " %"
            else:
                precipprob = "0 %"

            entry1 = "day" + str(index) + "-icon"
            entry2 = "day" + str(index) + "-weekday"
            entry3 = "day" + str(index) + "-tempmax"
            entry4 = "day" + str(index) + "-tempmin"
            entry5 = "day" + str(index) + "-precipprob"
            entry6 = "day" + str(index) + "-precip-icon"

            if self[entry1].instance:
                self[entry1].instance.setPixmapFromFile(icon)

            self[entry2].setText(weekday)
            self[entry3].setText(tempmax)
            self[entry4].setText(tempmin)
            self[entry5].setText(precipprob)

            if self[entry6].instance:
                self[entry6].instance.setPixmapFromFile(str(self.icon_path) + "others/precipprob-sm.png")

            index += 1

    def current(self):
        self["location"].setText(str(self.location))
        self["conditions"].setText(str(self.current_conditions))
        self["temp"].setText(str(self.current_temp))
        self["feelslike"].setText(str(self.current_feelslike))
        self["tempmax"].setText(str(self.current_tempmax))
        self["tempmin"].setText(str(self.current_tempmin))
        self["precipprob"].setText(str(self.current_precipprob))

        if self["icon"].instance:
            self["icon"].instance.setPixmapFromFile(self.current_icon)

        if self["tempmax-icon"].instance:
            self["tempmax-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/tempmax.png")

        if self["tempmin-icon"].instance:
            self["tempmin-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/tempmin.png")

        if self["precipprob-icon"].instance:
            self["precipprob-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/precipprob.png")

        # not compact
        if not self.infobarskin or cfg.infobarsize.value == "full" or cfg.developer.value:
            self["description"].setText(str(self.description))
            self["sunrise"].setText(str(self.current_sunrise))
            self["sunset"].setText(str(self.current_sunset))

            self["humidity"].setText(str(self.current_humidity))
            self["uvindex"].setText(str(self.current_uvindextext))
            self["pressure"].setText(str(self.current_pressure))
            self["moonphase"].setText(str(self.current_moonphase_text))
            self["windspeed"].setText(str(self.current_windspeed))
            self["datetime"].setText(_("Last update: ") + str(self.current_datetime.strftime("%H:%M %A")))

            if self["moon-icon"].instance:
                self["moon-icon"].instance.setPixmapFromFile(self.current_moonphase_png)

            if self["wind-icon"].instance:
                self["wind-icon"].instance.setPixmapFromFile(self.current_wind_png)

            if self["sunrise-icon"].instance:
                self["sunrise-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/sunrise.png")

            if self["sunset-icon"].instance:
                self["sunset-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/sunset.png")

            if self["humidity-icon"].instance:
                self["humidity-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/humidity.png")

            if self["uvindex-icon"].instance:
                self["uvindex-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/uvindex.png")

            if self["pressure-icon"].instance:
                self["pressure-icon"].instance.setPixmapFromFile(str(self.icon_path) + "others/pressure.png")
