#!/usr/bin/env python
# -*- coding: utf-8 -*-
#original plugin by mfaraj57
#Code by VillaK 2018-2021
#Code Speedtest-cli from source https://github.com/sivel/speedtest-cli
#This plugin is free software, you can
#modify it (if you keep the license),
#but it is not allowed to distribute/publish without the permission of the author
#you must respect the source code (this version and its modifications).
#This means that you also have to distribute
#source code of your modifications.

from __future__ import print_function
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.config import ConfigText, ConfigSubsection, config, configfile
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Language import language
from boxbranding import getBoxType, getMachineBrand, getMachineName
from enigma import getDesktop, eConsoleAppContainer
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import path
from skin import loadSkin
try:
	from urllib.request import urlretrieve
except ImportError:
	from urllib import urlretrieve
import gettext
import os,sys

plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/openSPAnetTest/speedtest.pyo'
skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/openSPAnetTest/skins/")
png_tmp = '/tmp/resultest.png'
font = resolveFilename(SCOPE_PLUGINS, "Extensions/openSPAnetTest/fonts")
cmd= 'python ' + plugin_path + ' --no-pre-allocate --share'

HD = getDesktop(0).size()
if HD.width() > 1280:
	loadSkin(skin_path + 'speednetest_1080.xml')
else:
	loadSkin(skin_path + 'speednetest_720.xml')

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("openSPAnetTest", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/openSPAnetTest/locale/"))

def _(txt):
	t = gettext.dgettext("openSPAnetTest", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

from enigma import addFont
try:
	addFont("%s/tuxtxt.ttf" % font, "Console", 100, 1)
except Exception as ex:
	print(ex)

opennetVersion = "2.0"
opennetabout = _(" Plugin OpenSPAnetTest " +opennetVersion+ "\n MOD by VillaK 2018-2021 OpenSPA Team.\n Credits to mfaraj57 and madhouse. ")

class SpeedTestScreen(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self['introduction'] = Label(_('Choose your option, to test.'))
		self['Title'] = Label(_('OpenSPA netSpeedTest'))
		self.container = eConsoleAppContainer()
		self["key_red"] = Label(_("Select your favourite server."))
		self["key_green"] = Label(_("Test auto server."))
		self["key_yellow"] = Label(_("Test your favourite server."))
		self["key_blue"] = Label(_("View last result to share."))
		self['key_info'] = Label(_("About"))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'SetupActions','DirectionActions'], 
		{'cancel': self.close,
		'green': self.speedauto,
		'back': self.close, 
		'red': self.favser, 
		'yellow': self.speedfav,
		"info": self.about,
		'blue': self.viewshare
		}, -1)

	def viewshare(self):
		if path.exists(png_tmp):
			self.session.open(sharesult)
		else:
			self.session.open(MessageBox,(_("Test result not exist, first do the test.")), MessageBox.TYPE_INFO, timeout = 3)

	def speedauto(self):
		self.session.open(SpeedTestScreenauto)

	def speedfav(self):
		self.session.open(SpeedTestScreenfav)

	def favser(self):
		self.session.open(serversel)

	def about(self, dummy=None):
		self.session.open(MessageBox, opennetabout, MessageBox.TYPE_INFO)

class SpeedTestScreenauto(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self['data'] = Label(_('Testing internet speed, please wait...'))
		self['ping'] = Label(" ")
		self['host'] = Label(" ")
		self['ip'] = Label(" ")
		self['download'] = Label(" ")
		self['upload'] = Label(" ")
		self["key_green"] = Label(_(" "))
		self['green'] = Pixmap()
		self["green"] .hide()
		self["key_blue"] = Label(" ")
		self['blue'] = Pixmap()
		self["blue"].hide()
		self["key_yellow"] = Label(" ")
		self['yellow'] = Pixmap()
		self["yellow"].hide()
		self['image'] = Pixmap()
		self['actions'] = ActionMap(['OkCancelActions','ColorActions'],{'cancel': self.exit,'green': self.testagain, 'blue': self.viewshare, 'yellow': self.donwl},-1)
		self.removepng()
		self.finished=False
		self.data=''
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.action)
		self.container.dataAvail.append(self.dataAvail)
		self.container.execute(cmd)

	def testagain(self):
		if  self.finished==False:
			return
		self.data=''
		self['data'].setText(_("Testing internet speed, please wait..."))
		self['ping'].setText(" ")
		self['host'].setText(" ")
		self['ip'].setText(" ")
		self['download'].setText(" ")
		self['upload'].setText(" ")
		self['green'].hide()
		self["key_green"].setText(" ")
		self["key_yellow"].setText(" ")
		self["yellow"].hide()
		self['blue'].hide()
		self["key_blue"].setText(" ")
		self.removepng()
		self.container.execute(cmd)

	def action(self, retval):
		print("retval",retval)
		print(_("finished test"))
		self.finished=True

	def dataAvail(self, rstr):
		if rstr:
			rstr=str(rstr.decode())
			self.data=self.data+rstr
			parts=rstr.split("\n")
			for part in parts:
				if 'Hosted by' in part:
					try:
						host = part.split('Hosted by')[1].strip()
					except:
						host = ''
					self['host'].setText(str(host))
				if 'Ping' in part:
					try:
						ping = rstr.split('Ping')[1].strip()
					except:
						ping = ''
					self['ping'].setText(str(ping))
				if 'Testing download from' in part:
					ip = part.split('Testing download from')[1].split(')')[0].replace('(','').strip()
					self['ip'].setText(str(ip))
					self.data = (_('Testing download from'))
				if 'Download:' in rstr:
					try:
						download = rstr.split(':')[1].split('\n')[0].strip()
					except:
						download = ''
					self['download'].setText(str(download))
					self.data = (_('Testing upload speed'))
				if 'Upload:' in rstr:
					try:
						upload = rstr.split(':')[1].split('\n')[0].strip()
					except:
						upload = ''
					self['upload'].setText(str(upload))
				if 'Share results:' in rstr:
					try:
						url_results = rstr.split()[2]
					except:
						url_results = ''
					self.url_png = str(url_results)
					self.data = (_("Test completed,to test again press green"))
					self["key_green"].setText(_('Test again'))
					self["green"].show()
					try:
						urlretrieve(self.url_png, png_tmp)
					except Exception as e:
							print(e)
							self.donwl()
					if path.exists(png_tmp):
						self["key_blue"].setText(_('Show results'))
						self["blue"].show()
						self["key_yellow"].setText(" ")
						self["yellow"].hide()
					else:
						self["blue"].show()
						self['key_blue'].setText(_('Download resultest.png failed!'))
						self["key_yellow"].setText(_('Download result'))
						self["yellow"].show()
				self['data'].setText(_(self.data).replace('Hosted by', '').replace('.', ''))

	def donwl(self):
		try:
			urlretrieve(self.url_png, png_tmp)
		except Exception as e:
			print(e)
		if path.exists(png_tmp):
			self['key_blue'].setText(_('Show results'))
			self['blue'].show()
			self["key_yellow"].setText(" ")
			self["yellow"].hide()
		else:
				self['data'].setText(_('Download speedtest.png failed!'))
				self["key_yellow"].setText(_('Download result'))
				self["yellow"].show()

	def viewshare(self):
		if path.exists(png_tmp):
			self.session.open(sharesult)
		else:
			self.session.open(MessageBox,(_("Test result not exist, first do the test.")), MessageBox.TYPE_INFO, timeout = 3)

	def removepng(self):
		try:
			if path.exists(png_tmp):
				os.remove("/tmp/resultest.png")
		except:
			pass

	def exit(self):
		self.container.appClosed.remove(self.action)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()

config.speedtest = ConfigSubsection()
config.speedtest.server = ConfigText(default="14539", visible_width = 250, fixed_size = False)
class serversel(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self['introduction'] = Label(_('Choose server and press ok, to test.'))
		self['Title'] = Label(_('OpenSPA netSpeedTest Server List'))
		self.resultlist = []
		self['list'] = MenuList(self.resultlist)
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Ok"))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'SetupActions','DirectionActions'], 
		{'cancel': self.exit,
		'ok': self.okClicked, 
		'green': self.okClicked, 
		'back': self.exit, 
		'red': self.exit, 
		'left': self.pageUp, 
		'right': self.pageDown, 
		'down': self.moveDown, 
		'up': self.moveUp 
		}, -1)
		self.showMenu()

	def pageUp(self):
		self['list'].instance.moveSelection(self['list'].instance.pageUp)

	def pageDown(self):
		self['list'].instance.moveSelection(self['list'].instance.pageDown)

	def moveUp(self):
		self['list'].instance.moveSelection(self['list'].instance.moveUp)

	def moveDown(self):
		self['list'].instance.moveSelection(self['list'].instance.moveDown)

	def exit(self):
		self.close()

	def showMenu(self):
		try:
			import subprocess
			myfavserv= subprocess.Popen(['python', '/usr/lib/enigma2/python/Plugins/Extensions/openSPAnetTest/speedtest.pyo', '--list'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			stdout,stderr = myfavserv.communicate()
			PY3 = (sys.version_info[0] == 3)
			try:
				if PY3:
					results = stdout.decode().split("\n")
				else:
					results = stdout.split("\n")
			except:
				pass
		except:
			results = []
			if results == 0:
				return False
		self.resultlist = []
		for searchResult in results:
			try:
				self.resultlist.append(searchResult)
			except:
				pass
		self['list'].setList(self.resultlist)

	def okClicked(self):
		id = self['list'].getCurrent()
		part = id.partition(")")
		if part:
			config.speedtest.server.value = (part[0])
			config.speedtest.server.save()
			configfile.save()
			self.session.openWithCallback(self.quit,SpeedTestScreenfav)

	def quit(self):
		self.close()

class sharesult(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self['info'] = Label(_('In the path /tmp/resultest.png you have your result, in order to share it. Or you can use the mobile to download your result, (with OpteleBot)...\n/desc /tmp/resultest.png'))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'SetupActions'], {'ok': self.close, 'back': self.close, 'red': self.close})
		self['stb'] = Label (_('Test in: %s %s') % (getMachineBrand(), getMachineName()))

class SpeedTestScreenfav(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self['data'] = Label(_('Testing internet speed, please wait...'))
		self['ping'] = Label(" ")
		self['host'] = Label(" ")
		self['ip'] = Label(" ")
		self['download'] = Label(" ")
		self['upload'] = Label(" ")
		self["key_green"] = Label(_(" "))
		self['green'] = Pixmap()
		self["green"] .hide()
		self["key_blue"] = Label(" ")
		self['blue'] = Pixmap()
		self["blue"].hide()
		self["key_yellow"] = Label(" ")
		self['yellow'] = Pixmap()
		self["yellow"].hide()
		self['image'] = Pixmap()
		self['actions'] = ActionMap(['OkCancelActions','ColorActions'],{'cancel': self.exit,'green': self.testagain, 'blue': self.viewshare, 'yellow': self.donwl},-1)
		self.server = config.speedtest.server.value
		cmd='python ' + plugin_path + ' --no-pre-allocate --server %s --share' % (self.server)
		self.removepng()
		self.finished=False
		self.data=''
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.action)
		self.container.dataAvail.append(self.dataAvail)
		self.container.execute(cmd)

	def testagain(self):
		if  self.finished==False:
			return
		self.data=''
		self['data'].setText(_("Testing internet speed, please wait..."))
		self['ping'].setText(" ")
		self['host'].setText(" ")
		self['ip'].setText(" ")
		self['download'].setText(" ")
		self['upload'].setText(" ")
		self['green'].hide()
		self["key_green"].setText(" ")
		self["key_yellow"].setText(" ")
		self["yellow"].hide()
		self['blue'].hide()
		self["key_blue"].setText(" ")
		cmd='python ' + plugin_path + ' --no-pre-allocate --server %s --share' % (self.server)
		self.removepng()
		self.container.execute(cmd)

	def action(self, retval):
		print("retval",retval)
		print(_("finished test"))
		self.finished=True

	def dataAvail(self, rstr):
		if rstr:
			rstr=str(rstr.decode())
			self.data=self.data+rstr
			parts=rstr.split("\n")
			for part in parts:
				if 'Hosted by' in part:
					try:
						host = part.split('Hosted by')[1].strip()
					except:
						host = ''
					self['host'].setText(str(host))
				if 'Ping' in part:
					try:
						ping = rstr.split('Ping')[1].strip()
					except:
						ping = ''
					self['ping'].setText(str(ping))
				if 'Testing download from' in part:
					ip = part.split('Testing download from')[1].split(')')[0].replace('(','').strip()
					self['ip'].setText(str(ip))
					self.data = (_('Testing download from'))
				if 'Download:' in rstr:
					try:
						download = rstr.split(':')[1].split('\n')[0].strip()
					except:
						download = ''
					self['download'].setText(str(download))
					self.data = (_('Testing upload speed'))
				if 'Upload:' in rstr:
					try:
						upload = rstr.split(':')[1].split('\n')[0].strip()
					except:
						upload = ''
					self['upload'].setText(str(upload))
				if 'Share results:' in rstr:
					try:
						url_results = rstr.split()[2]
					except:
						url_results = ''
					self.url_png = str(url_results)
					self.data = (_("Test completed,to test again press green"))
					self["key_green"].setText(_('Test again'))
					self["green"].show()
					try:
						urlretrieve(self.url_png, png_tmp)
					except Exception as e:
							print(e)
							self.donwl()
					if path.exists(png_tmp):
						self["key_blue"].setText(_('Show results'))
						self["blue"].show()
						self["key_yellow"].setText(" ")
						self["yellow"].hide()
					else:
						self["blue"].show()
						self['key_blue'].setText(_('Download resultest.png failed!'))
						self["key_yellow"].setText(_('Download result'))
						self["yellow"].show()
				self['data'].setText(_(self.data).replace('Hosted by', '').replace('.', ''))

	def donwl(self):
		try:
			urlretrieve(self.url_png, png_tmp)
		except Exception as e:
			print(e)
		if path.exists(png_tmp):
			self['key_blue'].setText(_('Show results'))
			self['blue'].show()
			self["key_yellow"].setText(" ")
			self["yellow"].hide()
		else:
				self['data'].setText(_('Download speedtest.png failed!'))
				self["key_yellow"].setText(_('Download result'))
				self["yellow"].show()

	def viewshare(self):
		if path.exists(png_tmp):
			self.session.open(sharesult)
		else:
			self.session.open(MessageBox,(_("Test result not exist, first do the test.")), MessageBox.TYPE_INFO, timeout = 3)

	def exit(self):
		self.container.appClosed.remove(self.action)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()

	def removepng(self):
		try:
			if path.exists(png_tmp):
				os.remove("/tmp/resultest.png")
		except:
			pass

def main(session,**kwargs):
	session.open(SpeedTestScreen)

def Plugins(**kwargs):
	result = [
	PluginDescriptor(name=_("OpenSPAnetTest"),
	description=_("SpeedNetTest by openSPA"),
	where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
	icon="OpnetTest.png",
	fnc=main)]
	return result