# -*- coding: utf-8 -*-
# by digiteng...07.2020 - 08.2020 Adapted by Villak OpenSPA Team for PermanentEvent 2021
# <widget source="session.CurrentService" render="SpaPrimeTimeBackdrop" position="0,0" size="300,170" zPosition="1"

from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, eEPGCache, eServiceReference, iPlayableServicePtr, loadJPG
from Components.config import config
from time import localtime, mktime, time
from datetime import datetime
import os, re, json

try:
	pathLoc = config.plugins.PermanentEvent.loc.value
except:
	pass

class SpaPrimeTimeBackdrop(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.delayPicTime = 100
		self.timer = eTimer()
		self.timer.callback.append(self.showPicture)
		self.epgcache = eEPGCache.getInstance()

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for attrib, value in self.skinAttributes:
			if attrib == 'delayPic':          # delay time(ms) for backdrop showing...
				self.delayPicTime = int(value)
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap
	def changed(self, what):
#		if not self.instance:
#			return
#		else:
		if what[0] != self.CHANGED_CLEAR:
			self.timer.start(self.delayPicTime, True)

	def showPicture(self):
		service = self.source.service
		info = None
		if isinstance(service, eServiceReference):
			info = self.source.info
		elif isinstance(service, iPlayableServicePtr):
			info = service and service.info()
			service = None
		if not info:
			return ""
		primeNm = ""
		try:
			service = self.source.serviceref
			if self.epgcache is not None:
				result = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/images/primetime.jpg"
				self.instance.setPixmap(loadJPG(result))
				self.instance.setScale(2)
				self.instance.show()
				evt = self.epgcache.lookupEvent(['IBDCT', (service.toString(), 0, -1, -1)])
#				print ('EVENTOS: ', evt)
			if evt:
				now = localtime(time())
#				print ('HORA ACTUAL: ', now)
				hour,minute = config.plugins.PermanentEvent_primetimehour.value,config.plugins.PermanentEvent_primetimemins.value
				dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, hour, minute)
#				print ('HORA EVENTO PRIMETIME: ', dt)
				primeNm = int(mktime(dt.timetuple()))
				next = False
				tomorrow = False
				for x in evt:
					if x[4]:
						begin = x[1]
						end = x[1]+x[2]
						if begin <= primeNm and end > primeNm or next:
							if not next and end <= primeNm + 1200: # 20 mins tolerance to starting next event
								next = True
								continue
							t = localtime(begin)
							primeimg = "%s" % (x[4])
#							print ('HOY NOMBRE EVENTO: ', primeimg)
							break
						if begin > primeNm and end > primeNm or tomorrow: # entry > primetime ? -> primetime not in epg
							if not next and end <= primeNm + 87840: # 24 and 20 mins hours to starting next event
								tomorrow = True
								continue
							t = localtime(begin)
							primeimg ="%s" % (x[4])
#							print ('TOMORROU NOMBRE EVENTO: ', primeimg)
							break
				primeimg = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", primeimg).rstrip()
				result = "{}PermanentEvent/backdrop/{}.jpg".format(pathLoc, primeimg.strip())
				print ('[PermanentEvent]RUTA IMAGEN PRIMETIME:', result)
				if os.path.exists(result):
					self.instance.setPixmap(loadJPG(result))
					self.instance.setScale(2)
					self.instance.show()
				else:
					nopstrNm = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/images/primetime.jpg"
					print ('[PermanentEvent]IMG NO ENCONTRADA, IMG POR DEFECTO...' , nopstrNm )
					self.instance.setPixmap(loadJPG(nopstrNm))
					self.instance.setScale(2)
					self.instance.show()
		except:
			print('[PermanentEvent]NO EPG, IMG POR DEFECTO')
			pass
