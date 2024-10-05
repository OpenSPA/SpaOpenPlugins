from sinric import SinricPro
import asyncio
import threading
from Components.Element import Element
from Screens import Standby
from Components.VolumeControl import VolumeControl
from Tools import Notifications
from Components.config import config
from .channels import channels
from enigma import eActionMap, eServiceReference, iServiceInformation, eTimer
from os import system
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from ServiceReference import ServiceReference

VOLVOICE = False
INITIAL = True
GSESSION = None
VOL = -1

tipos = {"DVB-T":4, "DVB-C":3, "DVB-S":2,"IPTV":1}
resol = {"UHD":3, "HD":2, "SD":1}


def power_state(device_id, state):
	print('[SinriConnect] Change Power State to: ', state)
	if state == "On" and Standby.inStandby:
		Standby.inStandby.Power()
	elif state == "Off" and not Standby.inStandby:
		Notifications.AddNotification(Standby.Standby)
	return True, state


def set_volume(device_id, volume):
	print('[SinriConnect] Set Volume to: ', volume)
	global VOLVOICE, INITIAL, VOL
	vctrl = VolumeControl.instance
	if VOLVOICE:
		vctrl.volctrl.setVolume(volume, volume)
		vctrl.volSave()
		if not INITIAL and config.plugins.sinric.viewvolbar.value:
			vctrl.volumeDialog.show()
		vctrl.volumeDialog.setValue(volume)
		vctrl.hideVolTimer.start(3000, True)
		VOL = volume
	INITIAL = False
	VOLVOICE = True
	return True, volume


def adjust_volume(device_id, volume):
	print('[SinriConnect] Adjust Volume to: ', volume)
	global VOLVOICE, INITIAL, VOL
	vctrl = VolumeControl.instance
	if volume != vctrl.volctrl.getVolume():
		vctrl.volctrl.setVolume(volume, volume)
		vctrl.volSave()
		VOL = volume
	if INITIAL:
		INITIAL = False
	elif config.plugins.sinric.viewvolbar.value:
		vctrl.volumeDialog.show()
	vctrl.volumeDialog.setValue(volume)
	vctrl.hideVolTimer.start(3000, True)
	VOLVOICE = True
	return True, volume


def set_Mute(device_id, mute):
	print('[SinriConnect] Change Mute to: ', mute)
	vctrl = VolumeControl.instance
	if not vctrl.volctrl.isMuted() and mute:
		vctrl.volMute()
	if vctrl.volctrl.isMuted() and not mute:
		vctrl.volMute()
	return True, mute


def media_control(device_id, control):
	print('[SinriConnect] Media control Key: ', control)
	remotetype = "dreambox remote control (native)"
	amap = eActionMap.getInstance()
	key = None
	if control == "Play" or control == "Pause":
		key = 164
	elif control == "Stop":
		key = 128
	elif control == "FastForward":
		key = 208
	elif control == "Rewind":
		key = 168

	if key:
		amap.keyPressed(remotetype, key, 0)
		amap.keyPressed(remotetype, key, 1)
		return True, control
	else:
		return False, control


def select_input(device_id, sinput):
	print('[SinriConnect]  input: ', sinput)
	from Screens.InfoBar import InfoBar
	sinput = sinput.lower()
	if "tuner" in sinput:
		try:
			if InfoBar and InfoBar.instance:
				InfoBar.instance.showRadio()
		except:
			pass
	elif "tv" in sinput:
		try:
			if InfoBar and InfoBar.instance:
				InfoBar.instance.showTv()
		except:
			pass
	elif "input" in sinput or "hdmi" in sinput:
		s = sinput.replace("input","").replace("hdmi","").replace(" ","")
		i = 0
		try:
			i = int(s)
		except:
			pass
		i = i-1
		if i>-1:
			if "input" in sinput:
				accion = config.plugins.sinric.input[i].accion.value
			elif "hdmi" in sinput:
				accion = config.plugins.sinric.hdmi[i].accion.value
		else:
			accion = "None"
		if accion == "epgdownload":
			#descarga epg
			try:
				from Plugins.Extensions.spazeMenu.spzPlugins.mhw2Timer.tstasker import tsTasker
				tsTasker.ejecuta(False)
			except:
				pass
		elif accion == "camdrestart":
			#reinicia camd
			if fileExists("/etc/.ActiveCamd") and fileExists("/etc/.CamdReStart.sh"):
				emuact = str(open('/etc/.ActiveCamd', "r").read())
				system("echo '' > /tmp/.spzCAMD")
				restartcam = system ('sh /etc/.CamdReStart.sh')
				try:
					from Plugins.Extensions.spazeMenu.Popup import Popup
					GSESSION.open(Popup, _("SinriConnect"),_("Restarting CAMD") + " " + emuact,type=Popup.TYPE_INFO, timeout = 5, picon=resolveFilename(SCOPE_PLUGINS)+"Extensions/SinriConnect/img/logo_sinric.png",enable_fade=True)
				except:
					pass
				if not fileExists("/tmp/.spzCAMD"):
					system("echo '' > /tmp/.spzCAMD")
		elif accion == "restart":
			#restart
			GSESSION.open(Standby.TryQuitMainloop, 3)
		elif accion == "reboot":
			#reboot
			GSESSION.open(Standby.TryQuitMainloop, 2)
		elif accion == "kodi":
			#kodi
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.py") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.pyc") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.so"):
				try:
					from Plugins.Extensions.Kodi.plugin import startLauncher
					startLauncher(GSESSION)
				except:
					pass
		elif accion == "info":
			#info
			try:
				if InfoBar and InfoBar.instance:
					InfoBar.instance.openEventView()
			except:
				pass
		elif accion == "epgchann":
			#Guia canal
			try:
				servicio=GSESSION.nav.getCurrentlyPlayingServiceReference()
				if servicio:
					from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSimple import spaEPGSelection
					GSESSION.open(spaEPGSelection,servicio)
			except:
				if InfoBar and InfoBar.instance:
					InfoBar.instance.showSingleEPG()
		elif accion == "exit":
			#exit
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 174, 0)
			amap.keyPressed(remotetype, 174, 1)
		elif accion == "up":
			#arriba
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 103, 0)
			amap.keyPressed(remotetype, 103, 1)
		elif accion == "down":
			#abajo
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 108, 0)
			amap.keyPressed(remotetype, 108, 1)
		elif accion == "left":
			#izquierda
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 105, 0)
			amap.keyPressed(remotetype, 105, 1)
		elif accion == "right":
			#derecha
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 106, 0)
			amap.keyPressed(remotetype, 106, 1)
		elif accion == "ok":
			#ok
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 352, 0)
			amap.keyPressed(remotetype, 352, 1)
		elif accion == "menu":
			#menu
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 139, 0)
			amap.keyPressed(remotetype, 139, 1)
		elif accion == "red":
			#rojo
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 398, 0)
			amap.keyPressed(remotetype, 398, 1)
		elif accion == "green":
			#verde
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 399, 0)
			amap.keyPressed(remotetype, 399, 1)
		elif accion == "yellow":
			#amarillo
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 400, 0)
			amap.keyPressed(remotetype, 400, 1)
		elif accion == "blue":
			#azul
			remotetype = "dreambox remote control (native)"
			amap = eActionMap.getInstance()
			amap.keyPressed(remotetype, 401, 0)
			amap.keyPressed(remotetype, 401, 1)
		elif accion == "guide":
			#guia
			try:
				from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.plugin import main
				servicelist = InfoBar.instance.servicelist
				main(GSESSION, servicelist)
			except:
				if InfoBar and InfoBar.instance:
					InfoBar.instance.showMultiEPG()
		elif accion == "script":
			#lanza script
			system("sh /usr/script/sinric.sh")
		elif accion == "epg_search":
			#cambia canal busqueda programada
			try:
				from Plugins.Extensions.spazeMenu.spzPlugins.spaTimerEntry.plugin import NextEvent
			except:
				NextEvent = None
			if NextEvent != None:
				if NextEvent[1] < 30:
					res = tipo = 0
					channel = None
					for x in NextEvent[2]:
						ch = channels()
						found = None
						for n in ch.services:

							if x in n[3].toString():
								found = n
								break

						if found != None:
							t = found[1]
							r = found[2]
							if tipos[t]>tipo:
								channel = found[3]
								tipo = tipos[t]
							if tipos[t]==tipo and resol[r]>res:
								channel = found[3]
								res=resol[r]
					if channel:
						GSESSION.nav.playService(channel)
					else:
						return False, sinput
			else:
				return False, sinput

	return True, sinput


def change_channel(device_id, channel_name=None, channel_number=None):
	if channel_name is None and channel_number is None:
		return False, "Unknown"
	ch = channels()
	if channel_number is None and channel_name is not None:
		if channel_name.isdigit():
			channel_number = int(channel_name)
	if channel_number is not None:
		print('[SinriConnect] Change Channel to: ', channel_number)
		channel, channel_name = ch.getNumber(channel_number)
		service = eServiceReference(channel)
		GSESSION.nav.playService(service)
		return True, str(channel_name)
	print('[SinriConnect] Change Channel to: ', channel_name)
	canales=ch.search(channel_name)
	tipo = res = 0
	channel = None
	for c in canales:
		t = c[1]
		r = c[2]
		if tipos[t]>tipo:
			channel = c
			tipo = tipos[t]
		if tipos[t]==tipo and resol[r]>res:
			channel = c
			res=resol[r]
	if not channel:
		return False, channel_name
	else:
		print('[SinriConnect] Change Channel Select is: ', channel[4])
		GSESSION.nav.playService(channel[3])
		return True, channel_name


def skip_channels(device_id, channel_count):
	print('[SinriConnect] Skip Channel: ', channel_count)
	from Screens.InfoBar import InfoBar
	if InfoBar and InfoBar.instance:
		if channel_count>0:
			for i in range(0,channel_count):
				InfoBar.instance.zapDown()
		else:
			n = channel_count*-1
			for i in range(0,n):
				InfoBar.instance.zapUp()
		return True, channel_count
	else:
		return False, channel_count


class CheckInit(Element):
	def __init__(self, func, session):
		Element.__init__(self)
		self.session = session
		self.func = func

	def changed(self, *args, **kwargs):
		val = self.source.boolean
		self.func(not val)


class sinriconnect():
	def __init__(self, session, key="", secret="", did="", log=False):
		global GSESSION, VOLVOICE
		self.key = key
		self.secret = secret
		self.tvid = did
		self.client = None
		self.loop = None
		self.log = log
		self.timer = eTimer()
		self.timer.callback.append(self.volvoice)
		self.timer2 = eTimer()
		self.timer2.callback.append(self.initilize)
		self.timer3 = eTimer()
		self.timer3.callback.append(self.closeloop)
		GSESSION = session
		VOLVOICE = True

		self.vctrl = VolumeControl.instance
		self.vol = -1
		self.volcontrol()
		self.timer4 = eTimer()
		self.timer4.callback.append(self.volcontrol)
		self.timer4.start(500,False)

		CheckInit(self.status, session).connect(session.screen["Standby"])


		self.callbacks = {
			'powerState': power_state,
			'setVolume': set_volume,
			'adjustVolume': adjust_volume,
			'mediaControl': media_control,
			'selectInput': select_input,
			'changeChannel': change_channel,
			'skipChannels': skip_channels,
			'setMute': set_Mute
		}

	def volcontrol(self):
		global VOLVOICE
		if VOL != self.vctrl.volctrl.getVolume():
			VOLVOICE = False
			self.volume(self.vctrl.volctrl.getVolume())

	def status(self, value):
		if self.isconnected():
			if value:
				self.client.event_handler.raiseEvent(self.tvid, 'setPowerState',data={'state': 'On'})
			else:
				self.client.event_handler.raiseEvent(self.tvid, 'setPowerState',data={'state': 'Off'})

	def volume(self, value):
		global VOLVOICE, VOL
		if VOLVOICE:
			VOLVOICE = False
		else:
			if self.isconnected():
				if VOL != self.vctrl.volctrl.getVolume():
					self.client.event_handler.raiseEvent(self.tvid, 'setVolume',data={'volume': value})
					VOL = self.vctrl.volctrl.getVolume()
				self.timer.start(2000,True)

	def volvoice(self):
		global VOLVOICE
		VOLVOICE = True
		self.timer.stop()

	def isconnected(self):
		ret = self.loop and self.loop.is_running() and self.client.socket.connection and self.client.socket.connection.open
		if ret==False and self.loop and self.loop.is_running():
			self.loop.stop()
			self.timer3.start(2000,True)
		return ret

	def closeloop(self):
		self.timer3.stop()
		try:
			self.loop.close()
		except:
			pass

	def run(self):
		global INITIAL
		INITIAL = True
		if len(self.secret)>0 and len(self.key)>0 and len(self.tvid)>0:
			self.loop = asyncio.get_event_loop()
			if self.loop: # and self.client:
				t = threading.Thread(target=self.connect)
				t.start()
				self.timer2.start(3000,True)

	def initilize(self):
		self.timer2.stop()
		if self.isconnected():
			vctrl = VolumeControl.instance
			vol = vctrl.volctrl.getVolume()
			self.status(not Standby.inStandby)
			self.volume(vol)

	def connect(self):
		self.client = SinricPro(self.key, [self.tvid], self.callbacks, enable_log=self.log, restore_states=False, secretKey=self.secret)
		self.loop.run_until_complete(self.client.connect())
