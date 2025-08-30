# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import gettext
from skin import loadSkin
from enigma import getDesktop

PluginLanguageDomain = "spzCAMD"
PluginLanguagePath = "Extensions/spzCAMD/locale"

def esHD():
	screenWidth = getDesktop(0).size().width()
	return screenWidth > 1400

def localeInit():
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		print("[" + PluginLanguageDomain + "] fallback to default translation for " + txt)
		t = gettext.gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)

loadSkin("%s%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/spzCAMD/skins/", "skinsHD.xml" if esHD() else "skins.xml"), replace = False)
