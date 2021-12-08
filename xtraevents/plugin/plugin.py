# -*- coding: utf-8 -*-
# by digiteng...(digiteng@gmail.com)
# https://github.com/digiteng/
# 06.2020 - 11.2020(v2.0)
from Plugins.Plugin import PluginDescriptor
from Components.config import config
import threading
from . import xtra
from . import download
from six.moves import reload_module
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext
import os

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("xtraEvent", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/xtraEvent/locale/"))

def _(txt):
	t = gettext.dgettext("xtraEvent", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def ddwn():
	if config.plugins.xtraEvent.timerMod.value == True:
		download.downloads("").save()
	if config.plugins.xtraEvent.timerMod.value == True:
		tmr = config.plugins.xtraEvent.timer.value
		t = threading.Timer(3600*int(tmr), ddwn) # 1h=3600
		t.start()
if config.plugins.xtraEvent.timerMod.value == True:
	threading.Timer(30, ddwn).start()

def main(session, **kwargs):
	reload_module(xtra)
	reload_module(download)
	try:
		session.open(xtra.xtra)
	except:
		import traceback
		traceback.print_exc()

def Plugins(**kwargs):
	return [PluginDescriptor(name="xtraEvent", description="xtraEvent plugin...", where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)]
