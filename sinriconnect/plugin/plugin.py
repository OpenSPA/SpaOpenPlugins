# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_ACTIVE_SKIN, SCOPE_LANGUAGE, fileExists
from Components.ConfigList import ConfigListScreen
from Components.Language import language
import gettext
from os import environ, system, remove
from Screens.MessageBox import MessageBox

from .sinriconnect import sinriconnect
from .channels import getBouquetList, getBlackBouquets

from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Element import Element
from Components.MenuList import MenuList
from Components.Sources.CurrentService import CurrentService
from enigma import eTimer, eServiceReference, eListboxPythonMultiContent, gFont, loadPNG, BT_SCALE, BT_KEEP_ASPECT_RATIO, getDesktop
from ServiceReference import ServiceReference
from Screens.ChannelSelection import SimpleChannelSelection
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend

##############################################

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("SinriConnect", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SinriConnect/locale/"))

def _(txt):
	t = gettext.dgettext("SinriConnect", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
#############

def esHD():
	if getDesktop(0).size().width() > 1400:
		return True
	else:
		return False

def fhd(num):
	if esHD():
		prod=num*1.5
	else: prod=num
	return int(round(prod))

def fontHD(nombre):
	if esHD():
		fuente = nombre+"HD"
	else:
		fuente = nombre
	return fuente


CLIENT = None
if esHD():
	ICON_ON = "%s%s/img/connected.png" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SinriConnect")
	ICON_OFF = "%s%s/img/disconnected.png" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SinriConnect")
else:
	ICON_ON = "%s%s/img/connectedSD.png" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SinriConnect")
	ICON_OFF = "%s%s/img/disconnectedSD.png" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SinriConnect")
	
from Components.config import ConfigYesNo, config, ConfigSubsection, getConfigListEntry, ConfigInteger, ConfigSubList, ConfigText, ConfigNumber, ConfigSelection


config.plugins.sinric = ConfigSubsection()
config.plugins.sinric.connectatstart = ConfigYesNo(default = False)
config.plugins.sinric.viewvolbar = ConfigYesNo(default = True)
config.plugins.sinric.viewpopup = ConfigYesNo(default = False)
config.plugins.sinric.logintent = ConfigYesNo(default = False)
config.plugins.sinric.use_table_ch = ConfigYesNo(default = False)

config.plugins.sinric.channelscount = ConfigInteger(0)
config.plugins.sinric.channels = ConfigSubList()

acciones = [("None", _("Do nothing")),("restart", _("Restart Enigma")),("reboot", _("Reboot Receiver")),("camdrestart", _("Restart CAMD")),("info", _("Show Actual Event Info")),("epgchann", _("Show the EPG of the Current Channel")),("guide",_("Show EPG Guide")),("script",_("Launch script /usr/script/sinric.sh")),("kodi",_("Launch Kodi")),("exit",_("Simulate Pressing the Exit Button")),("left",_("Simulate Pressing the Left Button")),("right",_("Simulate Pressing the Right Button")),("up",_("Simulate Pressing the Up Button")),("down",_("Simulate Pressing the Down Button")),("ok",_("Simulate Pressing the OK Button")),("menu",_("Simulate Pressing the Menu Button")),("red",_("Simulate Pressing the Red Button")),("green",_("Simulate Pressing the Green Button")),("yellow",_("Simulate Pressing the Yellow Button")),("blue",_("Simulate Pressing the Blue Button"))]

if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spaTimerEntry/plugin.so") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spaTimerEntry/plugin.py") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spaTimerEntry/plugin.pyc"):
	acciones.append(("epg_search",_("Change to the channel programmed search")))
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/plugin.so") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/plugin.py") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/plugin.pyc"):
	acciones.append(("epgdownload", _("Download EPG")))

config.plugins.sinric.input = ConfigSubList()
config.plugins.sinric.hdmi = ConfigSubList()
for i in range(0,10):
	config.plugins.sinric.input.append(ConfigSubsection())
	config.plugins.sinric.input[i].accion= ConfigSelection(default = "None",choices = acciones)
	config.plugins.sinric.hdmi.append(ConfigSubsection())
	config.plugins.sinric.hdmi[i].accion= ConfigSelection(default = "None",choices = acciones)


class listado(MenuList):
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setItemHeight(fhd(25))
		self.l.setFont(0, gFont(fontHD('Regular'), 19))

def listentry(name, black):
	res = [(name, black)]
	picture = None
	res.append(MultiContentEntryText(pos=(fhd(45), fhd(2)), size=(fhd(750), fhd(25)), font=0, text=name))
	if not black:
		picture = resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_on.png')
	else:
		picture = resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_off.png')
	if picture != None:
		if fileExists(picture):
			res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(10), fhd(3)), size=(fhd(20), fhd(19)), png=loadPNG(picture), flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
		
	return res





TITLE = "SinriConnect by OpenSPA"


if esHD():
	skin = """
		<screen name="sinriconnectconfig" position="center,center" size="1170,550" title="SinriConnect by OpenSPA" >
				<eLabel position="0,0" size="300,600" backgroundColor="#00FFFFFF" />
				<ePixmap pixmap="imagenestmp/sinric.png" position="0,0" size="300,115" zPosition="2" alphatest="blend" />
				<ePixmap pixmap="imagenestmp/alexa.png" position="0,130" size="300,168" zPosition="2" alphatest="blend" />
				<ePixmap pixmap="imagenestmp/google.png" position="0,300" size="300,168" zPosition="2" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/red_HD.png" position="308,470" size="210,60" transparent="1" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/green_HD.png" position="523,470" size="210,60" transparent="1" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/yellow_HD.png" position="738,470" size="210,60" transparent="1" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/blue_HD.png" position="953,470" size="210,60" transparent="1" alphatest="blend" />
				<widget source="key_red" render="Label" position="308,470" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF"/>
				<widget source="key_green" render="Label" position="523,470" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF" />
				<widget source="key_yellow" render="Label" position="738,470" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF"/>
				<widget source="key_blue" render="Label"  position="953,470" zPosition="1" size="210,60" font="Regular;30" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF"/>
				<widget name="config" position="300,10" size="865,428" scrollbarMode="showOnDemand" transparent="1" font="RegularHD; 17" itemHeight="35" />
				<widget name="menu" position="300,10" scrollbarMode="showOnDemand" size="865,428"/>
				<widget name="picConn" position="20,471" size="42,42" zPosition="2" alphatest="on" transparent="1" />
				<widget name="info" position="70,471" size="200,45" font="RegularHD;20" halign="center" zPosition="2" foregroundColor="#00000000" transparent="1" />
				</screen>""" 
else:
	skin = """
		<screen name="sinriconnectconfig" position="center,center" size="780,367" title="SinriConnect by OpenSPA" >
				<eLabel position="0,0" size="200,400" backgroundColor="#00FFFFFF" />
				<ePixmap pixmap="imagenestmp/sinricSD.png" position="0,0" size="200,77" zPosition="2" alphatest="blend" />
				<ePixmap pixmap="imagenestmp/alexaSD.png" position="0,87" size="200,112" zPosition="2" alphatest="blend" />
				<ePixmap pixmap="imagenestmp/googleSD.png" position="0,200" size="200,112" zPosition="2" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/red.png" position="205,313" size="140,40" transparent="1" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/green.png" position="349,313" size="140,40" transparent="1" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/yellow.png" position="492,313" size="140,40" transparent="1" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/blue.png" position="635,313" size="140,40" transparent="1" alphatest="blend" />
				<widget source="key_red" render="Label" position="205,313" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF" />
				<widget source="key_green" render="Label" position="349,313" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF"/>
				<widget source="key_yellow" render="Label" position="492,313" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF"/>
				<widget source="key_blue" render="Label"  position="635,313" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="#00FFFFFF"/>
				<widget name="config" position="200,7" size="577,293" scrollbarMode="showOnDemand" transparent="1" font="Regular; 18" itemHeight="25" />
				<widget name="picConn" position="13,314" size="28,28" zPosition="2" alphatest="on" transparent="1" />
				<widget name="info" position="47,316" size="133,30" font="Regular;20" halign="center" zPosition="2" foregroundColor="#00000000" transparent="1" />
				</screen>""" 

skin=skin.replace("imagenestmp/","%s%s/img/" % (resolveFilename(SCOPE_PLUGINS), "Extensions/SinriConnect"))


class sinriconnectconfig(ConfigListScreen,Screen):
	def __init__(self, session):
		self.skin = skin
		self.session = session
		Screen.__init__(self, session)
		self.configlist = []
		ConfigListScreen.__init__(self, self.configlist)
		
		self["picConn"] = Pixmap()
		self["info"] = Label()
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Connect"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText(_("Channels"))
		self["menu"] = listado(list())


		self["setupActions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.salir,
			"green": self.green,
			"blue": self.blue,
			"yellow": self.yellow,
			"cancel": self.salir,
			"ok": self.ok,
		}, -2)

		self.page = 1
		self.index = -1
		self.create_config()
				
		self.onShow.append(self.actualiza)

	def create_config(self):
		self.configlist = []
		if self.page == 1:
			self["menu"].hide()
			self["config"].show()
			self.setTitle(TITLE)
			self["key_red"].setText(_("Exit"))
			if CLIENT and CLIENT.isconnected():
				self["key_green"].setText("")
			else:
				self["key_green"].setText(_("Connect"))
			self["key_blue"].setText(_("Channels"))
			self["key_yellow"].setText(_("Bouquets"))
			self.configlist.append(getConfigListEntry(_("Connect when starting Enigma"), config.plugins.sinric.connectatstart))
			#Conectar al iniciar Enigma
			self.configlist.append(getConfigListEntry(_("See Popup when connecting from start"), config.plugins.sinric.viewpopup))
			#Ver Popup al conectar desde inicio
			self.configlist.append(getConfigListEntry(_("See the volume bar when changing it"), config.plugins.sinric.viewvolbar))
			#ver la barra de volumen al cambiarlo
			self.configlist.append(getConfigListEntry(_("Add interactions in the log"), config.plugins.sinric.logintent))
			#Añadir interacciones en el log
			self.configlist.append(getConfigListEntry(_("Use Custom Channel Table"), config.plugins.sinric.use_table_ch))
			#Usar Tabla de Canales Personalizada
			for i in range(0,10):
				self.configlist.append(getConfigListEntry("INPUT "+str(i+1), config.plugins.sinric.input[i].accion))
			for i in range(0,10):
				self.configlist.append(getConfigListEntry("HDMI "+str(i+1), config.plugins.sinric.hdmi[i].accion))

		elif self.page == 2:
			self.setTitle(TITLE + " - " + _("CHANNEL TABLE"))
			self["key_red"].setText(_("Back"))
			self["key_green"].setText(_("Append"))
			i = 0
			if fileExists("/etc/keys/sinric.chan"):
				chann=open("/etc/keys/sinric.chan","r").read().split("\n")
				while i<config.plugins.sinric.channelscount.value:
					txt = _("Channel Number %d  ==>") % config.plugins.sinric.channels[i].number.value
					self.configlist.append(getConfigListEntry(txt, config.plugins.sinric.channels[i].name))
					i += 1
			if i>0:
				self["key_blue"].setText(_("Edit"))
				self["key_yellow"].setText(_("Remove"))
			else:
				self["key_blue"].setText("")
				self["key_yellow"].setText("")
			

		elif self.page == 3:
			self.setTitle(TITLE + " - " + _("CHANNEL TABLE") + " - " + _("Edit"))
			self["key_blue"].setText("")
			self["key_green"].setText("")
			self["key_yellow"].setText("")
			txt = _("Channel Number")
			self.configlist.append(getConfigListEntry(_("Channel Number"), config.plugins.sinric.channels[self.index].number))
			self.configlist.append(getConfigListEntry(_("Channel (Press Ok to change)"), config.plugins.sinric.channels[self.index].name))
			
		elif self.page == 4:
			self.setTitle(TITLE + " - " + _("Bouquets"))
			self["config"].hide()
			self["menu"].show()
			self["key_blue"].setText(_("Switch All"))
			self["key_green"].setText("")
			self["key_yellow"].setText("")
			self["key_red"].setText(_("Back"))
			lista = []
			for b in self.bouquets:
				lista.append(listentry(b[0],b[1]))
			self["menu"].setList(lista)
		
		
		if self.page < 4:
			self["config"].list = self.configlist
						

	def actualiza(self):
		global CLIENT
		if CLIENT and CLIENT.isconnected():
			self['picConn'].instance.setPixmapFromFile(ICON_ON)
			self["info"].setText(_("Connected"))
			self["key_green"].setText("")
		else:
			self['picConn'].instance.setPixmapFromFile(ICON_OFF)
			self["info"].setText(_("Disconnected"))
			self["key_green"].setText(_("Connect"))
	

	def salir(self):
		if self.page == 1:
			for x in self["config"].list:
				if x[1].isChanged():
					x[1].save()

			self.close()
		elif self.page == 2:
			self.savechannels()
			self.page = self.page -1
			self.create_config()
		elif self.page == 3:
			self.savechannels()
			self.readchannels()
			self.page = self.page-1
			self.create_config()
			self["config"].setCurrentIndex(self.index)
		elif self.page == 4:
			self.saveblack()
			self.page = 1
			self.create_config()
			
	def saveblack(self):
		f = open("/etc/keys/sinric.blackbouquets","w")
		for bouquet in self.bouquets:
			if bouquet[1]:
				f.write(bouquet[0]+"\n")
		f.close()

	def ok(self):
		if self.page == 2:
			self.index = self["config"].getCurrentIndex()
			self.page = 3
			self.create_config()
		elif self.page == 3:
			cur = self["config"].getCurrentIndex()
			if cur == 1:		
				self.session.openWithCallback(
					self.finishedChannelSelection,
					SimpleChannelSelection,
					_("Select channel")
				)
		elif self.page == 4:
			try:
				self.bouquets[self["menu"].getSelectedIndex()][1] = not self.bouquets[self["menu"].getSelectedIndex()][1]
			except:
				pass
			self.create_config()


	def finishedChannelSelection(self, *args):
		if args:
			refser = ServiceReference(args[0])
			nomcan=refser.getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
			config.plugins.sinric.channels[self.index].name.value = nomcan
			config.plugins.sinric.channels[self.index].channel.value = args[0].toString()
			self.create_config()
	
	def readchannels(self):
		i = 0
		if fileExists("/etc/keys/sinric.chan"):
			chann=open("/etc/keys/sinric.chan","r").read().split("\n")
			i = 0
			for can in chann:
				ch = can.split(" ")
				if len(ch)>1:
					s = can.split(":")
					if len(s)==12:
						nomcan = s[-1]
						service = " ".join(ch[1:])
					else:
						try:
							service = ch[1]
							refser=eServiceReference(ch[1])
							nomcan=ServiceReference(refser).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
							if len(nomcan)==0 or nomcan is None:
								nomcan=_("*** CHANNEL NOT FOUND ***")
						except:
							nomcan=_("*** CHANNEL NOT FOUND ***")
					config.plugins.sinric.channels.append(ConfigSubsection())
					config.plugins.sinric.channels[i].number= ConfigNumber(int(ch[0]))
					config.plugins.sinric.channels[i].name = ConfigText(nomcan)
					config.plugins.sinric.channels[i].channel = ConfigText(service)
					i += 1
		config.plugins.sinric.channelscount.value = i

	def savechannels(self):
		i = 0
		txt = ""
		while i<config.plugins.sinric.channelscount.value:
			if len(config.plugins.sinric.channels[i].channel.value)>10:
				txt = "%s%d %s\n" % (txt,config.plugins.sinric.channels[i].number.value, config.plugins.sinric.channels[i].channel.value)
			i += 1
		if len(txt)>0:
			open("/etc/keys/sinric.chan","w").write(txt)			


	def yellow(self):
		if self.page == 2:
			self.index = self["config"].getCurrentIndex()
			config.plugins.sinric.channels.remove(config.plugins.sinric.channels[self.index])
			config.plugins.sinric.channelscount.value = config.plugins.sinric.channelscount.value -1
			self.savechannels()
			self.create_config()
		elif self.page == 1:
			self.page = 4
			self.tbouquets = getBouquetList()
			self.bbouquets = getBlackBouquets()
			self.bouquets = []
			for b in self.tbouquets:
				black = b[0] in self.bbouquets
				self.bouquets.append([b[0],black])
			self.create_config()
			
					
	def green(self):
		if self.page ==1:
			self.connect()
		elif self.page ==2:
			self.index = config.plugins.sinric.channelscount.value
			config.plugins.sinric.channels.append(ConfigSubsection())
			config.plugins.sinric.channels[self.index].number= ConfigNumber(0)
			config.plugins.sinric.channels[self.index].name = ConfigText("")
			config.plugins.sinric.channels[self.index].channel = ConfigText("")
			config.plugins.sinric.channelscount.value = self.index + 1
			self.page = 3
			self.create_config()

	def blue(self):
		if self.page == 1:
			self.readchannels()
			self.page = 2
			self.create_config()
		elif self.page == 2:
			self.ok()
		elif self.page ==4:
			for x in self.bouquets:
				x[1] = not x[1]
			self.create_config()

	def connect(self):
		appkey, appsecret, tvid = getkeys()
		global CLIENT
		if CLIENT is None:
			CLIENT = sinriconnect(self.session, appkey, appsecret, tvid, config.plugins.sinric.logintent.value)
			CLIENT.run()
		self.actualiza()

def getkeys():
	APP_KEY = APP_SECRET = TV_ID = ""
	if fileExists("/etc/keys/sinric.keys"):
		keys=open("/etc/keys/sinric.keys","r").read().split("\n")
		for l in keys:
			try:
				key = l.split("=")
				if key[0].strip() == "APP_KEY":
					APP_KEY = key[1].strip()
				if key[0].strip() == "APP_SECRET":
					APP_SECRET = key[1].strip()
				if key[0].strip() == "TV_ID":
					TV_ID = key[1].strip()
			except:
				pass
	return APP_KEY, APP_SECRET, TV_ID

class startclient(Element):
	def __init__(self,session,appkey, appsecret, tvid):  
		self.timer = eTimer()
		self.timer.callback.append(self.poll)
		Element.__init__(self)
		self.session = session
		self.appkey = appkey
		self.appsecret= appsecret
		self.tvid=tvid

	def changed(self, *args, **kwargs):
		try:
			service = self.source.service
			serviceref = self.source.serviceref
			if serviceref is not None and CLIENT is None:
				self.timer.start(4000, True) #temporizacion de 4 segundos
		except:
			pass

	def poll(self):
		global CLIENT
		if CLIENT is None:
			CLIENT = sinriconnect(self.session, self.appkey, self.appsecret, self.tvid, config.plugins.sinric.logintent.value)
			CLIENT.run()
			if CLIENT and config.plugins.sinric.viewpopup.value:
				try:
					from Plugins.Extensions.spazeMenu.Popup import Popup
					self.session.open(Popup, _("SinriConnect"),_("Client is connected"),type=Popup.TYPE_INFO, timeout = 5, picon=resolveFilename(SCOPE_PLUGINS)+"Extensions/SinriConnect/img/logo_sinric.png",enable_fade=True)
				except:
					pass
		self.timer.stop()

def autostart(reason, **kwargs):
	appkey, appsecret, tvid = getkeys()
	if reason == 0:
		if "session" in kwargs:
			session = kwargs["session"]
			if len(appkey)>0 and len(appsecret)>0 and len(tvid)>0 and config.plugins.sinric.connectatstart.value:
				session.screen["service"] = CurrentService(session.nav)
				startclient(session,appkey, appsecret, tvid).connect(session.screen["service"])

def main(session, **kwargs):
	appkey, appsecret, tvid = getkeys()
	if len(appkey)==0 or len(appsecret)==0 or len(tvid)==0:
		session.open(MessageBox, _("The configuration file is not filled in correctly. You must first open an account at https://sinric.pro/ and create a device of type Tv. The application key, application secret and device id must be entered in the /etc/keys/sinric.keys file after the = sign of each key."), MessageBox.TYPE_INFO, timeout=10)
		#El archivo de configuracion no esta correctamente rellenado. Primero debes abrir una cuenta en https://sinric.pro/ y crear un dispositivo de tipo Tv. La clave de aplicacion, secreto de aplicacion y id del dispositivos debes introducirlas en el archivo /etc/keys/sinric.keys despues del signo = de cada clave.
	else:
		session.open(sinriconnectconfig)


def Plugins(**kwargs):
	lista=[]
	lista.append(PluginDescriptor(
			name = _("SinriConnect"), 
			description = _("Allows you to control the receiver with Alexa or Google Home using Sinric Pro."), 
			where = PluginDescriptor.WHERE_PLUGINMENU, 
			icon ="icon.png",
			fnc=main))
	lista.append(PluginDescriptor(name=_("SinriConnect"), where = PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart))

	return lista
