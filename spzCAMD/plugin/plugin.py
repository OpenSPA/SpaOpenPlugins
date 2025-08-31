#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.FileList import FileList
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.SystemInfo import BoxInfo, getSysSoftcam
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap

from enigma import eTimer
from Tools.Directories import fileExists
from .prog import tsTasker
from os import listdir, system, walk, path as os_path, popen
from Components.Element import Element
from Components.Sources.CurrentService import CurrentService

# Configuration
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, configfile, \
	ConfigYesNo, ConfigClock, ConfigNumber, ConfigSelection, \
	config, ConfigSubsection, KEY_LEFT, KEY_RIGHT

config.plugins.spzCAMD = ConfigSubsection()
config.plugins.spzCAMD.activar = ConfigYesNo(default = False)
config.plugins.spzCAMD.restart_begin = ConfigClock(default = 60*60*4)
config.plugins.spzCAMD.restart_end = ConfigClock(default = 60*60*5)
config.plugins.spzCAMD.camd = ConfigSelection(default = _("Nothing"), choices = [])
config.plugins.spzCAMD.autostart = ConfigSelection(default = "1", choices = [("0", _("No")),("1", _("immediately")),("2", _("when a service starts"))])

config.plugins.spzCAMD.autorestart = ConfigYesNo(default = False)
config.plugins.spzCAMD.restart_check = ConfigNumber(default = 60)

config.plugins.spzCAMD.cccaminfo = ConfigYesNo(default = False)
config.plugins.spzCAMD.oscaminfo = ConfigYesNo(default = False)
config.plugins.spzCAMD.ncaminfo = ConfigYesNo(default = False)

session = None

class spzCAMD(ConfigListScreen, Screen):

	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "spzCAMD"
		self.index = -1
		self.sclist = []
		self.namelist = []
		self.chliste = []
		self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "SetupActions"],
		{
			"ok": self.action,
			"cancel": self.close_w,
			"left": self.keyleft,
			"right": self.keyright,
			"green": self.action,
			"red": self.stop,
#			"blue": self.downloads,
			"yellow": self.ecm
		}, -1)
		self["key_green"] = Button(_("Start/Restart"))
#		self["key_blue"] = Button(_("Download"))
		self["key_red"] = Button(_("Stop"))
		self["key_yellow"] = Button(_(" "))
		self["check"] = Pixmap()

		self["info"] = Label()
		self["list"] = Label("")
		title = "OpenSPA CAMD Manager"
		self.setTitle(title)
		self.list = []
		ConfigListScreen.__init__(self, self.list, session)

		self.create_config()
		self.bin = None
		self.lastCam = self.readCurrent()
		self.currentCam = self.lastCam
		self.readScripts()
		self.TimerTemp = eTimer()
		self.TimerTemp.callback.append(self.ecml)
		self.move()

		self.ecm()

	def close_w(self):
		self.save()
		self.close()

	def keyleft(self):
		self["config"].handleKey(KEY_LEFT)
		self.move()

	def keyright(self):
		self["config"].handleKey(KEY_RIGHT)
		self.move()

	def move(self):
		if config.plugins.spzCAMD.camd.value == self.currentCam and config.plugins.spzCAMD.camd.value != _("Nothing"):
			self["check"].show()
		else:
			self["check"].hide()
		self.create_config()

	def create_config(self):
		self.list = []
		self.list.append(getConfigListEntry(_("CAMD"), config.plugins.spzCAMD.camd, None, None))
		self.list.append(getConfigListEntry(_("CAMD start after boot"),config.plugins.spzCAMD.autostart, None, None ))
		self.list.append(getConfigListEntry(_("Enable Daily AutoRestart"),config.plugins.spzCAMD.activar, self.autoRestartInfo, self.autoRestartInfo ))
		if config.plugins.spzCAMD.activar.value:
			self.list.append(getConfigListEntry("    "+_("Daily AutoRestart start time"), config.plugins.spzCAMD.restart_begin, self.autoRestartInfo, self.autoRestartInfo ))
			self.list.append(getConfigListEntry("    "+_("Daily AutoRestart end time"), config.plugins.spzCAMD.restart_end, self.autoRestartInfo, self.autoRestartInfo ))

		self.list.append(getConfigListEntry(_("Restart CAMD after accidental closure"),config.plugins.spzCAMD.autorestart, self.autoRestartInfo, self.autoRestartInfo ))
		if config.plugins.spzCAMD.autorestart.value:
			self.list.append(getConfigListEntry("    "+_("Check every (seg)"),config.plugins.spzCAMD.restart_check, self.autoRestartInfo, self.autoRestartInfo ))

		softcams = listdir('/usr/bin/')
		for softcam in softcams:
			if softcam.lower().startswith('cccam'):
				config.plugins.spzCAMD.cccaminfo.value = True
			elif softcam.lower().startswith('oscam'):
				config.plugins.spzCAMD.oscaminfo.value = True
			elif softcam.lower().startswith('ncam'):
				config.plugins.spzCAMD.ncaminfo.value = True

		if getSysSoftcam() == "cccam":
			BoxInfo.setItem("ShowCccamInfo", True)
			BoxInfo.setItem("ShowOscamInfo", False)
			BoxInfo.setItem("ShowNcamInfo", False)
			self.list.append(getConfigListEntry(_("Show CCcam Info in extensions menu"), config.cccaminfo.showInExtensions, None, None ))
		if getSysSoftcam() in ("oscam", "ncam+", "ncam "):
			BoxInfo.setItem("ShowCccamInfo", False)
			if getSysSoftcam() == "oscam":
				BoxInfo.setItem("ShowOscamInfo", True)
				BoxInfo.setItem("ShowNcamInfo", False)
				self.list.append(getConfigListEntry(_("Show OSCam Info in extensions menu"), config.oscaminfo.showInExtensions, None, None ))
				config.ncaminfo.showInExtensions.value = False
				config.oscaminfo.showInExtensions.save()
			else:
				BoxInfo.setItem("ShowNcamInfo", True)
				BoxInfo.setItem("ShowOscamInfo", False)
				self.list.append(getConfigListEntry(_("Show NCam Info in extensions menu"), config.ncaminfo.showInExtensions, None, None ))
				config.oscaminfo.showInExtensions.value = False
				config.ncaminfo.showInExtensions.save()
		if not getSysSoftcam():
			BoxInfo.setItem("ShowOscamInfo", False)
			BoxInfo.setItem("ShowNcamInfo", False)
			BoxInfo.setItem("ShowCccamInfo", False)
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def getLastIndex(self):
		a = 0
		if len(self.namelist) > 0:
			for x in self.namelist:
				if x[0] == self.lastCam:
					return a
				else:
					a+=1
		else:
			return -1
		return -1

	def getCurrentIndex(self):
		self.currentCam = config.plugins.spzCAMD.camd.value
		a = 0
		if len(self.namelist) > 0:
			for x in self.namelist:
				if x[0] == self.currentCam:
					return a
				else:
					a+=1
		else:
			return -1
		return -1

	def action(self):
		self.session.nav.playService(None)
		self.TimerTemp.stop()
		last = self.getLastIndex()
		var = self.getCurrentIndex()
		if var > -1:
			if last > -1:
				self.cmd2 = "sh /usr/script/" + self.sclist[last] + " stop"
				cmdcam = open("/etc/Camdcmd.sh", "w")
				cmdcam.write("#!/bin/sh\n" + self.cmd2 + "\nsleep 2\n")
				self.cmd1 = "sh /usr/script/" + self.sclist[var] + " start"
				self.cmd3 = "sh /usr/script/" + self.sclist[var] + " stop"
				cmdcam.write(self.cmd1)
				cmdcam.close()
				system("chmod 755 /etc/Camdcmd.sh &")
				system("sleep 1")
				system("sh /etc/Camdcmd.sh")
				self.session.openWithCallback(self.callback, MessageBox, _("Stop Camd:") + " " + str(self.namelist[last][0]) + "\n" + _("Start Camd:") + " " + str(self.namelist[var][0]), type = MessageBox.TYPE_INFO, timeout = 8)
			else:
				try:
					self.cmd1 = "sh /usr/script/" + self.sclist[var] + " start"
					self.cmd3 = "sh /usr/script/" + self.sclist[var] + " stop"
					cmdcam = open("/etc/Camdcmd.sh", "w")
					cmdcam.write("#!/bin/sh\n" + self.cmd1)
					cmdcam.close()
					system("chmod 755 /etc/Camdcmd.sh &")
					system("sleep 1")
					system("sh /etc/Camdcmd.sh")
					self.session.openWithCallback(self.callback, MessageBox, _("Start Camd:") + " " + str(self.namelist[var][0]), type = MessageBox.TYPE_INFO, timeout = 8)
				except:
					self.close()

			if fileExists("/etc/Camdcmd.sh") is True :
				system("rm \"/etc/Camdcmd.sh\"")

			if last != var:
				try:
					self.lastCam = self.namelist[var][0]
				except:
					self.close()

			self.save()
			self.currentCam = self.lastCam
			self.bin = self.namelist[var][1]
			self.writeFile()
			self.session.nav.playService(self.oldService)
			self.move()
			self.ecm()
		else:
			self.stop()

	def save(self):
		cambiado = False
		for x in self["config"].list:
			if x[1].isChanged():
				x[1].save()
				if x[2] is not None:
					cambiado = True

		config.plugins.spzCAMD.save()
		configfile.save()
		if cambiado:
			self.autoRestartInfo()

	def autoRestartInfo(self, dummy=None):
		self.create_config()
		tsTasker.ShowAutoRestartInfo()

	def writeFile(self):
		if not self.lastCam is None:
			clist = open("/etc/.ActiveCamd", "w")
			clist.write(self.lastCam)
			clist.close()
			open("/etc/.BinCamd","w").write(self.bin)

		rstcam = open("/etc/.CamdReStart.sh", "w")
		rstcam.write("#!/bin/sh\n" + self.cmd3 + "\nsleep 2\n" + self.cmd1)
		rstcam.close()
		system("chmod 755 /etc/.CamdReStart.sh")

		stcam = open("/etc/.CamdStart.sh", "w")
		stcam.write("#!/bin/sh\n" + self.cmd1)
		stcam.close()
		system("chmod 755 /etc/.CamdStart.sh")
		if not fileExists("/tmp/.spzCAMD"):
			system("echo '' > /tmp/.spzCAMD")

	def stop(self):
		last = self.getLastIndex()

		if last > -1:
			self.session.nav.playService(None)
			self.cmd1 = "/usr/script/" + self.sclist[last] + " stop"
			system(self.cmd1)
			self.session.openWithCallback(self.callback, MessageBox, _("Stop Camd:") + " " + str(self.namelist[last][0]), type = MessageBox.TYPE_INFO, timeout = 8)
		else:
			return

		try:
			system("rm /etc/.CamdStart.sh")
			system("rm /etc/.CamdReStart.sh")
			system("rm /etc/.ActiveCamd")
		except:
			pass
		system("sleep 4")
		self.TimerTemp.stop()
		self["info"].setText(" ")
		self.session.nav.playService(self.oldService)
		config.plugins.spzCAMD.camd.value=_("Nothing")
		config.plugins.spzCAMD.camd.save()
		self.save()
		self.lastCam = None
		self.currentCam = None
		self.move()

	def readScripts(self):
		idx = 0
		scriptliste = []
		pliste = []
		nliste = []
		path = "/usr/script/"
		if not os_path.exists(path):
			system("mkdir " + str(path))

		for root, dirs, files in walk(path):
			for name in files:
				scriptliste.append(name)

		self.sclist = []
		namime=_("Nothing")
		for lines in scriptliste:
			dat = path + lines
			if fileExists(dat):
				sfile = open(dat, "r", encoding="ISO 8859-1")
				nam = ""
				nambin = ""
				for line in sfile:
					line.strip()
					if line[0:7] == "CAMD_ID": nam = line.split("=")[1]
					if line[0:5] == "CAMID": nam = line.split("=")[1]
					if line[0:9] == "CAMD_NAME": namime=line.split("\"")[1]
					if line[0:7] == "CAMNAME": namime=line.split("\"")[1]
					if "killall" in line:
						killine = line.split()
						for k in killine:
							if not "killall" in k and not "-9" in k and not ">" in k and not "&" in k:
								nambin = nambin + k + " "
				sfile.close()
				if nam:
					if not namime: namime = nam + " - w/o CAMD_NAME"
					pliste.append((namime,nambin[:-1]))
					nliste.append(namime)
					self.sclist.append(lines)
					if self.currentCam == namime:
						self.bin = nambin.strip()

		self.namelist = pliste
		nliste.append(_("Nothing"))
		self.chliste = nliste
		if self.currentCam == None: self.currentCam = _("Nothing")
		config.plugins.spzCAMD.camd.setChoices(nliste)
		config.plugins.spzCAMD.camd.value = self.currentCam


	def readCurrent(self):
		try:
			clist = open("/etc/.ActiveCamd", "r")
		except:
			return None

		lastcam = None
		if not clist is None:
			for line in clist:
				lastcam = line
			clist.close()

		return lastcam

#	def downloads(self):
		# self.session.openWithCallback(self.comprueba,descargasSPZ)
#		from Plugins.Extensions.spazeMenu.spzPlugins.descargasSPZ.plugin import descargasSPZ
#		self.session.openWithCallback(self.comprueba,descargasSPZ,categoria="10",nombrecategoria="Camd & Emulation")

	def comprueba(self, retval=True):
		if retval:
			self.readScripts()
			self.create_config()

	def ecm(self):
		self.ecml()
		self.TimerTemp.start(3000, False)

	def ecml(self):
		ecmf = ""
		caido = False

		if fileExists("/etc/.BinCamd") and fileExists("/etc/.CamdReStart.sh"):
			ebin = open("/etc/.BinCamd","r").read().split()
			caido = False
			for e in ebin:
				check = popen("pidof "+e).read()
				if check == "":
					caido = True
					ecmf = ecmf + e + " " + _("not working") + "\n"
			if caido:
				ecmf = ecmf[:-1]

		if fileExists("/tmp/ecm.info") and not caido:
			myfile = open("/tmp/ecm.info","r")
			ecmf = ""
			for line in myfile.readlines():
				print(line)
				ecmf = ecmf + line

		self["info"].setText(ecmf)

	def autocam(self):
		current = None
		try:
			clist = open("/etc/.ActiveCamd", "r")
			print('found list')
		except:
			return None

		if not clist is None:
			for line in clist:
				current = line
			clist.close()

		print("current =", current)

		if not fileExists("/etc/autocam.txt"):
			alist = open("/etc/autocam.txt", "w")
			alist.close()
		self.cleanauto()
		alist = open("/etc/autocam.txt", "a")
		alist.write(self.oldService.toString() + "\n")
		last = self.getLastIndex()
		alist.write(current + "\n")
		alist.close()
		self.session.openWithCallback(self.callback, MessageBox, _("Autocam assigned to the current channel"), type = MessageBox.TYPE_INFO, timeout = 10)

	def cleanauto(self):
		delcam = "no"
		if not fileExists("/etc/autocam.txt"):
			return
		myfile = open("/etc/autocam.txt", "r")
		myfile2 = open("/etc/autocam2.txt", "w")
		icount = 0
		for line in myfile.readlines():
			print("We are in CAMDManager line, self.oldService.toString() =", line, self.oldService.toString())
			if line[:-1] == self.oldService.toString():
				delcam = "yes"
				icount = icount+1
				continue
			if delcam == "yes":
				delcam = "no"
				icount = icount+1
				continue

			myfile2.write(line)
			icount = icount+1
		myfile.close()
		myfile2.close()
		system("rm /etc/autocam.txt")
		system("cp /etc/autocam2.txt /etc/autocam.txt")

class startcamd(Element):
	def __init__(self,session):
		self.timer = eTimer()
		self.timer.callback.append(self.poll)
		Element.__init__(self)
		self.session = session

	def changed(self, *args, **kwargs):
		try:
			service = self.source.service
			serviceref = self.source.serviceref
			if serviceref is not None and service is not None and not fileExists("/tmp/.spzCAMD") and fileExists("/etc/.CamdStart.sh"):
				self.timer.start(2000, True) #temporizacion de 2 segundos
		except:
			pass

	def poll(self):
		if fileExists("/etc/.ActiveCamd"):
			print("[spzCAMD] Started")
			try:
				clist = open("/etc/.ActiveCamd", "r")
			except:
				pass

			lastcam = None
			if not clist is None:
				for line in clist:
					lastcam = line
				clist.close()

			system("sh /etc/.CamdStart.sh")
			system("echo '' > /tmp/.spzCAMD")
			self.timer.stop()

###################################
###################################
def startConfig(session, **kwargs):
	session.open(spzCAMD)

def mainmenu(menuid):
	if menuid != "cam":
		return [ ]
	return [(_("OpenSPA CAMD Manager"), startConfig, "camdmngr", None)]

def callback(retval):
	pass

def autostart(reason, **kwargs):
	"called with reason=1 to during shutdown, with reason=0 at startup?"
	if not fileExists("/etc/.BinCamd") and fileExists("/etc/.CamdStart.sh"):
		sfile = open("/etc/.CamdStart.sh", "r")
		for line in sfile:
			if line[:2] == "sh":
				scriptf = line.split()[1]
		sfile.close()
		nambin = ""
		if scriptf:
			sfile = open(scriptf, "r")
			for line in sfile:
				if "killall" in line:
					nambin = nambin + line.split()[2] + " "
			sfile.close()
			if nambin != "":
				open("/etc/.BinCamd","w").write(nambin[:-1])
	global session
	if reason == 0:
		if "session" in kwargs:
			global gSession
			gSession = kwargs["session"]
			session = kwargs["session"]
			tsTasker.Initialize(gSession)

		if config.plugins.spzCAMD.autostart.value == "2":
			session.screen["service"] = CurrentService(session.nav)
			startcamd(session).connect(session.screen["service"])
		elif config.plugins.spzCAMD.autostart.value == "1":
			print("[spzCAMD] Started")
			try:
				if not fileExists("/tmp/.spzCAMD") and fileExists("/etc/.CamdStart.sh"):
					system("sleep 2")
					system("sh /etc/.CamdStart.sh")
					system("echo '' > /tmp/.spzCAMD")
			except:
				pass
		elif config.plugins.spzCAMD.autostart.value == "0":
			try:
				if not fileExists("/tmp/.spzCAMD"):
					system("rm /etc/.CamdStart.sh")
					system("rm /etc/.CamdReStart.sh")
					system("rm /etc/.ActiveCamd")
			except:
				pass

	else:
		pass

def Plugins(**kwargs):
	return [
	PluginDescriptor(
		name=_("OpenSPA CAMD Manager"),
		where = PluginDescriptor.WHERE_MENU, fnc=mainmenu),
	PluginDescriptor(
		name=_("OpenSPA CAMD Manager"),
		where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=startConfig),
	PluginDescriptor(
		name="OpenSPA CAMD Manager",
		description = "OpanSPA CAMD Manager",
		where = [
			PluginDescriptor.WHERE_AUTOSTART,
			PluginDescriptor.WHERE_SESSIONSTART
		],
		fnc = autostart,
	), ]
