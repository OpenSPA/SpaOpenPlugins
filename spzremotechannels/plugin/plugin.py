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
#from twisted.internet import reactor
#from twisted.internet.protocol import ClientCreator
#from twisted.protocols.ftp import FTPClient
#from urllib import quote
from EPGImport import EPGdownload, addBouquet, createBouquetFile

import xml.etree.ElementTree as ET
import urllib2, base64

#from FTPDownloader import FTPDownloader

from . import _
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd, fontHD


DIR_ENIGMA2 = '/etc/enigma2/'
DIR_TMP = '/tmp/'

config.plugins.RemoteStreamConverter = ConfigSubsection()
config.plugins.RemoteStreamConverter.address = ConfigText(default = "", fixed_size = False)
config.plugins.RemoteStreamConverter.ip = ConfigIP(default = [0,0,0,0])
config.plugins.RemoteStreamConverter.username = ConfigText(default = "root", fixed_size = False)
config.plugins.RemoteStreamConverter.password = ConfigText(default = "", fixed_size = False)
#config.plugins.RemoteStreamConverter.port = ConfigInteger(21, (0, 65535))
#config.plugins.RemoteStreamConverter.passive = ConfigYesNo(False)
#config.plugins.RemoteStreamConverter.telnetport = ConfigInteger(23, (0, 65535))
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
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="210,60" font="RegularHD;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_green" render="Label" position="210,0" zPosition="1" size="210,60" font="RegularHD;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="420,0" zPosition="1" size="210,60" font="RegularHD;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_blue" render="Label"  position="630,0" zPosition="1" size="210,60" font="RegularHD;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" font="RegularHD;20" position="15,75" size="825,487" scrollbarMode="showOnDemand" itemHeight="45" />
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
#		self.list.append(getConfigListEntry(_("FTPport:"), config.plugins.RemoteStreamConverter.port, False))
#		self.list.append(getConfigListEntry(_("Passive:"), config.plugins.RemoteStreamConverter.passive, False))
#		self.list.append(getConfigListEntry(_("Telnetport:"), config.plugins.RemoteStreamConverter.telnetport, False))
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
#		self.list.append(getConfigListEntry(_("FTPport:"), config.plugins.RemoteStreamConverter.port, False))
#		self.list.append(getConfigListEntry(_("Passive:"), config.plugins.RemoteStreamConverter.passive, False))
#		self.list.append(getConfigListEntry(_("Telnetport:"), config.plugins.RemoteStreamConverter.telnetport, False))
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
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="210,60" font="RegularHD;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="210,0" zPosition="1" size="210,60" font="RegularHD;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="420,0" zPosition="1" size="210,60" font="RegularHD;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render="Label" position="630,0" zPosition="1" size="210,60" font="RegularHD;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="list" position="7,75" size="810,540" itemHeight="45" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,615" zPosition="10" size="840,3" transparent="1" alphatest="on" />
			<widget source="statusbar" render="Label" position="7,630" zPosition="10" size="825,45" halign="center" valign="center" font="RegularHD;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
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
#			self["statusbar"].setText(_("Testing remote connection"))
#			timeout = 3000
#			self.currentLength = 0
#			self.total = 0
#			self.working = True
#			creator = ClientCreator(reactor, FTPClient, config.plugins.RemoteStreamConverter.username.value, config.plugins.RemoteStreamConverter.password.value, config.plugins.RemoteStreamConverter.passive.value)
#			creator.connectTCP(self.getRemoteAdress(), config.plugins.RemoteStreamConverter.port.value, timeout).addCallback(self.controlConnectionMade).addErrback(self.connectionFailed)

#	def controlConnectionMade(self, ftpclient):
#		self["statusbar"].setText(_("Connection to remote IP ok"))
#		ftpclient.quit()
#		self.fetchRemoteBouqets()

#	def connectionFailed(self, *args):
#		self.working = False
#		self["statusbar"].setText(_("Could not connect to remote IP"))

	def fetchRemoteBouqets(self):
		self["statusbar"].setText(_("Downloading remote services"))
		self.readIndex = 0
		self.workList = []
		self.workList.append('bouquets.tv')
		self.workList.append('bouquets.radio')
#		self.download(self.workList[0]).addCallback(self.fetchRemoteBouqetsFinished).addErrback(self.fetchRemoteBouqetsFailed)
		listindex = 0
		ip = self.getRemoteAdress()
		if config.plugins.RemoteStreamConverter.HTTPport.value != 80:
			ip = ip + ":" + str(config.plugins.RemoteStreamConverter.HTTPport.value)
		url = 'http://%s/web/bouquets' % ip 
		html = None
		if config.plugins.RemoteStreamConverter.httpauthentication.value:
			request = urllib2.Request(url)
			b64auth = base64.standard_b64encode("%s:%s" % (config.plugins.RemoteStreamConverter.username.value,config.plugins.RemoteStreamConverter.password.value))
			request.add_header("Authorization", "Basic %s" % b64auth)
		else:
			request = url
		try:
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
						service = child.text.encode("utf-8").split('"')
						if len(service)>1:
							filename = service[1]
					if child.tag == "e2servicename":
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
					
#	def fetchRemoteBouqetsFailed(self, string):
#		self.working = False
#		self["statusbar"].setText(_("Download from remote failed"))

#	def fetchRemoteBouqetsFinished(self, string):
#		self.readIndex += 1
#		if self.readIndex < len(self.workList):
#			self.download(self.workList[self.readIndex]).addCallback(self.fetchRemoteBouqetsFinished).addErrback(self.fetchRemoteBouqetsFailed)
#		else:
#			self.parseBouqets()

#	def parserWork(self, list, name):
#		try:
#			lines = open(name).readlines()
#			for line in lines:
#				tmp = line.split('userbouquet.')
#				if len(tmp) > 1:
#					if '\"' in line:
#						tmp2 = tmp[1].split('\"')
#					else:
#						tmp2 = tmp[1].split('\n')
#					list.append(tmp2[0])
#		except:
#			pass

#	def parseBouqets(self):
#		list = []
#		self.parserWork(list, DIR_TMP + 'bouquets.tv')
#		self.parserWork(list, DIR_TMP + 'bouquets.radio')
#		self.readIndex = 0
#		self.workList = []
#		for listindex in range(len(list)):
#			self.workList.append('userbouquet.' + list[listindex])
#		self.workList.append('lamedb')
#		self.download(self.workList[0]).addCallback(self.fetchUserBouquetsFinished).addErrback(self.fetchUserBouquetsFailed)

#	def fetchUserBouquetsFailed(self, string):
#		if self.readIndex < len(self.workList) and self.readIndex > 0:
#			self.workList.remove(self.workList[self.readIndex])
#			self.readIndex -= 1
#			self.fetchUserBouquetsFinished('')
#		self.working = False
#		self["statusbar"].setText(_("Download from remote failed"))

#	def fetchUserBouquetsFinished(self, string):
#		self.readIndex += 1
#		if self.readIndex < len(self.workList):
#			self["statusbar"].setText(_("FTP reading file %d of %d") % (self.readIndex, len(self.workList)-1))
#			self.download(self.workList[self.readIndex]).addCallback(self.fetchUserBouquetsFinished).addErrback(self.fetchUserBouquetsFailed)
#		else:
#			if len(self.workList) > 0:
#				self["statusbar"].setText(_("Make your selection"))
#				for listindex in range(len(self.workList) - 1):
#					name = self.readBouquetName(DIR_TMP + self.workList[listindex])
#					self.list.addSelection(name, self.workList[listindex], listindex, False)
##				self.removeFiles(DIR_TMP, "bouquets.")
#				self.working = False
#				self.hasFiles = True
#				self["key_green"].setText(_("Download"))
#				self["key_blue"].setText(_("Invert"))
#				self["key_yellow"].setText("")

#	def download(self, file, contextFactory = None, *args, **kwargs):
#		client = FTPDownloader(
#			self.getRemoteAdress(),
#			config.plugins.RemoteStreamConverter.port.value,
#			DIR_ENIGMA2 + file,
#			DIR_TMP + file,
#			config.plugins.RemoteStreamConverter.username.value,
#			config.plugins.RemoteStreamConverter.password.value,
#			*args,
#			**kwargs
#		)
#		return client.deferred

#	def convertBouquets(self):
#		self.readIndex = 0
#		while True:
#			if 'lamedb' not in self.workList[self.readIndex]:
#				filename = DIR_TMP + self.workList[self.readIndex]
#				#hasRemoteTag = False
#				self.workList[self.readIndex] = self.workList[self.readIndex].replace('userbouquet.', 'userbouquet.remote_')
#				if self.checkBouquetAllreadyInList(self.workList[self.readIndex], self.workList[self.readIndex]) is True:
#					self.workList[self.readIndex] = self.workList[self.readIndex].replace('userbouquet.remote_', 'userbouquet.remote2_')
					#hasRemoteTag = True

#				name = self.readBouquetName(filename)
#				fp = open(DIR_ENIGMA2 + self.workList[self.readIndex], 'w')
#				try:
#					lines = open(filename).readlines()
#					was_html = False
#					for line in lines:
#						if was_html and '#DESCRIPTION' in line:
#							was_html = False
#							continue
#						if '#NAME' in line:  #and hasRemoteTag:
#							if '\r' in line:
#								name_orig = line.replace('\r\n','')
#							else:
#								name_orig = line.replace('\n','')
#							line = "%s#SERVICE 1:576:0:0:0:0:0:0:0:0::%s|%d|%s|%s|%d\n#DESCRIPTION marker for Remote Bouquet\n" % (line.replace(name_orig, '#NAME remote_' + name), self.getRemoteAdress(), config.plugins.RemoteStreamConverter.HTTPport.value, config.plugins.RemoteStreamConverter.username.value, config.plugins.RemoteStreamConverter.password.value,config.plugins.RemoteStreamConverter.httpauthentication.value)
#						was_html = False
#						if 'http' in line:
#							was_html = True
#							continue
#						elif '#SERVICE' in line and not "#NAME" in line and line.split(":")[1] != "832" and line.split(":")[1] != "64":
#							line = line.strip('\r\n')
#							line = line.strip('\n')
#							tmp = line.split('#SERVICE')
#							if '::' in tmp[1]:
#								desc = tmp[1].split("::")
#								if (len(desc)) == 2:
#									tmp2 = tmp[1].split('::')
#									service_ref = ServiceReference(tmp2[0] + ':')
#									tag = tmp2[0][1:]
#							else:
#								tag = tmp[1][1:-1]
#								n=tmp[1].find(':')
#								if n>-1:
#									tag2 = config.plugins.RemoteStreamConverter.servicestype.value+tmp[1][n:-1]
#								else:
#									tag2 = tmp[1][1:-1]
#								aut = ""
#								if config.plugins.RemoteStreamConverter.Streamauthentication.value:
#									aut = config.plugins.RemoteStreamConverter.username.value + ':' + config.plugins.RemoteStreamConverter.password.value + '@'

#								service_ref = ServiceReference(tag)
								#open("/etc/enigma2/remotechannels","a").write(self.getRemoteAdress()+"|"+tag+"|"+service_ref.getServiceName()+"\n")
#							out = '#SERVICE ' + tag2 + ':' + quote('http://' + aut + self.getRemoteAdress() + ':' + str(config.plugins.RemoteStreamConverter.Streamport.value) + '/' + tag) + ':' + service_ref.getServiceName() + '\n'
#						else:
#							out = line
#						fp.write(out)
#				except:
#					pass
#				fp.close()
#			self.readIndex += 1
#			if self.readIndex == len(self.workList):
#				break
#		self.removeFiles(DIR_TMP, "userbouquet.")
#		self.removeFiles(DIR_TMP, "bouquets.")


#	def getTransponders(self, fp):
#		step = 0
#		lines = open(DIR_TMP + 'lamedb').readlines()
#		for line in lines:
#			if step == 0:
#				if 'transponders' in line:
#					step =1
#			elif step == 1:
#				if 'end' in line[:3]:
#					fp.write(line)
#					break
#				else:
#					fp.write(line)

#	def getServices(self, fp):
#		step = 0
#		lines = open(DIR_TMP + 'lamedb').readlines()
#		for line in lines:
#			if step == 0:
#				if 'services' in line[:8]:
#					step =1
#			elif step == 1:
#				if 'end' in line[:3]:
#					fp.write(line)
#					break
#				else:
#					fp.write(line)

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

#	def createBouquetFile(self, target, source, matchstr, typestr):
#		tmpFile = []
#		fp = open(target, 'w')
#		try:
#			lines = open(source).readlines()
#			for line in lines:
#				tmpFile.append(line)
#				fp.write(line)
#			for item in self.workList:
#				if typestr in item:
#					item = item.replace('userbouquet.', 'userbouquet.remote_')
#					if self.checkBouquetAllreadyInList(typestr, item) is True:
#						item = item.replace('userbouquet.', 'userbouquet.remote2_')
#					tmp = matchstr + item + '\" ORDER BY bouquet\n'
#					match = False
#					for x in tmpFile:
#						if tmp in x:
#							match = True
#					if match is not True:
#						fp.write(tmp)
#			fp.close()
#			self.copyFile(target, source)
#		except:
#			pass

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


#		fileValid = False
#		state = 0
#		fp = open(DIR_TMP + 'tmp_lamedb', 'w')
#		try:
#			lines = open(DIR_ENIGMA2 + 'lamedb').readlines()
#			for line in lines:
#				if 'eDVB services' in line:
#					fileValid = True
#				if state == 0:
#					if 'transponders' in line[:12]:
#						fp.write(line)
#					elif 'end' in line[:3]:
#						self.getTransponders(fp)
#						state = 1
#					else:
#						fp.write(line)
#				elif state == 1:
#					if 'services' in line[:8]:
#						fp.write(line)
#					elif 'end' in line[:3]:
#						self.getServices(fp)
#						state = 2
#					else:
#						fp.write(line)
#				elif state == 2:
#					fp.write(line)
#		except:
#			pass
#		fp.close()
#		if fileValid is not True:
#			self.copyFile(DIR_TMP + 'lamedb', DIR_TMP + 'tmp_lamedb')
#		tv = False
#		radio = False
#		for item in self.workList:
#			if '.tv' in item:
#				tv = True
#			if '.radio' in item:
#				radio = True
#		if radio or tv:
#			if tv:
#				self.createBouquetFile(DIR_TMP + 'tmp_bouquets.tv', DIR_ENIGMA2 + 'bouquets.tv', '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"', '.tv')
#			if radio:
#				self.createBouquetFile(DIR_TMP + 'tmp_bouquets.radio', DIR_ENIGMA2 + 'bouquets.radio', '#SERVICE 1:7:2:0:0:0:0:0:0:0:FROM BOUQUET \"', '.radio')
#			self.copyFile(DIR_TMP + 'tmp_lamedb', DIR_ENIGMA2 + 'lamedb')
#			db = eDVBDB.getInstance()
#			db.reloadServicelist()
#			self.convertBouquets()
#			self.removeFiles(DIR_TMP, "tmp_")
#			self.removeFiles(DIR_TMP, "lamedb")
#			db = eDVBDB.getInstance()
#			db.reloadServicelist()
#			db.reloadBouquets()
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

#	def removeFiles(self, targetdir, target):
#		import os
#		targetLen = len(target)
#		for root, dirs, files in os.walk(targetdir):
#			for name in files:
#				if target in name[:targetLen]:
#					os.remove(os.path.join(root, name))

#	def copyFile(self, source, dest):
#		import shutil
#		shutil.copy2(source, dest)


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
