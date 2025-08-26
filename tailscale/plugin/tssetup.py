from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigText
from Components.Input import Input
from Components.About import about
from Tools.Directories import fileExists, fileContains, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language
from .tsnetwork import screenWidth
from Plugins.Extensions.Tailscale.__init__ import _
from Plugins.Extensions.Tailscale.tsnetwork import getData
from Screens.Standby import TryQuitMainloop
from enigma import eTimer
import gettext
import process
import json
import os
import requests
import shutil



class TailscaleSetup(Screen, ConfigListScreen):
	if screenWidth == 1920:
		skin="""<screen name="TailscaleSetup" position="center,120" size="1230,780">
			<eLabel name="" position="10,715" size="30,30" backgroundColor="red" />
			<eLabel name="" position="285,715" size="30,30" backgroundColor="green" />
			<eLabel name="" position="480,715" size="30,30" backgroundColor="yellow" />
			<eLabel name="" position="900,715" size="30,30" backgroundColor="blue" />
			<widget source="key_red" render="Label" position="50,715" size="230,45" zPosition="2" font="RegularHD; 18" halign="left" />
			<widget source="key_green" render="Label" position="325,715" size="100,45" zPosition="2" font="RegularHD; 18" halign="left" transparent="1" />
			<widget source="key_yellow" render="Label" position="520,715" size="350,45" zPosition="2" font="RegularHD; 18" halign="left" />
			<widget source="key_blue" render="Label" position="940,715" size="410,45" zPosition="2" font="RegularHD; 18" halign="left" transparent="1" />
			<widget name="config" position="0,10" size="1230,218" itemHeight="40" scrollbarMode="showNever" valueFont="RegularHD; 16" transparent="1" font="RegularHD; 22" />
			<widget name="description" position="20,500" size="1200,200" transparent="1" font="RegularHD; 20" />
			<widget name="HelpWindow" position="350,360" size="1,1" transparent="1" />
			</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ['TailscaleSetup']
		self.setup_title = _('Tailscale Settings')
		self.onChangedEntry = []
		self['OkCancelActions'] = ActionMap(['SetupActions', 'ColorActions', 'DirectionActions'],
		   {
		   'left': self.keyLeft,
		   'down': self.keyDown,
		   'up': self.keyUp,
		   'right': self.keyRight,
		   'cancel': self.keyCancel,
		   'ok': self.keySave,
		   'red': self.keyCancel,
		   'green': self.keySave,
		   'yellow': self.keyYellow,
		   'blue': self.openKeyboard,
		   }, -1)
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self['key_red'] = StaticText(_('Cancel'))
		self['key_green'] = StaticText(_('OK'))
		self['key_yellow'] = StaticText(_('Load Auth Key') if not fileContains("/tmp/tailscale.log", "key") else _('Update Tailscale'))
		self['key_blue'] = StaticText(_('Keyboard'))
		self["description"] = Label("")

		list = []
		if not fileContains("/tmp/tailscale.log", "key"):
			list.append(getConfigListEntry(_('Automatic Start'), config.tailscale.autostart, _('1. Enter your key by pressing BLUE or entering it manually in the file /etc/keys/tailscale.key\n2. Press YELLOW button.\n3. Press \"OK\".\nWait a few seconds until it shows \"Running\".')))
			list.append(getConfigListEntry(_('Auth key'), config.tailscale.apikey, _('1. Enter your key by pressing BLUE or entering it manually in the file /etc/keys/tailscale.key\n2. Press YELLOW button.\n3. Press \"OK\".\nWait a few seconds until it shows \"Running\".')))
		else:
			list.append(getConfigListEntry(_('Automatic Start'), config.tailscale.autostart, _('Enable/Disable automatic start when enigma2 boots')))
			list.append(getConfigListEntry(_('Auth key'), config.tailscale.apikey, _('Auth key to register your device in Tailscale.')))
		self.UpdateTimer = eTimer()
		self.UpdateTimer.timeout.get().append(self.mover)

		ConfigListScreen.__init__(self, list, session=session, on_change=self.changedEntry)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)
		self.Getinfo()
		self.loadKey()
		if isinstance(self["config"].getCurrent()[1], ConfigText):
			if "HelpWindow" in self:
				if self["config"].getCurrent()[1].help_window and self["config"].getCurrent()[1].help_window.instance is not None:
					helpwindowpos = self["HelpWindow"].getPosition()
					from enigma import ePoint
					self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

	def cancel(self):
		for i in self['config'].list:
			i[1].cancel()
		self.close(False)

	def Getinfo(self):
		description = self['config'].getCurrent()[2]
		self['description'].setText(description)

	def checkInstalled(self):
		return fileExists('/usr/sbin/tailscaled')

	def autostart(self):
		if config.tailscale.autostart.getValue()==True:
			if self.checkInstalled():
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc2.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc3.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc4.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc5.d/S60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc0.d/K60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc1.d/K60tailscale-daemon')
				os.system('ln -s /etc/init.d/tailscale-daemon /etc/rc6.d/K60tailscale-daemon')
		else:
			os.system('rm -f /etc/rc2.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc3.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc4.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc5.d/S60tailscale-daemon')
			os.system('rm -f /etc/rc0.d/K60tailscale-daemon')
			os.system('rm -f /etc/rc1.d/K60tailscale-daemon')
			os.system('rm -f /etc/rc6.d/K60tailscale-daemon')

	def saveAll(self):
		for x in self['config'].list:
			x[1].save()

		config.tailscale.autostart.save()
		config.tailscale.apikey.save()
		configfile.save()
		self.autostart()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.Getinfo()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.Getinfo()

	def keyDown(self):
		self['config'].instance.moveSelection(self['config'].instance.moveDown)
		self.Getinfo()

	def keyUp(self):
		self['config'].instance.moveSelection(self['config'].instance.moveUp)
		self.Getinfo()

	def keySave(self):
		self.saveAll()
		os.system('tailscale up --authkey ' + config.tailscale.apikey.value)
		self.close()

	def keyYellow(self):
		if not fileContains("/tmp/tailscale.log", "key"):
			self.keyDown()
			filekey = '/etc/keys/tailscale.key'
			if os.path.exists(filekey):
				f = open(filekey, 'r')
				authkey = f.read()
				f.close()
				config.tailscale.apikey.value = authkey
				self.saveAll()
				self.keyUp()
		else:
			self.arq=about.getCPUArch()
			if self.arq=="Mipsel":
				self.arq="mipsle"
			print('arquitectura: ', self.arq)
			web="https://pkgs.tailscale.com/stable/#static"
			soup=requests.get(web).content
			self.version = soup.decode().split('<li>386: <a href="tailscale_')[1].split("_386")[0]
			print('versio: ', self.version)
			p = process.ProcessList()
			tailscale_process = str(p.named('tailscaled')).strip('[]')
			if tailscale_process:
				networks = json.loads(getData())
				version_actual=networks.get('Version').split("-")[0]
				if self.version!=version_actual:
					self.session.openWithCallback(self.actualizar, MessageBox, _('New version found.\nCurrent version: %s\nNew version: %s\nDo you want to install?') % (version_actual,self.version), MessageBox.TYPE_YESNO)
				else:
					self.session.open(MessageBox, _('Last version installed'), MessageBox.TYPE_INFO, timeout=5)

	def actualizar(self, raw):
		if raw:
			url = "https://pkgs.tailscale.com/stable/tailscale_%s_%s.tgz" % (self.version, self.arq.lower())
			self.tmpath = '/tmp/tailscale.tgz'
			os.system("wget -qO '"+self.tmpath+"' '"+str(url)+"'")
			os.system("sleep 5&&cd /tmp&&tar xvf /tmp/tailscale.tgz --strip-components=1 tailscale_%s_%s/tailscale tailscale_%s_%s/tailscaled" % (self.version, self.arq.lower(), self.version, self.arq.lower()))
			self.pararT()
		else:
			self.close()

	def pararT(self):
		p = process.ProcessList()
		tailscale_process = str(p.named('tailscaled')).strip('[]')
		if tailscale_process:
			os.system('/etc/init.d/tailscale-daemon stop')
		else:
			os.system('/etc/init.d/tailscale-daemon start')
		self.UpdateTimer.start(5000, True)

	def mover(self):
		shutil.move('/tmp/tailscaled', '/usr/sbin/tailscaled')
		shutil.move('/tmp/tailscale', '/usr/bin/tailscale')
		self.session.openWithCallback(self.reboot, MessageBox, _('Your receiver needs to reboot\nDo you want to do it now?'), type=MessageBox.TYPE_YESNO)

	def reboot(self, answer):
		if answer:
			self.session.open(TryQuitMainloop, 2)

	def loadKey(self):
		filekey = '/etc/keys/tailscale.key'
		if os.path.exists(filekey):
			f = open(filekey, 'r')
			authkey = f.read()
			f.close()
			config.tailscale.apikey.value = authkey
			self.saveAll()

	def openKeyboard(self):
		self.session.openWithCallback(self.CallbackInput, VirtualKeyBoard, title=(_("Enter your Auth Key")), text=config.tailscale.apikey.getValue())

	def CallbackInput(self, id=None):
		if id:
			config.tailscale.apikey.setValue(id)
			self.session.open(MessageBox, _('Execution finished.'), type=MessageBox.TYPE_INFO, timeout=5)

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self['config'].getCurrent()[0]

	def getCurrentValue(self):
		return str(self['config'].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary
