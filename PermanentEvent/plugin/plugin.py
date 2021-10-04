# PermanentEvent (v2.0)
# Code by Villak OpenSPA Team for PermanentEvent 2021
# This plugin is free software, you can
# modify it (if you keep the license),
# but it is not allowed to distribute/publish without the permission of the author
# you must respect the source code (this version and its modifications).
# This means that you also have to distribute
# source code of your modifications.

from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language
from Components.config import config
from boxbranding import getImageDistro
from enigma import addFont, getDesktop
from skin import loadSkin
import gettext
import threading
from . import permanent
from . import download

skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PermanentEvent/skins/")
font = resolveFilename(SCOPE_PLUGINS, "Extensions/PermanentEvent/font")
PluginLanguageDomain = "PermanentEvent"
PluginLanguagePath = "Extensions/PermanentEvent/locale/"

HD = getDesktop(0).size()
if HD.width() > 1280:
	loadSkin(skin_path + 'permanent_fhd.xml')
else:
	loadSkin(skin_path + 'permanent_hd.xml')

try:
	addFont("%s/autumn.ttf" % font, "Autumn", 120, 1)
	addFont("%s/EventHD.ttf" % font, "EventHD", 153, 1)
except Exception as ex:
	print(ex)

def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
language.addCallback(localeInit())

def ddwn():
	if config.plugins.PermanentEvent.timerMod.value == True:
		download.downloads("").save()
	if config.plugins.PermanentEvent.timerMod.value == True:
		tmr = config.plugins.PermanentEvent.timer.value
		t = threading.Timer(3600*int(tmr), ddwn) # 1h=3600
		t.start()
if config.plugins.PermanentEvent.timerMod.value == True:
	threading.Timer(30, ddwn).start()

def startConfig(session, **kwargs):
		session.open(permanent.PermanentEventMenu)

def main(menuid):
		if menuid != 'system':
			return []
		return [(_('Permanent Event'),
			startConfig,
			'permanent_event',
			None)]

def Plugins(**kwargs):
		if getImageDistro() in ('openspa'):
				return [
				PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=permanent.sessionstart), 
				PluginDescriptor(name=_('Permanent Event'), description=_('Shows the event permanent on the screen'), where=PluginDescriptor.WHERE_MENU, fnc=main)]
		else:
				return [
				PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=permanent.sessionstart), 
				PluginDescriptor(name=_('Permanent Event'), description=_('Shows the event permanent on the screen'), where=[PluginDescriptor.WHERE_PLUGINMENU], icon='event.png', fnc=startConfig)]
