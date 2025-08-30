#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# In case of reuse of this source code please do not remove this copyright.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	For more information on the GNU General Public License see:
#	<http://www.gnu.org/licenses/>.
#
from . import _
from enigma import eTimer, eConsoleAppContainer
from Components.config import config
from Screens.MessageBox import MessageBox
from time import localtime, sleep, strftime, time
from Screens import Standby
from os import system, popen
from Screens.Console import Console
from Tools.Directories import fileExists


class timerScriptTasker:
	def __init__(self):
		self.restartTimer = eTimer()
		self.restartTimer.timeout.get().append(self.RestartTimerStart)
		self.checkCAMD = eTimer()
		self.checkCAMD.callback.append(self.checkstarted)

		self.minutes = 0
		self.timerActive = False
		self.oldService = None
		self.dormido = False

	def Initialize(self, session):
		self.session = session
		if config.plugins.spzCAMD.activar.value:
			self.restartTimer.start(60 * 1000, False)
		if config.plugins.spzCAMD.autorestart.value:
			self.checkCAMD.start(config.plugins.spzCAMD.restart_check.value*1000, False)

	def RestartTimerStart(self, initializing=False, postponeDelay=0):
		try:
			self.restartTimer.stop()
			self.timerActive = False

			lotime = localtime()
			wbegin = config.plugins.spzCAMD.restart_begin.value
			wend = config.plugins.spzCAMD.restart_end.value
			xtimem = lotime[3]*60 + lotime[4]
			ytimem = wbegin[0]*60 + wbegin[1]
			ztimem = wend[0]*60 + wend[1]
			if ytimem > ztimem:	ztimem += 12*60

			if postponeDelay > 0:
				self.restartTimer.start(postponeDelay * 60000, False)
				self.timerActive = True
				mints = postponeDelay % 60
				hours = postponeDelay / 60
				return

			minsToGo = ytimem - xtimem
			if xtimem > ztimem:	minsToGo += 24*60

			if initializing or minsToGo > 0:
				if minsToGo < 0:		# if initializing
					minsToGo += 24*60	# today's window already passed
				elif minsToGo == 0:
					minsToGo = 1
				self.restartTimer.start(minsToGo * 60000, False)
				self.timerActive = True
				self.minutes = minsToGo
				mints = self.minutes % 60
				hours = self.minutes / 60
			else:
				recordings = len(self.session.nav.getRecordings())
				next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
				if not recordings and (((next_rec_time - time()) > 360) or next_rec_time < 0):
					self.InitRestart()
				else:
					self.minutes = 15
					self.restartTimer.start(15*60*1000, False)
					self.timerActive = True
		except Exception:
			print("[spzCAMD] RestartTimerStart exception:\n")
			self.RestartTimerStart(True, 30)

	def lanzare(self):
		self.LaunchRestart(True)	# no need to query if in standby mode

	def InitRestart(self):
		if Standby.inStandby:
			self.dormido = True
			self.TimerTemp = eTimer()
			self.TimerTemp.callback.append(self.lanzare)
			self.TimerTemp.startLongTimer(7)
		else:
			# query from the user if it is ok to restart now
			self.dormido = False
			cam = config.plugins.spzCAMD.camd.value
			stri = _("Restart CAMD: "+cam+"?\n Select no to postpone by 30 minutes.")
			self.session.openWithCallback(self.LaunchRestart, MessageBox, stri, MessageBox.TYPE_YESNO, timeout = 30)

	def callback(self, retval):
		self.Initialize(self.session)

	def reinicioCB(self,retval):
		if (retval):
			self.TimerTemp = eTimer()
			self.TimerTemp.callback.append(self.reinicioA)
			self.TimerTemp.startLongTimer(2)

	def ejecuta(self):
		if fileExists("/etc/.CamdReStart.sh") is True :
			system("sh /etc/.CamdReStart.sh")
			cam = config.plugins.spzCAMD.camd.value
			self.session.openWithCallback(self.callback, MessageBox, _("Restart Camd: "+cam+"..."), type = 1, timeout = 9)

	def LaunchRestart(self, confirmFlag=True):
		if confirmFlag:
			# this means that we're going to be re-instantiated after Enigma has restarted
			self.TimerTemp = eTimer()
			self.TimerTemp.callback.append(self.ejecuta)
			self.TimerTemp.startLongTimer(4)
		else:
			self.RestartTimerStart(True, 30)

	def ShowAutoRestartInfo(self):
		# call the Execute/Stop function to update minutes
		if config.plugins.spzCAMD.activar.value:
			self.RestartTimerStart(True)
		else:
			self.RestartTimerStop()

		if self.timerActive:
			mints = self.minutes % 60
			hours = self.minutes / 60

		if config.plugins.spzCAMD.autorestart.value and fileExists("/tmp/.spzCAMD"):
			self.checkCAMD.stop()
			self.checkCAMD.start(config.plugins.spzCAMD.restart_check.value*1000, False)
		else:
			self.checkCAMD.stop()

	def checkstarted(self):
		if fileExists("/etc/.BinCamd") and fileExists("/etc/.CamdReStart.sh") and fileExists("/tmp/.spzCAMD"):
			caido = False
			ebin = open("/etc/.BinCamd","r").read().split()
			for e in ebin:
				check = popen("pidof "+e).read()
				if check == "":
					caido = True
					open("/tmp/spzCAMD.log","a").write(strftime("%d/%m/%y %H:%M:%S") + " " + e + " " + _("not working") + "\n")

			if fileExists("/tmp/sbox.log"):
				log = popen("grep 'Broken pipe' /tmp/sbox.log").read()
				log2 = popen("grep 'no card inserted' /tmp/sbox.log").read()
				if len(log)>0 or len(log2)>0:
					open("/tmp/spzCAMD.log","a").write(strftime("%d/%m/%y %H:%M:%S") + " [Broken pipe] sbox " + _("not working") + "??\n")
					caido = True

			if caido:
				system("sh /etc/.CamdReStart.sh")
				try:
					clist = open("/etc/.ActiveCamd", "r")
				except:
					pass

				lastcam = None
				if not clist is None:
					for line in clist:
						lastcam = line
					clist.close()
				try:
					open("/tmp/spzCAMD.log","a").write(strftime("%d/%m/%y %H:%M:%S") + " " + _("Start Camd:")+ " " + str(lastcam) + "\n")
				except:
					pass

	def RestartTimerStop(self):
		self.restartTimer.stop()
		self.timerActive = False
		self.minutes = 0

tsTasker = timerScriptTasker()
