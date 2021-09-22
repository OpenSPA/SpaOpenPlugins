# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
from enigma import getDesktop
import gettext
import sys

def py3():
	if sys.version_info[0] == 3:
		return True
	else:
		return False

def esHD():
	if getDesktop(0).size().width() > 1400:
		return True
	else:
		return False

def fhd(num, factor=1.5):
	if esHD():
		prod=num*factor
	else: prod=num
	return int(round(prod))

def fontHD(nombre):
	if esHD():
		fuente = nombre+"HD"
	else:
		fuente = nombre
	return fuente

def localeInit():
	gettext.bindtextdomain("spzRemoteChannels", resolveFilename(SCOPE_PLUGINS, "Extensions/spzRemoteChannels/locale"))

def _(txt):
	t = gettext.dgettext("spzRemoteChannels", txt)
	if t == txt:
		print("[spzRemoteChannels] fallback to default translation for", txt)
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
