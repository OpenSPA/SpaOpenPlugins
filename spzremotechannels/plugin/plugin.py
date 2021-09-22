from . import _, esHD, fhd, fontHD, py3
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.SelectionList import SelectionList
from Components.ActionMap import ActionMap
from Components.config import config, configfile, ConfigInteger, ConfigSubsection, ConfigText, ConfigYesNo, getConfigListEntry, ConfigIP, ConfigSelection
from enigma import eServiceCenter, eServiceReference, eDVBDB, eEPGCache, eTimer
from ServiceReference import ServiceReference
from Screens.MessageBox import MessageBox
from .EPGImport import EPGdownload, addBouquet, createBouquetFile

import xml.etree.ElementTree as ET
if py3():
	import urllib.request, urllib.error, urllib.parse, base64
else:
	import urllib2, base64


DIR_ENIGMA2 = '/etc/enigma2/'
DIR_TMP = '/tmp/'

config.plugins.RemoteStreamConverter = ConfigSubsection()
config.plugins.RemoteStreamConverter.address = ConfigText(default = "", fixed_size = False)
config.plugins.RemoteStreamConverter.ip = ConfigIP(default = [0,0,0,0])
config.plugins.RemoteStreamConverter.username = ConfigText(default = "root", fixed_size = False)
config.plugins.RemoteStreamConverter.password = ConfigText(default = "", fixed_size = False)
config.plugins.RemoteStreamConverter.HTTPport = ConfigInteger(80, (0, 65535))
config.plugins.RemoteStreamConverter.Streamport = ConfigInteger(8001, (0, 65535))
config.plugins.RemoteStreamConverter.Streamauthentication = ConfigYesNo(False)
config.plugins.RemoteStreamConverter.httpauthentication = ConfigYesNo(False)
config.plugins.RemoteStreamConverter.servicestype = ConfigSelection(choices = {"1": "DVB", "4097": "IPTV"}, default = "1")

class ServerEditor(ConfigListScreen, Screen):
	if esHD():
		skin = """
		<screen position="center,center" size="840,495" title="FTP Server Editor">
			<ePixmap pixmap="skin_default/buttons/red_HD.png" position="0,0" size="210,60" transparent="1" alphatest="blend" />
			<ePixmap pixmap="skin_default/buttons/green_HD.png" position="210,0" size="210,60" transparent="1" alphatest="blend" />
			<ePixmap pixmap="skin_default/buttons/yellow_HD.png" position="420,0" size="210,60" transparent="1" alphatest="blend" />
			<ePixmap pixmap="skin_default/buttons/blue_HD.png" position="630,0" size="210,60" transparent="1" alphatest="blend" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_green" render="Label" position="210,0" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="420,0" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_blue" render="Label"  position="630,0" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" font="Regular;30" position="15,75" size="825,487" scrollbarMode="showOnDemand" itemHeight="45" />
		</screen>"""
	else:
		skin = """
		<screen position="center,center" size="560,330" title="FTP Server Editor">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" transparent="1" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_blue" render="Label"  position="420,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="10,50" size="550,325" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("OK"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText("")
		self.isIp = True
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		if config.plugins.RemoteStreamConverter.address.value != '':
			self.createMenuAdress()
		else:
			self.createMenuIp()
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
			{
				"up": self.keyUp,
				"down": self.keyDown,
				"ok": self.keySave,
				"save": self.keySave,
				"cancel": self.keyCancel,
				"blue": self.enterUrl,
				"yellow": self.switchMode
			}, -2)
		self.setTitle(_("FTP Server Editor"))

	def keyUp(self):
		if self["config"].getCurrentIndex() > 0:
			self["config"].setCurrentIndex(self["config"].getCurrentIndex() - 1)
			self.setVkeyOnOff()

	def keyDown(self):
		if self["config"].getCurrentIndex() < len(self.list) - 1:
			self["config"].setCurrentIndex(self["config"].getCurrentIndex() + 1)
			self.setVkeyOnOff()

	def switchMode(self):
		if self["config"].getCurrentIndex() != 0:
			return
		config.plugins.RemoteStreamConverter.ip.value = [0, 0, 0, 0]
		config.plugins.RemoteStreamConverter.address.value = ""
		if self.isIp:
			self.createMenuAdress()
		else:
			self.createMenuIp()

	def setVkeyOnOff(self):
		if self.list[self["config"].getCurrentIndex()][2]:
			self["key_blue"].setText(_("Keyboard"))
		else:
			self["key_blue"].setText("")

		if self["config"].getCurrentIndex() == 0:
			if self.isIp:
				self["key_yellow"].setText(_("Use address"))
			else:
				self["key_yellow"].setText(_("Use IP"))
		else:
			self["key_yellow"].setText("")

	def createMenuIp(self):
		self.list = []
		self.list.append(getConfigListEntry(_("IP:"), config.plugins.RemoteStreamConverter.ip, False))
		self.list.append(getConfigListEntry(_("Username:"), config.plugins.RemoteStreamConverter.username, True))
		self.list.append(getConfigListEntry(_("Password:"), config.plugins.RemoteStreamConverter.password, True))
		self.list.append(getConfigListEntry(_("HTTPport:"), config.plugins.RemoteStreamConverter.HTTPport, False))
		self.list.append(getConfigListEntry(_("HTTP Authentication:"), config.plugins.RemoteStreamConverter.httpauthentication, False))
		self.list.append(getConfigListEntry(_("Streamport:"), config.plugins.RemoteStreamConverter.Streamport, False))
		self.list.append(getConfigListEntry(_("Stream Authentication:"), config.plugins.RemoteStreamConverter.Streamauthentication, False))
		self.list.append(getConfigListEntry(_("Register Channel as:"), config.plugins.RemoteStreamConverter.servicestype, False))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self.isIp = True
		self.setVkeyOnOff()

	def createMenuAdress(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Adress:"), config.plugins.RemoteStreamConverter.address, True))
		self.list.append(getConfigListEntry(_("Username:"), config.plugins.RemoteStreamConverter.username, True))
		self.list.append(getConfigListEntry(_("Password:"), config.plugins.RemoteStreamConverter.password, True))
		self.list.append(getConfigListEntry(_("HTTPport:"), config.plugins.RemoteStreamConverter.HTTPport, False))
		self.list.append(getConfigListEntry(_("HTTP Authentication:"), config.plugins.RemoteStreamConverter.httpauthentication, False))
		self.list.append(getConfigListEntry(_("Streamport:"), config.plugins.RemoteStreamConverter.Streamport, False))
		self.list.append(getConfigListEntry(_("Stream Authentication:"), config.plugins.RemoteStreamConverter.Streamauthentication, False))
		self.list.append(getConfigListEntry(_("Register Channel as:"), config.plugins.RemoteStreamConverter.servicestype, False))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self.isIp = False
		self.setVkeyOnOff()

	POS_ADDRESS = 0
	POS_USERNAME = 1
	POS_PASSWORD = 2

	def enterUrl(self):
		if not self.list[self["config"].getCurrentIndex()][2]:
			return
		if self["config"].getCurrentIndex() == self.POS_ADDRESS and not self.isIp:
			txt = config.plugins.RemoteStreamConverter.address.value
			head = _("Enter address")
		elif self["config"].getCurrentIndex() == self.POS_USERNAME:
			txt = config.plugins.RemoteStreamConverter.username.value
			head = _("Enter username")
		elif self["config"].getCurrentIndex() == self.POS_PASSWORD:
			txt = config.plugins.RemoteStreamConverter.password.value
			head = _("Enter password")
		self.session.openWithCallback(self.urlCallback, VirtualKeyBoard, title = head, text = txt)

	def urlCallback(self, res):
		if res is not None:
			if self["config"].getCurrentIndex() == self.POS_ADDRESS:
				config.plugins.RemoteStreamConverter.address.value = res
			elif self["config"].getCurrentIndex() == self.POS_USERNAME:
				config.plugins.RemoteStreamConverter.username.value = res
			elif self["config"].getCurrentIndex() == self.POS_PASSWORD:
				config.plugins.RemoteStreamConverter.password.value = res

	def keySave(self):
		config.plugins.RemoteStreamConverter.address.value = config.plugins.RemoteStreamConverter.address.value.strip()
		self.saveAll()
		if self.isIp:
			config.plugins.RemoteStreamConverter.address.save()
		else:
			config.plugins.RemoteStreamConverter.ip.save()
		configfile.save()
		self.close(True)

class StreamingChannelFromServerScreen(Screen):
	if esHD():
		skin = """
		<screen name="StreamingChannelFromServerScreen" position="center,center" size="825,675" title="Select bouquets to convert" >
			<ePixmap pixmap="skin_default/buttons/red_HD.png" position="0,0" size="210,60" alphatest="blend" />
			<ePixmap pixmap="skin_default/buttons/green_HD.png" position="210,0" size="210,60" alphatest="blend" />
			<ePixmap pixmap="skin_default/buttons/yellow_HD.png" position="420,0" size="210,60" alphatest="blend" />
			<ePixmap pixmap="skin_default/buttons/blue_HD.png" position="630,0" size="210,60" alphatest="blend" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="210,60" font="Regular;30" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="210,0" zPosition="1" size="210,60" font="Regular;30" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="420,0" zPosition="1" size="210,60" font="Regular;30" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render="Label" position="630,0" zPosition="1" size="210,60" font="Regular;30" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="list" position="7,75" size="810,540" itemHeight="45" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,615" zPosition="10" size="840,3" transparent="1" alphatest="on" />
			<widget source="statusbar" render="Label" position="7,630" zPosition="10" size="825,45" halign="center" valign="center" font="Regular;33" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		</screen>"""
	else:
		skin = """
		<screen name="StreamingChannelFromServerScreen" position="center,center" size="550,450" title="Select bouquets to convert" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="list" position="5,50" size="540,360" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,410" zPosition="10" size="560,2" transparent="1" alphatest="on" />
			<widget source="statusbar" render="Label" position="5,420" zPosition="10" size="550,30" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.workList = []
		self.readIndex = 0
		self.working = False
		self.hasFiles = False
		self.list = SelectionList()
		self["list"] = self.list
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText("")
		self["key_yellow"] = StaticText(_("Set server IP"))
		self["key_blue"] = StaticText("")
		self["statusbar"] = StaticText(_("Select a remote server IP first"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.keyOk,
			"cancel": self.close,
			"red": self.close,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue
		}, -1)
		self.setTitle(_("Select bouquets to convert"))

	def keyOk(self):
		if self.working:
			return
		if self.readIndex > 0:
			self.list.toggleSelection()

	def keyBlue(self):
		if not self.hasFiles or self.working:
			return
		if self.readIndex > 0:
			try:
				self.list.toggleAllSelection()
			except AttributeError:
				self.list.toggleSelection()

	def keyYellow(self):
		if not self.hasFiles:
			self.session.openWithCallback(self.setRemoteIpCallback, ServerEditor)

	def setRemoteIpCallback(self, ret = False):
		if ret:
			self.fetchRemoteBouqets()

	def fetchRemoteBouqets(self):
		self["statusbar"].setText(_("Downloading remote services"))
		self.readIndex = 0
		self.workList = []
		self.workList.append('bouquets.tv')
		self.workList.append('bouquets.radio')
		listindex = 0
		ip = self.getRemoteAdress()
		if config.plugins.RemoteStreamConverter.HTTPport.value != 80:
			ip = ip + ":" + str(config.plugins.RemoteStreamConverter.HTTPport.value)
		url = 'http://%s/web/bouquets' % ip 
		html = None
		if config.plugins.RemoteStreamConverter.httpauthentication.value:
			if py3():
				request = urllib.request.Request(url)
			else:
				request = urllib2.Request(url)

			data = "%s:%s" % (config.plugins.RemoteStreamConverter.username.value,config.plugins.RemoteStreamConverter.password.value)
			if py3():
				b64auth = base64.standard_b64encode(data.encode('ascii'))
				request.add_header("Authorization", "Basic " + b64auth.decode('ascii'))
			else:
				b64auth = base64.standard_b64encode(data)
				request.add_header("Authorization", "Basic %s" % b64auth)
		else:
			request = url
		try:
			if py3():
				html = urllib.request.urlopen(request).read()
			else:
				html = urllib2.urlopen(request).read()
		except:
			html = None
			self.session.open(MessageBox, _('It is not possible to connect to the indicated address'), type=MessageBox.TYPE_ERROR, timeout=10)
		bouquets = []
	
		if html:
			try:
				bouquets = ET.fromstring(html)
			except:
				bouquets = []
		if len(bouquets) > 0:
			filename = name = None
			for bouquet in bouquets:
				for child in bouquet:
					if child.tag == "e2servicereference":
						if py3():
							service = child.text.split('"')
						else:
							service = child.text.encode("utf-8").split('"')
						if len(service)>1:
							filename = service[1]
					if child.tag == "e2servicename":
						if py3():
							name = child.text
						else:
							name = child.text.encode("utf-8")
				if filename and name:
					self.readIndex += 1
					self.list.addSelection(name, filename, listindex, False)
					listindex += 1

		if listindex>0:
			self.working = False
			self.hasFiles = True
			self["key_green"].setText(_("Download"))
			self["key_blue"].setText(_("Invert"))
			self["key_yellow"].setText("")
					
	def checkBouquetAllreadyInList(self, typestr, item):
		item = item.replace('userbouquet.', '')
		list = []
		if '.tv' in typestr:
			self.readBouquetList(list, '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet')
		else:
			self.readBouquetList(list, '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet')
		if len(list) > 0:
			for x in list:
				if item in x:
					return True
		return False

	def keyGreen(self):
		if not self.hasFiles:
			return
		self.workList = []
		tmpList = []
		tmpList = self.list.getSelectionsList()
		if len(tmpList) == 0:
			self["statusbar"].setText(_("No bouquets selected"))
			return
		ip = self.getRemoteAdress()
		port = int(config.plugins.RemoteStreamConverter.HTTPport.value)
		user = config.plugins.RemoteStreamConverter.username.value
		password = config.plugins.RemoteStreamConverter.password.value
		auth = int(config.plugins.RemoteStreamConverter.httpauthentication.value)
		stype = config.plugins.RemoteStreamConverter.servicestype.value
		streamport = int(config.plugins.RemoteStreamConverter.Streamport.value)
		streamaut = int(config.plugins.RemoteStreamConverter.Streamauthentication.value)
		data = ""
		for item in tmpList:
#			self.workList.append(item[1])
			name = "remote_" + item[0]
			bouquet = item[1].replace("userbouquet.","userbouquet.remote_")

			line = "%s|%d|%s|%s|%d|%s|%d|%d" % (ip,port,user,password,auth,stype,streamport,streamaut)

			if not self.checkBouquetAllreadyInList(bouquet,".tv"):
				addBouquet(bouquet, name)

			createBouquetFile(bouquet, name, line, [])

		db = eDVBDB.getInstance()
		db.reloadServicelist()
		db.reloadBouquets()


		self.close()

	def getRemoteAdress(self):
		if config.plugins.RemoteStreamConverter.address.value != "":
			return config.plugins.RemoteStreamConverter.address.value
		else:
			return '%d.%d.%d.%d' % (config.plugins.RemoteStreamConverter.ip.value[0], config.plugins.RemoteStreamConverter.ip.value[1], config.plugins.RemoteStreamConverter.ip.value[2], config.plugins.RemoteStreamConverter.ip.value[3])

	def readBouquetName(self, filename):
		bouquetname = ""
		try:
			if "tv" in filename:
				lines = open(DIR_TMP + "bouquets.tv").readlines()
			else:
				lines = open(DIR_TMP + "bouquets.radio").readlines()
			for line in lines:
				data = line.split('\"')
				if len(data) == 3:
					name = data[1]
					if name in filename:
						data = line.split(':')
						if len(data) == 12:
							bouquetname = data[-1]
							if '\r' in bouquetname:
								bouquetname = bouquetname.split('\r\n')[0]
							else:
								bouquetname = bouquetname.split('\n')[0]
							return bouquetname
		except:
			pass

		if bouquetname == "":
			try:
				lines = open(filename).readlines()
				for line in lines:
					if '#NAME' in line:
						tmp = line.split('#NAME ')
						if '\r' in tmp[1]:
							bouquetname = tmp[1].split('\r\n')[0]
						else:
							bouquetname = tmp[1].split('\n')[0]
						return bouquetname
			except:
				pass
		return ""

	def readBouquetList(self, list, rootstr):
		bouquet_root = eServiceReference(rootstr)
		if not bouquet_root is None:
			serviceHandler = eServiceCenter.getInstance()
			if not serviceHandler is None:
				servicelist = serviceHandler.list(bouquet_root)
				if not servicelist is None:
					while True:
						service = servicelist.getNext()
						if not service.valid():
							break
						tmp = service.toString().split('userbouquet.')
						if len(tmp[1]) > 0:
							tmp2 = tmp[1].split('\"')
							name = self.readBouquetName(DIR_ENIGMA2 + 'userbouquet.' + tmp2[0])
							list.append((name, tmp2[0]))


def Download_EPG(session, **kwargs):
	session.open(EPGdownload)


def main(session, **kwargs):
	session.open(StreamingChannelFromServerScreen)

def mainInMenu(menuid, **kwargs):
	if menuid == "scan":
		return [(_("Append Remote channels streams"), main, "streamconvert", 99)]
	else:
		return []

def Plugins(**kwargs):
	return [ PluginDescriptor(name = _("Append Remote channels streams"), description = _("Convert remote channel list for streaming"), where = PluginDescriptor.WHERE_MENU, fnc = mainInMenu),
PluginDescriptor(name=_("Download EPG from Remote Channels"), description=_("Download EPG from Remote Channels"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=Download_EPG) ]
