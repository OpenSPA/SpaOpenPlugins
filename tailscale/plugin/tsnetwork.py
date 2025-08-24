from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Components.config import config, configfile
from Components.Sources.List import List
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Input import Input
from Tools.BoundFunction import boundFunction
from Tools.Directories import fileContains, fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from enigma import eTimer, getDesktop
from time import time
from datetime import datetime
from Components.Language import language
from Plugins.Extensions.Tailscale.__init__ import _
from requests.auth import HTTPBasicAuth
import json
import process
import subprocess
import requests
import os

screenWidth = getDesktop(0).size().width()


def getData():
	dato = os.popen("tailscale status --json")
	data = dato.read()
	return data

class TailscaleNetwork(Screen):
	if screenWidth == 1920:
		skin = """
		<screen name="Tailscale" position="center,120" size="1230,780" title=" ">
			<widget name="picRed" pixmap="buttons/red_HD.png" position="60,707" size="210,60" alphatest="blend" transparent="1" />
			<widget name="picGreen" pixmap="buttons/green_HD.png" position="360,707" size="210,60" alphatest="blend" transparent="1" />
			<widget name="picYellow" pixmap="buttons/yellow_HD.png" position="660,707" size="210,60" alphatest="blend" transparent="1" />
			<widget name="picBlue" pixmap="buttons/blue_HD.png" position="960,707" size="210,60" alphatest="blend" transparent="1" />
			<widget name="lblRed" position="15,707" size="300,60" zPosition="1" font="RegularHD;17" halign="center" valign="center" transparent="1" />
			<widget name="lblGreen" position="315,707" size="300,60" zPosition="1" font="RegularHD;17" halign="center" valign="center" transparent="1" />
			<widget name="lblYellow" position="615,707" size="300,60" zPosition="1" font="RegularHD;17" halign="center" valign="center" transparent="1" />
			<widget name="lblBlue" position="915,707" size="300,60" zPosition="1" font="RegularHD;17" halign="center" valign="center" transparent="1" />
			<widget source="list" render="Listbox" position="12,68" size="1200,630" scrollbarMode="showOnDemand" enableWrapAround="on">
				<convert type="TemplatedMultiContent">
					{ "template": [ MultiContentEntryText(pos=(135,2),size=(1080,45),font=0,text=4),
					MultiContentEntryPixmapAlphaBlend(pos=(24,15),size=(90,90),png=1),
					MultiContentEntryPixmapAlphaBlend(pos=(38,15),size=(75,75),png=2),
					MultiContentEntryText(pos=(135,42),size=(1080,66),font=1,text=3,color=0xa0a0a0),
					MultiContentEntryPixmapAlphaBlend(pos=(0,0),size=(1200,3),png=5)],
					"fonts": [gFont("RegularHD",22),gFont("RegularHD",17)],
					"itemHeight": 112
					}
				</convert>
			</widget>
			<eLabel name="menu" text="Menu" position="1050,15" size="100,45" font="RegularHD;18" backgroundColor="key_back" zPosition="2"/>
			<widget name="picMenu" position="1060,20" size="75,37" pixmap="buttons/key_menu.png" transparent="1" alphatest="blend" />
			<widget name="lblStatus" position="19,9" size="1100,51" font="RegularHD;20" zPosition="2" transparent="1"/>
		</screen>"""
	else:
		skin = """
		<screen name="Tailscale" position="center,120" size="820,520" title=" ">
			<widget name="picRed" pixmap="buttons/red.png" position="40,471" size="140,40" alphatest="blend" transparent="1" />
			<widget name="picGreen" pixmap="buttons/green.png" position="240,471" size="140,40" alphatest="blend" transparent="1" />
			<widget name="picYellow" pixmap="buttons/yellow.png" position="440,471" size="140,40" alphatest="blend" transparent="1" />
			<widget name="picBlue" pixmap="buttons/blue.png" position="640,471" size="140,40" alphatest="blend" transparent="1" />
			<widget name="lblRed" position="10,471" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" transparent="1" />
			<widget name="lblGreen" position="210,471" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" transparent="1" />
			<widget name="lblBlue" position="610,471" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" transparent="1" />
			<widget source="list" render="Listbox" position="8,45" size="800,420" scrollbarMode="showOnDemand" enableWrapAround="on">
				<convert type="TemplatedMultiContent">
					{ "template": [ MultiContentEntryText(pos = (90,1),size = (720,30),font=0,text=4),
					MultiContentEntryPixmapAlphaBlend(pos = (20,15),size = (60,60),png=1),
					MultiContentEntryPixmapAlphaBlend(pos = (25,10),size = (50,50),png=2),
					MultiContentEntryText(pos = (90,28),size = (720,44),font=1,text=3,color=0xa0a0a0),
					MultiContentEntryPixmapAlphaBlend(pos = (0,0),size = (800,2),png=5)],
					"fonts": [gFont("Regular",22),gFont("Regular",17)],
					"itemHeight": 74
					}
				</convert>
			</widget>
			<widget name="picMenu" position="760,14" size="50,24" pixmap="buttons/key_menu.png" transparent="1" alphatest="blend" />
			<widget name="lblStatus" position="12,6" size="733,34" font="Regular;20" zPosition="2" />
		</screen> """

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ['Tailscale']
		self['actions'] = ActionMap(['ColorActions', 'MenuActions', 'OkCancelActions'],
			{
				"menu": self.KeyMenu,
				"cancel": self.keyExit,
				"green": self.keyGreen,
				"red": self.keyRed,
				"yellow": self.keyYellow,
				"blue": self.keyBlue,
			}, -2)
		self['list'] = List()
		self['lblStatus'] = Label()
		self['picMenu'] = Pixmap()
		self['picRed'] = Pixmap()
		self['lblRed'] = Label(_('Stop'))
		self['picGreen'] = Pixmap()
		self['lblGreen'] = Label('')
		self['picYellow'] = Pixmap()
		self['lblYellow'] = Label(_('Devices'))
		self['picBlue'] = Pixmap()
		self['lblBlue'] = Label(_('Disable Daemon'))

		self.checkLogin()
		self.line = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Tailscale/images/div-h.png')
		if screenWidth == 1920:
			self.networkpic = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Tailscale/images/network-hd.png')
		else:
			self.networkpic = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Tailscale/images/network.png')

		self.ListTimer = eTimer()
		self.ListTimer.timeout.get().append(self.UpdateEntry)

		self.UpdateTimer = eTimer()
		self.UpdateTimer.timeout.get().append(self.UpdateStatus)

		self['list'].onSelectionChanged.append(self.selectionChanged)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.UpdateTitle()
		self.UpdateTimer.start(300, True)

	def UpdateTitle(self):
		self.setTitle(_('Tailscale Network'))

	def UpdateStatusLabel(self):
		p = process.ProcessList()
		tailscale_process = str(p.named('tailscaled')).strip('[]')
		if tailscale_process:
			stat = _('Actived')
			self['picGreen'].show()
			if fileContains("/tmp/tailscale.log", "key"):
				self['lblGreen'].setText(_('Start'))
			self['lblBlue'].show()
			self['lblBlue'].setText(_('Disable Daemon'))
		else:
			stat = _('Not Running')
			self['picGreen'].hide()
			self['lblGreen'].hide()
			self['picRed'].hide()
			self['lblRed'].hide()
			self['lblBlue'].setText(_('Enable Daemon'))
		self['lblStatus'].setText(_('Tailscale-Daemon: ') + stat)

	def UpdateStatus(self):
		self.listNetwork()
		self.UpdateStatusLabel()
		self.UpdateTimer.start(15000, True)

	def KeyMenu(self):
		from Plugins.Extensions.Tailscale.tssetup import TailscaleSetup
		self.session.open(TailscaleSetup)

	def keyExit(self):
		config.tailscale.save()
		self.close()

	def selectionChanged(self):
		self.ListTimer.start(400, True)

	def UpdateEntry(self):
		sel = self['list'].getCurrent()
		if sel:
			self['picRed'].show()
			self['lblRed'].show()
		else:
			self['picRed'].hide()
			self['lblRed'].hide()

	def listNetwork(self):
		p = process.ProcessList()
		tailscale_process = str(p.named('tailscaled')).strip('[]')
		index = self['list'].getIndex()
		mlist = []
		if tailscale_process:
			networks = json.loads(getData())
			text0 = '%s: %s ' % (_('Device'), networks.get('Self')['HostName'])
			text0 = text0 + '                                    %s: %s ' % (_('Version'), networks.get('Version').split("-")[0])
			text1 = '%s: %s\n' % (_('Status'), _(networks.get('BackendState')))
			if networks.get('BackendState') == "NeedsLogin" or networks.get('AuthURL') != "" or not networks.get('TailscaleIPs'):
				text1 += _("Press Menu button and enter Auth Key to register device")
			else:
				text1 += '%s: %s' % ('IP', networks.get('TailscaleIPs')[0])
			mlist.append((networks, self.networkpic, None, str(text1), str(text0), self.line))
			self['list'].setList(mlist)
			self['list'].setIndex(index)
			return
		else:
			del mlist[:]
			self['list'].setList(mlist)
			return

	def checkLogin(self):
		command = 'tailscale lock'
		processout = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
		output = processout.communicate()
		with open("/tmp/tailscale.log", "w") as fw:
			fw.write(output[0])

	def keyGreen(self):
		self.checkLogin()
		p = process.ProcessList()
		tailscale_process = str(p.named('tailscaled')).strip('[]')
		if not fileContains("/tmp/tailscale.log", "key"):
			return
		else:
			if tailscale_process:
				os.system("tailscale up")
				self.UpdateTimer.start(2000, True)

	def keyRed(self):
		p = process.ProcessList()
		tailscale_process = str(p.named('tailscaled')).strip('[]')
		if tailscale_process:
			os.system("tailscale down")
			self.UpdateTimer.start(2000, True)

	def keyYellow(self):
		devicelist = []
		if not fileContains("/etc/keys/tailscale_api.key", "tskey"):
			self.session.open(MessageBox, _('1. Click in \"Generate access token\" in your Tailscale web session.\n2. Enter your generated key in /etc/keys/tailscale_api.key'), MessageBox.TYPE_INFO, simple=True)
			return
		else:
			try:
				info = json.loads(self.get_devices().text)
				devices = info.get('devices')
				for device in devices:
					devicelist.append((device['hostname'], device['addresses'][0], device['clientVersion'].split('-')[0]))
				self.session.open(Tailscaleuser, devicelist)
			except:
				self.session.open(MessageBox, _('Could not get the list of devices on your network.\n\nTo display the devices in your Tailscale network you must:\n1. Delete if an old key exists in your Tailscale web session\n2. Click in \"Generate access token\" in your Tailscale web session\n3. Enter your generated key in /etc/keys/tailscale_api.key\n4. NOTE: If you still see this message after following these steps, delete the current API key from your token and generate a new one.'), MessageBox.TYPE_INFO, simple=True)

	def keyBlue(self):
		p = process.ProcessList()
		tailscale_process = str(p.named('tailscaled')).strip('[]')
		if tailscale_process:
			os.system('/etc/init.d/tailscale-daemon stop')
		else:
			os.system('/etc/init.d/tailscale-daemon start')
		self.UpdateTimer.start(5000, True)

	def get_devices(self):
		self.api_key = open('/etc/keys/tailscale_api.key','r').read().replace("\n","")
		self.base_url = 'https://api.tailscale.com/api/v2'
		self._auth = HTTPBasicAuth(self.api_key, '')
		self._headers = {
			'Accept':'application/json'
		}
		p = process.ProcessList()
		tailscale_process = str(p.named('tailscaled')).strip('[]')
		if tailscale_process:
			networks = json.loads(getData())
			self.tailnet = networks.get("CurrentTailnet")['Name']
			url = f'{self.base_url}/tailnet/{self.tailnet}/devices'
			response = requests.get(url, auth=self._auth)
			return response
		return ""

class Tailscaleuser(Screen):
	if screenWidth == 1920:
		skin = """
		<screen name="TailscaleUser" position="center,120" size="1230,780" title=" ">
			<widget name="picRed" pixmap="buttons/red_HD.png" position="60,707" size="210,60" alphatest="blend" transparent="1" />
			<widget name="lblRed" position="15,707" size="300,40" zPosition="1" font="RegularHD;20" halign="center" valign="center" transparent="1" />
			<widget source="list" render="Listbox" position="12,68" size="1200,630" scrollbarMode="showOnDemand" enableWrapAround="on">
				<convert type="TemplatedMultiContent">
					{ "template": [ MultiContentEntryText(pos=(135,2),size=(1080,45),font=0,text=2),
					MultiContentEntryText(pos=(135,42),size=(1080,66),font=1,text=1),
					MultiContentEntryText(pos=(135,72),size=(1080,66),font=1,text=3,color=0xa0a0a0),
					MultiContentEntryPixmapAlphaBlend(pos=(20,15),size=(112,112),png=4),
					MultiContentEntryPixmapAlphaBlend(pos=(0,0),size=(1200,3),png=5)],
					"fonts": [gFont("RegularHD",22),gFont("RegularHD",17)],
					"itemHeight": 112
					}
				</convert>
			</widget>
			<widget name="lblStatus" position="19,9" size="1100,51" font="RegularHD;20" zPosition="2" />
		</screen>"""
	else:
		skin = """
		<screen name="TailscaleUser" position="center,120" size="820,520" title=" ">
			<widget name="picRed" pixmap="buttons/red.png" position="40,471" size="140,40" alphatest="blend" transparent="1" />
			<widget name="lblRed" position="10,471" size="200,40" zPosition="1" font="RegularHD;20" halign="center" valign="center" transparent="1" />
			<widget source="list" render="Listbox" position="8,45" size="800,420" scrollbarMode="showOnDemand" enableWrapAround="on">
				<convert type="TemplatedMultiContent">
					{ "template": [ MultiContentEntryText(pos = (70,1),size = (720,30),font=0,text=2),
					MultiContentEntryText(pos = (70,28),size = (720,44),font=1,text=1),
					MultiContentEntryText(pos=(70,48),size=(720,44),font=1,text=3,color=0xa0a0a0),
					MultiContentEntryPixmapAlphaBlend(pos=(4,4),size=(60,60),png=4),
					MultiContentEntryPixmapAlphaBlend(pos = (0,0),size = (800,2),png=5)],
					"fonts": [gFont("Regular",22),gFont("Regular",17)],
					"itemHeight": 74
					}
				</convert>
			</widget>
			<widget name="lblStatus" position="12,6" size="733,34" font="Regular;20" zPosition="2" />
		</screen> """

	def __init__(self, session, lista):
		Screen.__init__(self, session)
		self.skinName = ['TailscaleUser']
		self.lista = lista

		self['actions'] = ActionMap(['SetupActions','ColorActions'],
		{
			'cancel': self.KeyExit,
			'red': self.KeyExit
		}, -2)

		self['list'] = List()

		self['lblStatus'] = Label()
		self['picRed'] = Pixmap()
		self['lblRed'] = Label(_("Close"))

		self.line = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Tailscale/images/div-h.png')
		if screenWidth == 1920:
			self.networkpic = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Tailscale/images/network-hd.png')
		else:
			self.networkpic = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/Tailscale/images/network.png')
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(_('Devices in your network'))
		self.UpdateStatus()

	def KeyExit(self):
		self.close()

	def UpdateStatus(self):
		self['lblStatus'].setText(_('Downloading data, please wait...'))
		self.memberlist()

	def memberlist(self):
		self['lblStatus'].setText(_('%d Entries') % len(self.lista))
		index = self['list'].getIndex()
		mlist = []
		for data in self.lista:
			pic = self.networkpic
			text0 = '%s: %s' % (_('Device'), data[0])
			text1 = '%s: %s' % (_('IP'), data[1])
			text2 = '%s: %s' % (_('Version'), data[2])
			mlist.append((data, str(text1), str(text0), str(text2),  pic, self.line))
		self['list'].setList(mlist)
		self['list'].setIndex(index)
		return
