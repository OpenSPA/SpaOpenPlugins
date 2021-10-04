# -*- coding: utf-8 -*-
# PermanentEvent converter code by Villak OpenSPA Team for PermanentEvent 2021
# <widget source="session.CurrentService" render="Label" position="0,0" size="700,100" >
# <convert type="SpaPrimeTime" /> 
# </widget>

from enigma import eEPGCache, eServiceReference, iPlayableServicePtr
from Components.Converter.Converter import Converter
from Components.Element import cached
from time import localtime, mktime, time
from datetime import datetime
from Components.config import config
import re

class SpaPrimeTime(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.epgcache = eEPGCache.getInstance()

	@cached
	def getText(self):
		service = self.source.service
		info = None
		if isinstance(service, eServiceReference):
			info = self.source.info
		elif isinstance(service, iPlayableServicePtr):
			info = service and service.info()
			service = None
		if not info:
			return ""

		event = self.source.event
		if event is None:
			self.text = ""
			return
		service = self.source.serviceref
		if self.epgcache is not None:
			result = _('LOAD THE EPG FIRST\nNO EPG PRIMETIME ON CHANNEL')
			evt = self.epgcache.lookupEvent(['IBDCT', (service.toString(), 0, -1, -1)])
#			print 'EVENTOS: ', evt
		if evt:
			now = localtime(time())
#			print 'hora actual: ', now
			try:
				hour,minute = config.plugins.PermanentEvent_primetimehour.value,config.plugins.PermanentEvent_primetimemins.value
			except:
				hour,minute = 22,00
			dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, hour, minute)
#			print 'hora busqueda: ', dt
			primetime = int(mktime(dt.timetuple()))
			next = False
			tomorrow = False
			for x in evt:
				if x[4]:
					begin = x[1]
					end = x[1]+x[2]
					if begin <= primetime and end > primetime or next:
						if not next and end <= primetime + 1200: # 20 mins tolerance to starting next event
							next = True
							continue
						t = localtime(begin)
						text= _("Tonight at... ")
						result = text +"%02d:%02d \n%s" % (t[3], t[4], x[4])
#						print('[PermanentEvent]PRIMETIME HOY: ', result)
						break
					if begin > primetime and end > primetime or tomorrow: # entry > primetime ? -> primetime not in epg
						if not next and end <= primetime + 87840: # 24 and 20 mins hours to starting next event
							tomorrow = True
							continue
						t = localtime(begin)
						texto= _("Tomorrow at... ")
						result = texto +"%02d:%02d \n%s" % (t[3], t[4], x[4])
#						print('[PermanentEvent]PRIMETIME TOMORROU: ', result)
						break
		print('[PermanentEvent]', result)
		return result

	text = property(getText)
	def changed(self, changedvalue):
			Converter.changed(self, changedvalue)
