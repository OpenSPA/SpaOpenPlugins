# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os, gettext, hashlib
from functools import reduce
import sys
from enigma import getDesktop
PluginLanguageDomain = "MyTube"
PluginLanguagePath = "Extensions/MyTube/locale"

def localeInit():
	lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
	os.environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
	print("[MyTube] set language to ", lang)
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
	if gettext.dgettext(PluginLanguageDomain, txt):
		return gettext.dgettext(PluginLanguageDomain, txt)
	else:
		print("[" + PluginLanguageDomain + "] fallback to default translation for " + txt)
		return gettext.gettext(txt)

localeInit()
language.addCallback(localeInit())

def bin2long(s):
	return reduce( lambda x,y:(x<<8)+y, list(map(ord, s)))

def long2bin(l):
	res = ""
	for byte in range(128):
		res += chr((l >> (1024 - (byte + 1) * 8)) & 0xff)
	return res

def rsa_pub1024(src, mod):
	return long2bin(pow(bin2long(src), 65537, bin2long(mod)))
	
def decrypt_block(src, mod):
	if len(src) != 128 and len(src) != 202:
		return None
	dest = rsa_pub1024(src[:128], mod)
	hash = hashlib.sha1(dest[1:107])
	if len(src) == 202:
		hash.update(src[131:192])	
	result = hash.digest()
	if result == dest[107:127]:
		return dest
	return None

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


