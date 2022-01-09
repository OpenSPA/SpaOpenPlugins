# -*- encoding: utf-8 -*-

from . import _, esHD, py3
import xml.etree.ElementTree as ET
if py3():
	import urllib.request, urllib.error, urllib.parse, base64
	from urllib.parse import quote
else:
	import urllib2, base64
	from urllib import quote
from enigma import eEPGCache, eConsoleAppContainer, eTimer, eDVBDB, eServiceCenter, eServiceReference
from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.ProgressBar import ProgressBar
from Components.config import config
from Screens.MessageBox import MessageBox
from os import remove, listdir
from Tools.Directories import fileExists,SCOPE_CURRENT_SKIN, resolveFilename

class DownloadComponent:
	EVENT_DOWNLOAD = 0
	EVENT_DONE = 1
	EVENT_ERROR = 2

	def __init__(self, n, ref, name, target):
		self.cmd = eConsoleAppContainer()
		self.cache = None
		self.name = None
		self.data = None
		self.number = n
		self.ref = ref
		self.name = name
		self.target = target
		self.callbackList = []

	def startCmd(self, cmd, filename = None):
		rute = 'wget'
		if filename:
			rute = rute + ' -O '+filename
			self.filename = filename
		else:
			self.filename = cmd.split('/')[-1]
		
		rute = rute + ' ' + cmd
		self.runCmd(rute)

	def runCmd(self, cmd):
		print("executing", cmd)
		self.cmd.appClosed.append(self.cmdFinished)
		self.cmd.dataAvail.append(self.cmdData)
		if self.cmd.execute(cmd):
			self.cmdFinished(-1)

	def cmdFinished(self, retval):
		if fileExists(self.filename):
			self.data = open(self.filename).read()
			remove(self.filename)
		else:
			self.data = None
		self.callCallbacks(self.EVENT_DONE, self.number, self.data, self.ref, self.name, self.target)
		self.cmd.appClosed.remove(self.cmdFinished)
		self.cmd.dataAvail.remove(self.cmdData)


	def cmdData(self, data):
		if py3():
			data = data.decode('utf-8')
		if self.cache is None:
			self.cache = data
		else:
			self.cache += data

		if '\n' in data:
			splitcache = self.cache.split('\n')
			if self.cache[-1] == '\n':
				iteration = splitcache
				self.cache = None
			else:
				iteration = splitcache[:-1]
				self.cache = splitcache[-1]
			for mydata in iteration:
				if mydata != '':
					self.parseLine(mydata)

	def parseLine(self, data):
		try:
			if data.startswith(self.name):
				self.callCallbacks(self.EVENT_DOWNLOAD, data.split(' ', 5)[1].strip())
			elif data.startswith('An error occurred'):
				self.callCallbacks(self.EVENT_ERROR, None)
			elif data.startswith('Failed to download'):
				self.callCallbacks(self.EVENT_ERROR, None)
		except Exception as ex:
			print("Failed to parse: '%s'" % data)

	def callCallbacks(self, event, param = None, data = None, ref = None, name = None, target=None):
		for callback in self.callbackList:
			callback(event, param, data, ref, name, target)

	def addCallback(self, callback):
		self.callbackList.append(callback)

	def removeCallback(self, callback):
		self.callbackList.remove(callback)


class EPGdownload(Screen):
	if esHD():
		skin = """
		<screen name="EPGdownload" position="60,60" size="615,195" title="RemoteChannels EPG Download" flags="wfNoBorder" backgroundColor="#ff000000">
		<ePixmap name="background" position="0,0" size="615,195" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/backgroundHD.png" zPosition="-1" alphatest="off" />
		<widget name="picon" position="15,55" size="120,80" transparent="1" noWrap="1" alphatest="blend"/>
		<widget name="action" halign="left" valign="center" position="13,9" size="433,30" font="Regular;25" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>
		<widget name="progress" position="150,97" size="420,12" borderWidth="0" backgroundColor="#1143495b" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/progresoHD.png" zPosition="2" alphatest="blend" />
		<eLabel name="fondoprogreso" position="150,97" size="420,12" backgroundColor="#102a3b58" />
		<widget name="espera" valign="center" halign="center" position="150,63" size="420,30" font="Regular;22" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>
		<widget name="status" halign="center" valign="center" position="150,120" size="420,30" font="Regular;24" foregroundColor="#ffffff" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>
		</screen>"""
	else:
		skin = """
		<screen name="EPGdownload" position="40,40" size="410,130" title="RemoteChannels EPG Download" flags="wfNoBorder" backgroundColor="#ff000000">
		<ePixmap name="background" position="0,0" size="410,130" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/background.png" zPosition="-1" alphatest="off" />
		<widget name="picon" position="10,36" size="80,53" transparent="1" noWrap="1" alphatest="blend"/>
		<widget name="action" halign="left" valign="center" position="9,6" size="289,20" font="Regular;17" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>
		<widget name="progress" position="100,65" size="280,8" borderWidth="0" backgroundColor="#1143495b" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/progreso.png" zPosition="2" alphatest="blend" />
		<eLabel name="fondoprogreso" position="100,65" size="280,8" backgroundColor="#102a3b58" />
		<widget name="espera" valign="center" halign="center" position="100,42" size="240,20" font="Regular;15" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>
		<widget name="status" halign="center" valign="center" position="100,80" size="240,20" font="Regular;16" foregroundColor="#ffffff" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>
		</screen>"""

	def __init__(self, session, args = "" ):
		self.session = session
		Screen.__init__(self, session)
		self.iprogress = 0
		self.total = 0
		self.skinName = "mhwEPG"
		self["progress"] = ProgressBar()
		self["progress"].setValue(0)
		self["action"] = Label(_("EPG Download: %s Remote Channels") % args)
		self["espera"] = Label("")
		self["status"] = Label(_("Wait..."))
		self["actions"] = ActionMap(["OkCancelActions"], {"cancel": self.salir}, -1)
		self["picon"] = Pixmap()
		self.epgcache = eEPGCache.getInstance()
		self.fd = None
		self.state = 1
		self.onFirstExecBegin.append(self.download)

	def download(self):
		try:
			fd = listdir("/etc/enigma2")
		except:
			return

		self.fd = []
		for f in fd:
			if f.startswith("userbouquet.remote") and not f.endswith(".del"):
				l = open("/etc/enigma2/"+f,"r").readlines()
				ip = port = user = password = auth = name = service = stype = streamport = streamaut = None
				data = name = None
				isok = False
				for line in l:
					if line.startswith("#NAME"):
						try:
							name = line.split()[1]
						except:
							name = None
					if line.startswith("#SERVICE 1:576:"):
						y = line.split(":")[-1]
						z = y.split("|")
						isok = True
						if len(z) > 4:
							ip = z[0]
							port = int(z[1])
							user = z[2]
							password = z[3]
							auth =  int(z[4])
							try:
								stype = z[5]
							except:
								stype = config.plugins.RemoteStreamConverter.servicestype.value
							try:
								streamport = int(z[6])
							except:
								streamport = config.plugins.RemoteStreamConverter.Streamport.value
							try:
								streamaut = int(z[7])
							except:
								streamaut = int(config.plugins.RemoteStreamConverter.Streamauthentication.value)
							data = "%s|%d|%s|%s|%d|%s|%d|%d" % (ip,port,user,password,auth,stype,streamport,streamaut)
					if line.find('http')>0:
						break

				if name and data:
					self.fd = createBouquetFile(f,name,data,self.fd)


		db = eDVBDB.getInstance()
		db.reloadServicelist()
		db.reloadBouquets()

		self.total = len(self.fd)
		self.actualizaprogreso(event=DownloadComponent.EVENT_DONE, param=0)

	def actualizaprogreso(self, event=None, param=None, data=None, ref=None, name=None, ref_target=None):
		####### hack for exit before end
		cont = False
		try:
			if self.state == 1:
				cont = True
		except:
			pass
		#################################
		if cont:
			if data and ref and name and ref_target:
				#pos = ref.find(":")
				#ref_target = "4097"+ref[pos:]
				#ref_target = ref_target + quote("http://192.168.0.30:8001/"+ref[:-1])+":"+name
				self.parse_channel(data, ref_target)

			if event == DownloadComponent.EVENT_DONE:
				try:
					self.iprogress = ((param+1) *100) // self.total
				except:
					self.iprogress=100
				if self.iprogress > 100:
					self.iprogress = 100

				self["progress"].setValue(self.iprogress)
				self["espera"].setText(str(self.iprogress)+" %")
				if self.fd:
					if param<self.total:
						channel = self.fd[param]
						ip = channel[0]
						port = channel[1]
						if port != 80:
							ip = ip+":"+str(port)
						user = channel[2]
						password = channel[3]
						auth = channel[4]
						if auth == 1:
							ip = user+":"+password+"@"+ip
						ref = channel[5]
						name = channel[6]
						self["status"].setText(_("Wait for Channel: ")+name)

						try:
							from Components.Renderer import spaPicon
						except:
							from Components.Renderer import Picon as spaPicon
						pngname = spaPicon.getPiconName(ref)
						if not fileExists(pngname):
							pngname = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")

						try:
							if fileExists(pngname):
								self["picon"].instance.setScale(1)
								self["picon"].instance.setPixmapFromFile(pngname)
						except:
							pass

						ref_target = channel[7]
						self.down = DownloadComponent(param+1, ref, name, ref_target)
						self.down.addCallback(self.actualizaprogreso)
						try:
							last_day = int(config.epg.maxdays.value) * 24 * 60
						except:
							last_day = 9999999

						self.down.startCmd("http://"+ip+"/web/epgservice?sRef="+ref+"&endTime="+str(last_day), '/tmp/xml')
					else:
						self.close()
				else:
					self.TimerTemp = eTimer()
					self.TimerTemp.callback.append(self.salirok)
					self.TimerTemp.startLongTimer(1)

	def parse_channel(self, xml, ref_target):
		events = []

		print("Load epg for service %s" % ref_target)
		try:
			ch_epg = ET.fromstring(xml)
		except:
			ch_epg = []
		for event in ch_epg:
			start = 0
			duration = 0
			title = ""
			description = ""
			extended = ""
			channel = ""
			name = ""
			for child in event:
				if child.tag == "e2eventstart":
					start = int(child.text)
				if child.tag == "e2eventduration":
					duration = int(child.text)
				if child.tag == "e2eventtitle":
					title = child.text
					if title == None:
						title = ""
					if not py3():
						title = title.encode("utf-8")
				if child.tag == "e2eventdescription":
					description = child.text
					if description == None:
						description = ""
					if not py3():
						description = description.encode("utf-8")
				if child.tag == "e2eventdescriptionextended":
					extended = child.text
					if extended == None:
						extended = ""
					if not py3():
						extended = extended.encode("utf-8")
			events.append((start,duration,title,description,extended,0))
		if len(events)>0:
			iterator = iter(events)
			events_tuple = tuple(iterator)
			self.epgcache.importEvents(ref_target,events_tuple)

	def salir(self):
			stri = _("The download is in progress. Exit now?")
			self.session.openWithCallback(self.salirok, MessageBox, stri, MessageBox.TYPE_YESNO, timeout = 30)
			
	def salirok(self,answer=True):
		if answer:
			self.close(True) 

def addBouquet(bouquet, name):
	if config.usage.multibouquet.value:
		bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
	else:
		bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(service_types_tv)
	bouquet_root = eServiceReference(bouquet_rootstr)
	serviceHandler = eServiceCenter.getInstance()
	mutableBouquetList = serviceHandler.list(bouquet_root).startEdit()
	if mutableBouquetList:
		str = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"'+bouquet+'\" ORDER BY bouquet'
		new_bouquet_ref = eServiceReference(str)
		if not mutableBouquetList.addService(new_bouquet_ref):
			mutableBouquetList.flushChanges()
			eDVBDB.getInstance().reloadBouquets()
			mutableBouquet = serviceHandler.list(new_bouquet_ref).startEdit()
			if mutableBouquet:
				mutableBouquet.setListName(name)
				mutableBouquet.flushChanges()
			else:
				print("get mutable list for new created bouquet failed")

def createBouquetFile(bouquet, name, data, lista):
	line = "1:576:0:0:0:0:0:0:0:0::%s" % data
	content = "#NAME %s\n#SERVICE %s\n#DESCRIPTION marker for Remote Bouquet\n" % (name, line)
	z = data.split("|")
	if len(z) > 4:
		ip = z[0]
		port = int(z[1])
		user = z[2]
		password = z[3]
		auth =  int(z[4])
		try:
			stype = z[5]
		except:
			stype = config.plugins.RemoteStreamConverter.servicestype.value
		try:
			streamport = int(z[6])
		except:
			streamport = config.plugins.RemoteStreamConverter.Streamport.value
		try:
			streamaut = int(z[7])
		except:
			streamaut = int(config.plugins.RemoteStreamConverter.Streamauthentication.value)
		ip1=ip
		if port != 80:
			ip1 = ip1+":"+str(port)
		url = 'http://%s/web/getservices?sRef=1:7:1:0:0:0:0:0:0:0:' % ip1 + quote('FROM BOUQUET "%s" ORDER BY bouquet' % bouquet.replace("remote_",""))
		html = None

		print("url: ", url)
		if auth == 1:
			if py3():
				request = urllib.request.Request(url)
			else:
				request = urllib2.Request(url)

			data = "%s:%s" % (user,password)
			if py3():
				b64auth = base64.standard_b64encode(data.encode('ascii'))
				request.add_header("Authorization", "Basic " + b64auth.decode('ascii'))
			else:
				b64auth = base64.standard_b64encode(data)
				request.add_header("Authorization", "Basic %s" % b64auth)
		else:
			request = url

		print("request: ", str(request))
		try:
			if py3():
				html = urllib.request.urlopen(request).read()
			else:
				html = urllib2.urlopen(request).read()

		except:
			html = None

		ch_epg = []
	
		if html:
			try:
				ch_epg = ET.fromstring(html)
			except:
				ch_epg = []
		if len(ch_epg) > 0:
			for e2service in ch_epg:
				for child in e2service:
					if child.tag == "e2servicereference":
						if py3():
							service = child.text
						else:
							service = child.text.encode("utf-8")
						n=service.find(':')
						if n>-1:
							tag2 = stype+service[n:-1]
						else:
							tag2 = service

					if child.tag == "e2servicename":
						if py3():
							name = child.text
						else:
							name = child.text.encode("utf-8")
				ip1=ip
				if streamaut == 1:
					ip1 = user+":"+password+"@"+ip1
				typech = service.split(":")[1]
				blacklist = ["832","64","320"]
				if typech in blacklist:
					target = tag2 + "\n#DESCRIPTION " + name
				else:
					target = tag2 + ":" + quote('http://' + ip1 + ":" + str(streamport) + '/' + tag2) + ':' + name
				content = content + '#SERVICE ' + target + '\n'
				if ip and port and user and password and name and service and target and typech not in blacklist:
					lista.append((ip,port,user,password,auth,service,name,target))
				open("/etc/enigma2/"+bouquet,"w").write(content)

	return lista
				
