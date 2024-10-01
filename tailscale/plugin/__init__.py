# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import gettext

PluginLanguageDomain = "Tailscale"
PluginLanguagePath = "Extensions/Tailscale/locale"

def localeInit():
	lang = language.getLanguage()
	environ["LANGUAGE"] = lang[:2]
	print("[tailscale] set language to ", lang)
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		print("[" + PluginLanguageDomain + "] fallback to default translation for " + txt)
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
