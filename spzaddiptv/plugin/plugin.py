from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.ServiceList import ServiceList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Screens.VirtualKeyBoard import VirtualKeyBoard
from urllib.parse import quote
from enigma import eDVBDB, eServiceReference, eServiceCenter, eListboxPythonMultiContent, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO, RT_HALIGN_RIGHT,RT_HALIGN_LEFT,RT_HALIGN_CENTER
from Screens.ChannelSelection import ChannelSelectionEdit, ChannelSelectionBase
from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from ServiceReference import ServiceReference

from Components.Language import language
from os import environ
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext

from Plugins.Extensions.spazeMenu.plugin import esHD, fhd, fontHD

service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
FILE_M3U = '/etc/streams.m3u'

if esHD():
	skin = """
	<screen position="340,150" size="975,715" title="">
		<widget name="menu" font="RegularHD;19" position="15,7" size="945,525" scrollbarMode="showOnDemand" />
		<widget source="statusbar" render="Label" position="15,550" zPosition="10" size="945,75" halign="center" valign="center" font="RegularHD;18" foregroundColor="#666666" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdredcor.png" position="15,617" size="225,60" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreencor.png" position="255,617" size="225,60" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdyellowcor.png" position="495,617" size="225,60" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdbluecor.png" position="735,617" size="225,60" alphatest="blend" />
		<widget source="key_red" render="Label" position="15,617" zPosition="1" size="225,87" font="RegularHD;20" halign="center" valign="center" transparent="1" />
		<widget source="key_green" render="Label" position="255,617" zPosition="1" size="225,87" font="RegularHD;20" halign="center" valign="center" transparent="1" />
		<widget source="key_yellow" render="Label" position="495,617" zPosition="1" size="225,87" font="RegularHD;20" halign="center" valign="center" transparent="1" />
		<widget source="key_blue" render="Label" position="735,617" zPosition="1" size="225,87" font="RegularHD;20" halign="center" valign="center" transparent="1" />
		</screen>"""
else:
	skin = """
	<screen position="340,150" size="650,440" title="">
		<widget name="menu" position="10,5" size="630,330" scrollbarMode="showOnDemand" />
		<widget source="statusbar" render="Label" position="10,340" zPosition="10" size="630,50" halign="center" valign="center" font="Regular;18" foregroundColor="#666666" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/spzAddIPTV/images/redcor.png" position="10,385" size="150,40" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/spzAddIPTV/images/greencor.png" position="170,385" size="150,40" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/spzAddIPTV/images/yellowcor.png" position="330,385" size="150,40" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/spzAddIPTV/images/bluecor.png" position="490,385" size="150,40" alphatest="on" />
		<widget source="key_red" render="Label" position="10,385" zPosition="1" size="150,45" font="Regular;20" halign="center" valign="center" transparent="1" />
		<widget source="key_green" render="Label" position="170,385" zPosition="1" size="150,45" font="Regular;20" halign="center" valign="center" transparent="1" />
		<widget source="key_yellow" render="Label" position="330,385" zPosition="1" size="150,45" font="Regular;20" halign="center" valign="center" transparent="1" />
		<widget source="key_blue" render="Label" position="490,385" zPosition="1" size="150,45" font="Regular;20" halign="center" valign="center" transparent="1" />
	</screen>"""


##############################################

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("spzAddIPTV", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "SystemPlugins/spzAddIPTV/locale/"))

def _(txt):
	t = gettext.dgettext("spzAddIPTV", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#############



def getBouquetServices(bouquet):
	services = []
	Servicelist = eServiceCenter.getInstance().list(bouquet)
	serviceHandler=eServiceCenter.getInstance()
	n = -1
	if Servicelist is not None:
		while True:
			service = Servicelist.getNext()
			if not service.valid():
				break
			n += 1
			if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker):
				continue
			info = serviceHandler.info(service)
			name = info.getName(service).replace('\xc2\x86', '').replace('\xc2\x87', '')
			services.append((name,service,n))
	return services


def m3ulistentry (name, url, select=False, append=False):
	res = [name]
	if append:
		png = LoadPixmap("/usr/lib/enigma2/python/Plugins/SystemPlugins/spzAddIPTV/images/tvn.png")
		color = 0x666666
	else:
		if select:
			png = LoadPixmap("/usr/lib/enigma2/python/Plugins/SystemPlugins/spzAddIPTV/images/vtv.png")
			color = 0xbab329
		else:
			png = LoadPixmap("/usr/lib/enigma2/python/Plugins/SystemPlugins/spzAddIPTV/images/tv.png")
			color = 0xffffff
	res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(5), fhd(3)), size=(fhd(20), fhd(20)), png = png, flags = BT_SCALE | BT_KEEP_ASPECT_RATIO))
	#res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 5, 3, 20, 20, png))
	res.append(MultiContentEntryText(pos=(fhd(30,1.6), 0), size=(fhd(600), fhd(30)), font=0, text=name, color=color))
	res.append(MultiContentEntryText(pos=(fhd(30,1.6), fhd(22)), size=(fhd(600), fhd(30)), font=1, text=url, color=0x666666))
	return res

class m3uList(MenuList):
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setItemHeight(fhd(50))
		self.l.setFont(0, gFont(fontHD("Regular"), 20))
		self.l.setFont(1, gFont(fontHD("Regular"), 18))


class liveStreamingFromFile(Screen):

	def __init__(self, session, bouquet):
		self.skin = skin
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Change All Selections"))
		self["key_yellow"] = StaticText(_("View"))
		self["key_blue"] = StaticText(_("Add Selected"))
		#self["Title"] = Label()
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "MediaPlayerActions"],
		{
			"ok": self.keyOk,
			"cancel": self.keyCancel,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.append,
			"red": self.keyCancel,
			"stop" : self.keyCancel,
			"play" : self.keyYellow,
		}, -2)

		self.cur = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.bouquet = bouquet

		self["statusbar"] = StaticText(_("Select streams to add in bouquet")+" "+self.bouquet[0])

		self.list= []
		self["menu"] = m3uList([])
		self.mutableList = None
		self.servicelist = ServiceList(None)
		self.playing = False

		self.m3u = []

		self.services = getBouquetServices(self.bouquet[1])

		self.onLayoutFinish.append(self.createTopMenu)

	def updateLista(self):
		self.list=[]
		for x in self.m3u:
			self.list.append(m3ulistentry(x[0],x[1],x[2],x[3]))
		self["menu"].setList(self.list)		



	def createTopMenu(self):
		#self["Title"].setText(_("Add stream from ")+FILE_M3U)
		self.setTitle(_("Add stream from ")+FILE_M3U)
		self.readm3u()

	def readm3u(self):
		self.list= []
		tmpList = []

		if fileExists(FILE_M3U):
			tmpList = self.readFile(FILE_M3U)
			name = ""
			if tmpList != '':
				for x in tmpList:
					'''
					#EXTINF:0,Aljazera Sporte +10
http://2m4u.com/index2.php?q=aHR0cDovLzE3My4xOTMuNDguMTM3OjkwMDAvSlNDMTA%2FaWQ9MDA6MUQ6OTI6RjE6NUE6NkEmaXA9MTc2LjMxLjI1MS44NiZhdXRoPTU3YzRiZmVhNWE2MjgwNWE0ZGY5NzU0YzJmMWExM2Yy&hl=2ed 
					#EXTINF:0, MATV
rtmp://$OPT:rtmp-raw=rtmp://202.1.2.52:80/live/ pageUrl=http://livetvstreaming.ucoz.com live=1 playpath=BoyaboLive 
					'''
					if name != "":
						url = x.replace("\n","").replace(chr(13),"")
						if "rtmp-raw=" in url:
							url = url.split("rtmp-raw=")[1]
						if url !="":
							str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(url), quote(name))
							nser = ServiceReference(eServiceReference(str))
							yaesta = False
							for ch in self.services:
								nservice = ServiceReference(ch[1])
								ref = nservice.ref.toString()
								if ref.split(":")[10] == nser.ref.toString().split(":")[10]: 
									yaesta = True
									continue
							self.m3u.append([name,url,False,yaesta])
							name=""
					if '#EXTINF' in x:
						try:
							name = x.split(",")[1].replace("\n","").replace(chr(13),"")
						except:
							name = ""
		self.updateLista()

	def keyYellow(self):
		self.session.nav.stopService()
		name = self.m3u[self["menu"].getSelectedIndex()][0].rstrip("\n")
		url = self.m3u[self["menu"].getSelectedIndex()][1]
		str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(url), quote(name))
		ref = eServiceReference(str)
		self.session.nav.playService(ref)
		self.playing = True
		self["key_red"].setText(_("Stop"))

	def keyGreen(self):
		for x in self.m3u:
			if not x[3]:
				x[2] = not x[2]
		self.updateLista()

	def keyOk(self):
		if not self.m3u[self["menu"].getSelectedIndex()][3]:
			self.m3u[self["menu"].getSelectedIndex()][2] = not self.m3u[self["menu"].getSelectedIndex()][2]
		self.updateLista()

	def append(self):
		for x in self.m3u:
			if x[2]:
				name = x[0]
				url = x[1]
				str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(url), quote(name))
				ref = eServiceReference(str)
				self.addServiceToBouquet(ref,name)
				x[2] = False
				x[3] = True

		name = self.m3u[self["menu"].getSelectedIndex()][0]
		url = self.m3u[self["menu"].getSelectedIndex()][1]
		str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(url), quote(name))
		ref = eServiceReference(str)
		self.addServiceToBouquet(ref,name)
		self.m3u[self["menu"].getSelectedIndex()][2] = False
		self.m3u[self["menu"].getSelectedIndex()][3] = True
		self.updateLista()

	def keyCancel(self):
		service = self.session.nav.getCurrentlyPlayingServiceReference()
		#if service != self.cur:
		if self.playing:		
			self.session.nav.stopService()
			try:
				self.session.nav.playService(self.cur)
			except:
				pass
			self["key_red"].setText(_("Cancel"))
			self.playing = False
		else:
			self.close("cancel")

	def readFile(self, name):
		try:
			lines = open(name).readlines()
			return lines
		except:
			return ''
			pass

	def addServiceToBouquet(self, service=None, name=None):
		mutableList = self.getMutableList(self.bouquet[1])
		if not mutableList is None:
			services = getBouquetServices(self.bouquet[1])
			edit = False
			for x in range(0,len(services)):
				if services[x][0] == name:
					mutableList.removeService(services[x][1], False)
					mutableList.addService(service)
					mutableList.moveService(service, services[x][2])
					mutableList.flushChanges()
					edit = True
					break

			if not edit:
				if not mutableList.addService(service):
					mutableList.flushChanges()

	def getMutableList(self, root=eServiceReference()):
		if not self.mutableList is None:
			return self.mutableList
		serviceHandler = eServiceCenter.getInstance()
		if not root.valid():
			root=self.getRoot()
		list = root and serviceHandler.list(root)
		if list is not None:
			return list.startEdit()
		return None


class LiveStreamingLinksHeader(Screen):
	if esHD():
		skin = """
			<screen position="585,390" size="450,300" title="">
			<widget name="menu" position="15,15" size="1590,1065" scrollbarMode="showOnDemand" itemHeight="38" />
			</screen>"""
	else:
		skin = """
			<screen position="390,260" size="300,200" title="">
			<widget name="menu" position="10,10" size="1060,710" scrollbarMode="showOnDemand" />
			</screen>"""

	def __init__(self, session):
		self.skin = LiveStreamingLinksHeader.skin
		Screen.__init__(self, session)
		self["actions"] = ActionMap(["SetupActions"],
		{
			"ok": self.keyOk,
			"cancel": self.keyCancel,
		}, -2)

		self.list= []
		self.list.append('http://')
		self.list.append('rtmp://')
		self.list.append('rtsp://')
		self.list.append('mms://')
		self.list.append('m3u://')
		self.list.append('pls://')
		self.list.append('asx://')
		self["menu"] = MenuList(self.list)

		self.onLayoutFinish.append(self.layoutFinish)

	def layoutFinish(self):
		self.setTitle(_("Select URL type"))

	def keyOk(self):
		self.close(self.list[self["menu"].getSelectedIndex()])

	def keyCancel(self):
		self.close('cancel')

class spzAddIPTV(Screen):

	def __init__(self, session):
		self.skin = skin
		Screen.__init__(self, session)
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Append"))
		if fileExists(FILE_M3U):
			self["key_yellow"] = StaticText(_("From file"))
		self["key_blue"] = StaticText(_("New bouquet"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyOk,
			"cancel": self.keyCancel,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"red": self.keyCancel,
			"blue": self.keyBlue,
		}, -2)

		self["statusbar"] = StaticText(_("Select a bouquet to add channels to"))

		self.list= []
		self["menu"] = MenuList(self.list)
		self.mutableList = None
		self.servicelist = ServiceList(None)

		self.onLayoutFinish.append(self.createTopMenu)


	def keyBlue(self):
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.pyo") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.so"):
			from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
			self.session.openWithCallback(self.addBouquet, spzVirtualKeyboard, titulo = _("Enter Bouquet name"), texto = "")
		else:
			self.session.openWithCallback(self.addBouquet, VirtualKeyBoard, title = _("Enter Bouquet name"), text = '')


	def buildBouquetID(self, str):
		#tmp = str
		name = ''
		for c in str:
			c = c.lower()
			if (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9'):
				name += c
			else:
				name += '_'
		return name

	def addBouquet(self, bName):
		if bName:
			serviceHandler = eServiceCenter.getInstance()
			mutableBouquetList = serviceHandler.list(self.bouquet_root).startEdit()
			if mutableBouquetList:
				#bName += _(" (TV)")
				str = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"userbouquet.%s.tv\" ORDER BY bouquet'%(self.buildBouquetID(bName))
				new_bouquet_ref = eServiceReference(str)
				if not mutableBouquetList.addService(new_bouquet_ref):
					mutableBouquetList.flushChanges()
					eDVBDB.getInstance().reloadBouquets()
					mutableBouquet = serviceHandler.list(new_bouquet_ref).startEdit()
					if mutableBouquet:
						mutableBouquet.setListName(bName)
						mutableBouquet.flushChanges()
					else:
						print("get mutable list for new created bouquet failed")
					self.createTopMenu()


	def keyYellow(self):
		if fileExists(FILE_M3U):
			self.session.openWithCallback(self.FileaddCallback, liveStreamingFromFile, self.list[self["menu"].getSelectedIndex()])			

	def FileaddCallback(self, res):
		pass

	def initSelectionList(self):
		self.list = []
		self["menu"].setList(self.list)

	def createTopMenu(self):
		self.setTitle(_("Add IPTV Channels"))
		self.initSelectionList()
		self.list= []
		tmpList = []
		self.list = self.getBouquetList()
		self["menu"].setList(self.list)
		if esHD():
			self["menu"].instance.setItemHeight(42)

	def getBouquetList(self):
		self.service_types = service_types_tv
		if config.usage.multibouquet.value:
			self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
		else:
			self.bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(self.service_types)
		self.bouquet_root = eServiceReference(self.bouquet_rootstr)
		bouquets = [ ]
		serviceHandler = eServiceCenter.getInstance()
		if config.usage.multibouquet.value:
			list = serviceHandler.list(self.bouquet_root)
			if list:
				while True:
					s = list.getNext()
					if not s.valid():
						break
					if s.flags & eServiceReference.isDirectory:
						info = serviceHandler.info(s)
						if info:
							bouquets.append((info.getName(s), s))
				return bouquets
		else:
			info = serviceHandler.info(self.bouquet_root)
			if info:
				bouquets.append((info.getName(self.bouquet_root), self.bouquet_root))
			return bouquets
		return None

	def addServiceToBouquet(self, dest, service=None, name=None):
		mutableList = self.getMutableList(dest)
		if not mutableList is None:
			if service is None: #use current selected service
				return
			services = getBouquetServices(dest)
			edit = False
			for x in range(0,len(services)):
				if services[x][0] == name:
					mutableList.removeService(services[x][1], False)
					mutableList.addService(service)
					mutableList.moveService(service, services[x][2])
					mutableList.flushChanges()
					edit = True
					break

			if not edit:
				if not mutableList.addService(service):
					mutableList.flushChanges()

	def getMutableList(self, root=eServiceReference()):
		if not self.mutableList is None:
			return self.mutableList
		serviceHandler = eServiceCenter.getInstance()
		if not root.valid():
			root=self.getRoot()
		list = root and serviceHandler.list(root)
		if list is not None:
			return list.startEdit()
		return None

	def getRoot(self):
		return self.servicelist.getRoot()


	def keyGreen(self):
		if len(self.list) == 0:
			return
		self.name = ''
		self.url = ''
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.pyo") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.so"):
			from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
			self.session.openWithCallback(self.nameCallback, spzVirtualKeyboard, titulo = _("Enter name"), texto = "")
		else:
			self.session.openWithCallback(self.nameCallback, VirtualKeyBoard, title = _("Enter name"), text = '')

	def keyOk(self):
		if fileExists(FILE_M3U):
			self.keyYellow()
		else:
			self.keyGreen()

	def nameCallback(self, res):
		if res:
			self.name = res
			self.session.openWithCallback(self.urlTypeCallback, LiveStreamingLinksHeader)

	def urlTypeCallback(self, res):
		if res:
			if res != 'cancel':
				if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.pyo") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.so"):
					from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
					self.session.openWithCallback(self.addservice, spzVirtualKeyboard, titulo = _("Enter URL"), texto = res)
				else:
					self.session.openWithCallback(self.addservice, VirtualKeyBoard, title = _("Enter URL"), text = res)

	def addservice(self, res):
		if res:
			self.url = res
			str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(self.url), quote(self.name))
			ref = eServiceReference(str)
			self.addServiceToBouquet(self.list[self["menu"].getSelectedIndex()][1],ref, self.name)

	def keyCancel(self):
		self.close()

def main(session, **kwargs):
	session.open(spzAddIPTV)

def addstreamsetup(menuid, **kwargs):
	if menuid == "scan":
		return [(_("Add IPTV Channels"), main, "spzAddIPTV", None)]
	else:
		return []


def Plugins(**kwargs):
	list = [PluginDescriptor(name = _("Add IPTV Channels"), description = _("Add streaming channels to your channellist"), where = PluginDescriptor.WHERE_MENU, fnc = addstreamsetup)]
	return list
