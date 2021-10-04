# -*- coding: utf-8 -*-
# by digiteng...07.2020 - 08.2020 Adapted by Villak OpenSPA Team for PermanentEvent 2021
# <widget source="session.Event_Now" or "session.Event_Next" render="SpaBackdrop" position="0,0" size="300,170" zPosition="1" />

from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG
from Components.config import config
import os, re, json

try:
	pathLoc = config.plugins.PermanentEvent.loc.value
except:
	pass

class SpaBackdrop(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.delayPicTime = 100
		self.timer = eTimer()
		self.timer.callback.append(self.showPicture)

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for attrib, value in self.skinAttributes:
			if attrib == 'delayPic':
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
		evnt = ''
		pstrNm = ''
		evntNm = ''
		try:
			event = self.source.event
			if event:
				evnt = event.getEventName()
				evntNm = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", evnt).rstrip()
				self.evntNm = evntNm
#				print('EVENTO:', self.evntNm)
				pstrNm = "{}PermanentEvent/backdrop/{}.jpg".format(pathLoc, evntNm)
				print ('[PermanentEvent]RUTA IMAGEN EVENTO:', pstrNm)
				if os.path.exists(pstrNm):
					self.instance.setPixmap(loadJPG(pstrNm))
					self.instance.setScale(2)
					self.instance.show()
				else:
					nopstrNm = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/images/event.jpg"
					print ('[PermanentEvent]IMG NO ENCONTRADA, IMG POR DEFECTO...' , nopstrNm )
					self.instance.setPixmap(loadJPG(nopstrNm))
					self.instance.setScale(2)
					self.instance.show()
			else:
				self.instance.hide()
		except:
			pass
