from sinricpro import SinricPro, SinricProTV, SinricProConfig, SinricProLogger, LogLevel
from sinricpro.core.types import SinricProRequest

import asyncio
#import threading
from Components.Element import Element
from Screens import Standby
from Components.VolumeControl import VolumeControl
from Tools import Notifications
from Components.config import config
from .channels import channels
from enigma import eActionMap, eServiceReference, iServiceInformation, eTimer, eDVBVolumecontrol
from os import system
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from ServiceReference import ServiceReference
from Screens.InfoBar import InfoBar

tipos = {"DVB-T":4, "DVB-C":3, "DVB-S":2,"IPTV":1}
resol = {"UHD":3, "HD":2, "SD":1}

class CheckInit(Element):
	def __init__(self, func, session, loop):
		Element.__init__(self)
		self.session = session
		self.func = func
		self.loop = loop

	def changed(self, *args, **kwargs):
		val = self.source.boolean
		self.loop.create_task(self.func(not val))


class sinriconnect():
	def __init__(self, session, key="", secret="", did="", log=False):
		self.key = key
		self.secret = secret
		self.tvid = did
		self.client = SinricPro.get_instance()
		self.loop = None
		self.oldMute = False
		self.timer = eTimer()
		self._vol_task = None
		self.session = session
		
		self.client.on_connected(self.onconnect)
		self.client.on_disconnected(self.ondisconnect)

		if log:	
			SinricProLogger.set_level(LogLevel.DEBUG)
		else:
			SinricProLogger.set_level(LogLevel.INFO)
		

		# Create TV device
		self.my_tv = SinricProTV(self.tvid)

		# Register callbacks
		self.my_tv.on_power_state(self.power_state)
		self.my_tv.on_volume(self.set_volume)
		self.my_tv.on_adjust_volume(self.adjust_volume)
		self.my_tv.on_mute(self.set_Mute)
		self.my_tv.on_change_channel(self.change_channel)
		self.my_tv.on_skip_channels(self.skip_channels)
		self.my_tv.on_select_input(self.select_input)
		self.my_tv.on_media_control(self.media_control)

		# Add device to SinricPro
		self.client.add(self.my_tv)

		# Configure and connect
		self.config = SinricProConfig(
			app_key=self.key,
			app_secret=self.secret
		)

		self.vctrl = VolumeControl.instance
		self.vol = -1

	async def power_state(self, state):
		print('[SinriConnect] Change Power State to: ', state)
		if state and Standby.inStandby:
			Standby.inStandby.Power()
		elif not state and not Standby.inStandby:
			Notifications.AddNotification(Standby.Standby)
		return True

	async def media_control(self, control):
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
			return True
		else:
			return False


	async def set_volume(self, volume):
		print('[SinriConnect] Set Volume to: ', volume)
		self.vctrl.volctrl.setVolume(volume, volume)
		self.vctrl.volSave()
		if config.plugins.sinric.viewvolbar.value:
			self.vctrl.volumeDialog.show()
		self.vctrl.volumeDialog.setValue(volume)
		self.vctrl.hideVolTimer.start(3000, True)
		self.vol = volume
		return True

	async def adjust_volume(self, volume_delta):
		volume = max(0, min(100, self.vctrl.volctrl.getVolume() + volume_delta))
		print('[SinriConnect] Adjust Volume to: ', volume)
		self.vctrl.volctrl.setVolume(volume, volume)
		self.vctrl.volSave()
		self.vol = volume
		if config.plugins.sinric.viewvolbar.value:
			self.vctrl.volumeDialog.show()
		self.vctrl.volumeDialog.setValue(volume)
		self.vctrl.hideVolTimer.start(3000, True)
		await self.client.get(self.tvid).send_event('setVolume',{'volume': volume})
		return True

	async def set_Mute(self,mute):
		print('[SinriConnect] Change Mute to: ', mute)
		if not self.vctrl.volctrl.isMuted() and mute:
			self.vctrl.volMute()
		if self.vctrl.volctrl.isMuted() and not mute:
			self.vctrl.volMute()
		self.oldMute = mute
		return True

	async def change_channel(self, channel=None):
		channel_name = channel.get("name")
		channel_number = channel.get("number")
		if channel_name is None and channel_number is None:
			return False
		ch = channels()
		if channel_number is None and channel_name is not None:
			if channel_name.isdigit():
				channel_number = int(channel_name)
		if channel_number is not None:
			print('[SinriConnect] Change Channel to: ', channel_number)
			channel, channel_name = ch.getNumber(channel_number)
			service = eServiceReference(channel)
			self.session.nav.playService(service)
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
			self.session.nav.playService(channel[3])
			return True


	async def skip_channels(self, channel_count):
		print('[SinriConnect] Skip Channel: ', channel_count)
		if InfoBar and InfoBar.instance:
			if channel_count>0:
				for i in range(0,channel_count):
					InfoBar.instance.zapDown()
			else:
				n = channel_count*-1
				for i in range(0,n):
					InfoBar.instance.zapUp()
			return True
		else:
			return False

	async def select_input(self, sinput):
		print('[SinriConnect]  input: ', sinput)
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
						self.session.open(Popup, _("SinriConnect"),_("Restarting CAMD") + " " + emuact,type=Popup.TYPE_INFO, timeout = 5, picon=resolveFilename(SCOPE_PLUGINS)+"Extensions/SinriConnect/img/logo_sinric.png",enable_fade=True)
					except:
						pass
					if not fileExists("/tmp/.spzCAMD"):
						system("echo '' > /tmp/.spzCAMD")
			elif accion == "restart":
				#restart
				self.session.open(Standby.TryQuitMainloop, 3)
			elif accion == "reboot":
				#reboot
				self.session.open(Standby.TryQuitMainloop, 2)
			elif accion == "kodi":
				#kodi
				if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.py") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.pyc") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.so"):
					try:
						from Plugins.Extensions.Kodi.plugin import startLauncher
						startLauncher(self.session)
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
					servicio=self.session.nav.getCurrentlyPlayingServiceReference()
					if servicio:
						from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSimple import spaEPGSelection
						self.session.open(spaEPGSelection,servicio)
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
					main(self.session, servicelist)
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
							self.session.nav.playService(channel)
						else:
							return False
				else:
					return False
		return True

	def onconnect(self):
		print("[sinriconnect] Device Connected")
		self.loop = asyncio.get_event_loop()
		CheckInit(self.status, self.session, self.loop).connect(self.session.screen["Standby"])
		self.timer.callback.append(self._onVolTimer)
		self.timer.start(500,False)
		
	def ondisconnect(self):
		print("[sinriconnect] Device Disconnected")
		
	def _onVolTimer(self):
		if self._vol_task and not self._vol_task.done():
			return

		self._vol_task = self.loop.create_task(
			self.volcontrol()
		)

	async def volcontrol(self):
		current = self.vctrl.volctrl.getVolume()
		if current != self.vol:
			await self.volume(current)
			self.vol = current

	async def status(self, value):
		if self.isconnected():
			if value:
				await self.client.get(self.tvid).send_event('setPowerState',{'state': 'On'})
			else:
				await self.client.get(self.tvid).send_event('setPowerState',{'state': 'Off'})

	async def volume(self, value):
		if self.isconnected():
			await self.client.get(self.tvid).send_event('setVolume',{'volume': value})

	def isconnected(self):
		return self.client.is_connected if self.client else False

	async def run(self):
		if len(self.secret)>0 and len(self.key)>0 and len(self.tvid)>0:
			await self.client.begin(self.config)
			# Keep the application running
			while True:
				await asyncio.sleep(1)

