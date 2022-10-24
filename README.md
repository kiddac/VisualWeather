# VisualWeather
15 day weather forecasts by KiddaC

Plugin incorporates the use of https://www.visualcrossing.com/ weather api. Visual crossings api is very good at finding your local location and uses multiple nearby weather stations for accuracy.

Free sign up required at https://www.visualcrossing.com/ to get your free API key. No credit card required.

Your personal API key can be entered via the plugin or manually pasting into /etc/enigma2/VisualWeather/apikey.txt

Note to skinners


Plugin lives here: /usr/lib/enigma2/python/Plugins/Extensions/VisualWeather


Weather Icons

Icon sets live here: /usr/lib/enigma2/python/Plugins/Extensions/VisualWeather/weather-icons

There are currently 4 icon sets provided in the plugin. 3D - Set 1, 3D - Set 2, Flat, Simple.

Icons have been sourced from free sets available on the net and tweaked by me.

Icons are 96x96 pixels. Except a smaller precipitation icon used in 15 day weather which is 32x32 pixels.

Scaling is turned on in my skin files, but enigma2 scales badly. So best to add any new icons at these sizes.

To add new icon sets add a new folder to the weather-icons folder.


Custom skins
Skins live here: /usr/lib/enigma2/python/Plugins/Extensions/VisualWeather/skins

I provide one default skin set for 15 day, compact widget, full widget

To add a new skin add a new folder to the /skins/ folder.


There a 3 skin files per skin

forecast.xml - 15 day forecast

infobar.xml - full infobar widget

infobarcompact.xml - compact infobar widget


All elements that can be used in any of the 3 screens can be copied from forecast.xml into the other screens.

To allow elements to be used that are not in my default skin for infobar.xml and infobarcompact.xml please turn skin developer mode on in the plugin settings. This option initiates all variables for all screens.

** do note though, unused elements will cause lots of noise in debug logs if you have debug logs turned on **
