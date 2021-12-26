from . import _, py3, esHD
from enigma import eTimer, ePythonMessagePump
from .MyTubeService import GoogleSuggestions
from Screens.Screen import Screen
from Screens.LocationBox import MovieLocationBox
from Components.config import config, ConfigText, getConfigListEntry
from Components.config import KEY_DELETE, KEY_BACKSPACE, KEY_ASCII, KEY_TIMEOUT
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText 
from Components.Task import job_manager
from Tools.Directories import resolveFilename, SCOPE_HDD
from Screens.InputBox import PinInput

from threading import Thread
from .ThreadQueue import ThreadQueue
from xml.etree.cElementTree import fromstring as cet_fromstring
from io import StringIO
if py3():
	from urllib.request import FancyURLopener
else:
	from urllib import FancyURLopener

#added by openspa
from .skinsmytube import *
from .skinsmytubeHD import *

def rutaskin(nombre):
    if esHD():
        nombre=nombre+'HD'
    return nombre    

class MyOpener(FancyURLopener):
	version = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12'

class SuggestionsQueryThread(Thread):
	def __init__(self, query, param, callback, errorback):
		Thread.__init__(self)
		self.messagePump = ePythonMessagePump()
		self.messages = ThreadQueue()
		self.query = query
		self.param = param
		self.callback = callback
		self.errorback = errorback
		self.canceled = False
		self.messagePump.recv_msg.get().append(self.finished)

	def cancel(self):
		self.canceled = True

	def run(self):
		if self.param not in (None, ""):
			try:
				suggestions = self.query.getSuggestions(self.param)
				self.messages.push((suggestions, self.callback))
				self.messagePump.send(0)
			except Exception as ex:
				self.messages.push((ex, self.errorback))
				self.messagePump.send(0)

	def finished(self, val):
		if not self.canceled:
			message = self.messages.pop()
			message[1](message[0])

class ConfigTextWithGoogleSuggestions(ConfigText):
	def __init__(self, default = "", fixed_size = True, visible_width = False):
		ConfigText.__init__(self, default, fixed_size, visible_width)
		self.suggestions = GoogleSuggestions()
		self.suggestionsThread = None
		self.suggestionsThreadRunning = False
		self.suggestionsListActivated = False

	def prepareSuggestionsThread(self):
		self.suggestions.hl = "en"
		if config.plugins.mytube.search.lr.value is not None:
			self.suggestions.hl=config.plugins.mytube.search.lr.value

	def suggestionsThreadStarted(self):
		if self.suggestionsThreadRunning:
			self.cancelSuggestionsThread()
		self.suggestionsThreadRunning = True

	def suggestionsThreadFinished(self):
		self.suggestionsThreadRunning = False

	def cancelSuggestionsThread(self):
		if self.suggestionsThread is not None:
			self.suggestionsThread.cancel()
		self.suggestionsThreadFinished()

	def propagateSuggestions(self, suggestionsList):
		self.cancelSuggestionsThread()
		print("[MyTube - ConfigTextWithGoogleSuggestions] propagateSuggestions:",suggestionsList)
		if self.suggestionsWindow:
			self.suggestionsWindow.update(suggestionsList)

	def gotSuggestionsError(self, val):
		print("[MyTube - ConfigTextWithGoogleSuggestions] gotSuggestionsError:",val)

	def getSuggestions(self):
		self.prepareSuggestionsThread()
		self.suggestionsThreadStarted()
		self.suggestionsThread = SuggestionsQueryThread(self.suggestions, self.value, self.propagateSuggestions, self.gotSuggestionsError)
		self.suggestionsThread.start()

	def handleKey(self, key):
		if not self.suggestionsListActivated:
			ConfigText.handleKey(self, key)
			if key in [KEY_DELETE, KEY_BACKSPACE, KEY_ASCII, KEY_TIMEOUT]:
				self.getSuggestions()

	def onSelect(self, session):
		ConfigText.onSelect(self, session)
		if session is not None:
			self.suggestionsWindow = session.instantiateDialog(MyTubeSuggestionsListScreen, self)
			self.suggestionsWindow.deactivate()
			self.suggestionsWindow.hide()
		self.getSuggestions()

	def onDeselect(self, session):
		self.cancelSuggestionsThread()
		ConfigText.onDeselect(self, session)
		if self.suggestionsWindow:
			session.deleteDialog(self.suggestionsWindow)
			self.suggestionsWindow = None

	def suggestionListUp(self):
		if self.suggestionsWindow.getlistlenght() > 0:
			self.value = self.suggestionsWindow.up()

	def suggestionListDown(self):
		if self.suggestionsWindow.getlistlenght() > 0:
			self.value = self.suggestionsWindow.down()

	def suggestionListPageDown(self):
		if self.suggestionsWindow.getlistlenght() > 0:
			self.value = self.suggestionsWindow.pageDown()

	def suggestionListPageUp(self):
		if self.suggestionsWindow.getlistlenght() > 0:
			self.value = self.suggestionsWindow.pageUp()

	def activateSuggestionList(self):
		ret = False
		if self.suggestionsWindow is not None and self.suggestionsWindow.shown:
			self.tmpValue = self.value
			self.value = self.suggestionsWindow.activate()
			self.allmarked = False
			self.suggestionsListActivated = True
			ret = True
		return ret

	def deactivateSuggestionList(self):
		ret = False
		if self.suggestionsWindow is not None:
			self.suggestionsWindow.deactivate()
			self.getSuggestions()
			self.allmarked = True
			self.suggestionsListActivated = False
			ret = True
		return ret

	def cancelSuggestionList(self):
		self.value = self.tmpValue
		return self.deactivateSuggestionList()

	def enableSuggestionSelection(self,value):
		if self.suggestionsWindow is not None:
			self.suggestionsWindow.enableSelection(value)

default = resolveFilename(SCOPE_HDD)
tmp = config.movielist.videodirs.value
if default not in tmp:
	tmp.append(default)

class MyTubeSuggestionsListScreen(Screen):
	if esHD():
		skin = skinMyTubeSuggestionsListScreenHD
	else:
		skin = skinMyTubeSuggestionsListScreen
		
	def __init__(self, session, configTextWithGoogleSuggestion):
		Screen.__init__(self, session)
		self.activeState = False
		self.list = []
		self.suggestlist = []
		self["suggestionslist"] = List(self.list)
		self.configTextWithSuggestion = configTextWithGoogleSuggestion

	def update(self, suggestions):
		if suggestions and len(suggestions) > 0:
			if not self.shown:
				self.show()
			suggestions_tree = cet_fromstring( suggestions )
			if suggestions_tree:
				self.list = []
				self.suggestlist = []
				for suggestion in suggestions_tree.findall("CompleteSuggestion"):
					name = None
					numresults = None
					for subelement in suggestion:
						if 'data' in subelement.attrib:
							name = subelement.attrib['data'].encode("UTF-8")
						if 'int' in subelement.attrib:
							numresults = subelement.attrib['int']
						if name and numresults:
							self.suggestlist.append((name, numresults ))
				if len(self.suggestlist):
					self.suggestlist.sort(key=lambda x: int(x[1]))
					self.suggestlist.reverse()
					for entry in self.suggestlist:
						self.list.append((entry[0], entry[1] + _(" Results") ))
					self["suggestionslist"].setList(self.list)
					self["suggestionslist"].setIndex(0)
		else:
			self.hide()

	def getlistlenght(self):
		return len(self.list)

	def up(self):
		print("up")
		if self.list and len(self.list) > 0:
			self["suggestionslist"].selectPrevious()
			return self.getSelection()

	def down(self):
		print("down")
		if self.list and len(self.list) > 0:
			self["suggestionslist"].selectNext()
			return self.getSelection()
	
	def pageUp(self):
		print("up")
		if self.list and len(self.list) > 0:
			self["suggestionslist"].selectPrevious()
			return self.getSelection()

	def pageDown(self):
		print("down")
		if self.list and len(self.list) > 0:
			self["suggestionslist"].selectNext()
			return self.getSelection()

	def activate(self):
		print("activate")
		self.activeState = True
		return self.getSelection()

	def deactivate(self):
		print("deactivate")
		self.activeState = False
		return self.getSelection()

	def getSelection(self):
		if self["suggestionslist"].getCurrent() is None:
			return None
		# fixed by openspa team
		try:
			print(self["suggestionslist"].getCurrent()[0])
			return self["suggestionslist"].getCurrent()[0]
		except:
			return None

	def enableSelection(self,value):
		self["suggestionslist"].selectionEnabled(value)


class MyTubeSettingsScreen(Screen, ConfigListScreen):
	if esHD():
		skin = skinMyTubeSettingsScreenHD
	else:
		skin = skinMyTubeSettingsScreen

	def __init__(self, session, plugin_path):
		Screen.__init__(self, session)
		self.skin_path = plugin_path
		self.session = session

		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "MediaPlayerActions", "DirectionActions"],
		{
			"ok": self.keyOK,
			"back": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
		}, -1)
		
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Save"))
		self["title"] = Label()

		self.oldadultcontentvalue = config.plugins.mytube.general.showadult.value

		self.searchContextEntries = []
		self.ProxyEntry = None
		self.loadFeedEntry = None
		self.VideoDirname = None
		ConfigListScreen.__init__(self, self.searchContextEntries, session)
		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)
		self.onShown.append(self.setWindowTitle)

	def layoutFinished(self):
		self["title"].setText(_("MyTubePlayer settings"))

	def setWindowTitle(self):
		self.setTitle(_("MyTubePlayer settings"))

	def createSetup(self):
		self.searchContextEntries = []
		self.searchContextEntries.append(getConfigListEntry(_("Display search results by:"), config.plugins.mytube.search.orderBy))
		self.searchContextEntries.append(getConfigListEntry(_("Search restricted content:"), config.plugins.mytube.search.racy))
		self.searchContextEntries.append(getConfigListEntry(_("Search category:"), config.plugins.mytube.search.categories))
		self.searchContextEntries.append(getConfigListEntry(_("Search region:"), config.plugins.mytube.search.lr))
		self.loadFeedEntry = getConfigListEntry(_("Load feed on startup:"), config.plugins.mytube.general.loadFeedOnOpen)
		self.searchContextEntries.append(self.loadFeedEntry)
		if config.plugins.mytube.general.loadFeedOnOpen.value:
			self.searchContextEntries.append(getConfigListEntry(_("Start with following feed:"), config.plugins.mytube.general.startFeed))
		self.searchContextEntries.append(getConfigListEntry(_("Videoplayer stop/exit behavior:"), config.plugins.mytube.general.on_movie_stop))
		self.searchContextEntries.append(getConfigListEntry(_("Video EOF behavior:"), config.plugins.mytube.general.on_movie_EOF))
		self.searchContextEntries.append(getConfigListEntry(_("Videobrowser exit behavior:"), config.plugins.mytube.general.on_exit))
		"""self.ProxyEntry = getConfigListEntry(_("Use HTTP Proxy Server:"), config.plugins.mytube.general.useHTTPProxy)
		self.searchContextEntries.append(self.ProxyEntry)
		if config.plugins.mytube.general.useHTTPProxy.value:
			self.searchContextEntries.append(getConfigListEntry(_("HTTP Proxy Server IP:"), config.plugins.mytube.general.ProxyIP))
			self.searchContextEntries.append(getConfigListEntry(_("HTTP Proxy Server Port:"), config.plugins.mytube.general.ProxyPort))"""
		# disabled until i have time for some proper tests	
		self.VideoDirname = getConfigListEntry(_("Download location"), config.plugins.mytube.general.videodir)
		if config.usage.setup_level.index >= 2: # expert+
			self.searchContextEntries.append(self.VideoDirname)
		self.searchContextEntries.append(getConfigListEntry(_("Clear history on Exit:"), config.plugins.mytube.general.clearHistoryOnClose))
		self.searchContextEntries.append(getConfigListEntry(_("Auto paginate on last entry:"), config.plugins.mytube.general.AutoLoadFeeds))
		self.searchContextEntries.append(getConfigListEntry(_("Reset tv-screen after playback:"), config.plugins.mytube.general.resetPlayService))
		self.searchContextEntries.append(getConfigListEntry(_("Login at start:"), config.plugins.mytube.general.logininit))
		self.searchContextEntries.append(getConfigListEntry(_("Search for videos:"), config.plugins.mytube.general.searchvideos))
		self.searchContextEntries.append(getConfigListEntry(_("Search for channels:"), config.plugins.mytube.general.searchchannels))
#		self.searchContextEntries.append(getConfigListEntry(_("Youtube Username (reopen plugin on change):"), config.plugins.mytube.general.username))
#		self.searchContextEntries.append(getConfigListEntry(_("Youtube Password (reopen plugin on change):"), config.plugins.mytube.general.password))
		self.searchContextEntries.append(getConfigListEntry(_("Allow viewing adult videos:"), config.plugins.mytube.general.showadult))
		self["config"].list = self.searchContextEntries
		self["config"].l.setList(self.searchContextEntries)
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)

	def selectionChanged(self):
		current = self["config"].getCurrent()

	def newConfig(self):
		print("newConfig", self["config"].getCurrent())
		if self["config"].getCurrent() == self.loadFeedEntry:
			self.createSetup()

	def keyOK(self):
		cur = self["config"].getCurrent()
		if config.usage.setup_level.index >= 2 and cur == self.VideoDirname:
			self.session.openWithCallback(
				self.pathSelected,
				MovieLocationBox,
				_("Choose target folder"),
				config.plugins.mytube.general.videodir.value,
				minFree = 100 # We require at least 100MB free space
			)
		else:
			self.keySave()

	def pathSelected(self, res):
		if res is not None:
			if config.movielist.videodirs.value != config.plugins.mytube.general.videodir.choices:
				config.plugins.mytube.general.videodir.setChoices(config.movielist.videodirs.value, default=res)
			config.plugins.mytube.general.videodir.value = res

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyCancel(self):
		print("cancel")
		for x in self["config"].list:
			x[1].cancel()
		self.close()	

	def keySave(self):
		print("saving")
		if config.plugins.mytube.general.searchvideos.value is False and config.plugins.mytube.general.searchchannels.value is False:
			config.plugins.mytube.general.searchvideos.value = True
		config.plugins.mytube.search.orderBy.save()
		config.plugins.mytube.search.racy.save()
		config.plugins.mytube.search.categories.save()
		config.plugins.mytube.search.lr.save()
		config.plugins.mytube.general.loadFeedOnOpen.save()
		config.plugins.mytube.general.startFeed.save()
		config.plugins.mytube.general.on_movie_stop.save()
		config.plugins.mytube.general.on_exit.save()
		config.plugins.mytube.general.videodir.save()
		config.plugins.mytube.general.clearHistoryOnClose.save()
		config.plugins.mytube.general.AutoLoadFeeds.save()
		config.plugins.mytube.general.logininit.save()
		config.plugins.mytube.general.searchvideos.save()
		config.plugins.mytube.general.searchchannels.save()

		if config.ParentalControl.configured.value and config.plugins.mytube.general.showadult.value and config.plugins.mytube.general.showadult.value != self.oldadultcontentvalue:
			pinList = self.getPinList()
			self.session.openWithCallback(self.pinEntered, PinInput, pinList=pinList, triesEntry=config.ParentalControl.retries.setuppin, title = _("Please enter the correct pin code"), windowTitle = _("Enter pin code"))
 
		if config.plugins.mytube.general.clearHistoryOnClose.value:
			config.plugins.mytube.general.history.value = ""
			config.plugins.mytube.general.history.save()
		#config.plugins.mytube.general.useHTTPProxy.save()
		#config.plugins.mytube.general.ProxyIP.save()
		#config.plugins.mytube.general.ProxyPort.save()
		for x in self["config"].list:
			x[1].save()
		config.plugins.mytube.general.save()
		config.plugins.mytube.search.save()
		config.plugins.mytube.save()
		"""if config.plugins.mytube.general.useHTTPProxy.value is True:
			proxy = {'http': 'http://'+str(config.plugins.mytube.general.ProxyIP.getText())+':'+str(config.plugins.mytube.general.ProxyPort.value)}
			self.myopener = MyOpener(proxies=proxy)
			urllib.urlopen = MyOpener(proxies=proxy).open
		else:
			self.myopener = MyOpener()
			urllib.urlopen = MyOpener().open"""
		self.close()

	def getPinList(self):
		pinList = []
		pinList.append(config.ParentalControl.setuppin.value)
		for x in config.ParentalControl.servicepin:
			pinList.append(x.value)
		return pinList

	def pinEntered(self, result):
		if result is None:
			config.plugins.mytube.general.showadult.value = False
			config.plugins.mytube.general.showadult.save()
		elif not result:
			config.plugins.mytube.general.showadult.value = False
			config.plugins.mytube.general.showadult.save()


class MyTubeTasksScreen(Screen):
	if esHD():
		skin = skinMyTubeTasksScreenHD
	else:    
		skin = skinMyTubeTasksScreen

	def __init__(self, session, plugin_path, tasklist):
		Screen.__init__(self, session)
		self.skin_path = plugin_path
		self.session = session
		self.tasklist = tasklist
		self["tasklist"] = List(self.tasklist)
		
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "MediaPlayerActions"],
		{
			"ok": self.keyOK,
			"back": self.keyCancel,
			"red": self.keyCancel,
		}, -1)
		
		self["key_red"] = Button(_("Close"))
		self["title"] = Label()
		
		self.onLayoutFinish.append(self.layoutFinished)
		self.onShown.append(self.setWindowTitle)
		self.onClose.append(self.__onClose)
		self.Timer = eTimer()
		self.Timer.callback.append(self.TimerFire)
		
	def __onClose(self):
		del self.Timer

	def layoutFinished(self):
		self["title"].setText(_("MyTubePlayer active video downloads"))
		self.Timer.startLongTimer(2)

	def TimerFire(self):
		self.Timer.stop()
		self.rebuildTaskList()
	
	def rebuildTaskList(self):
		self.tasklist = []
		for job in job_manager.getPendingJobs():
			self.tasklist.append((job,job.name,job.getStatustext(),int(100*job.progress/float(job.end)) ,str(100*job.progress/float(job.end)) + "%" ))
		self['tasklist'].setList(self.tasklist)
		self['tasklist'].updateList(self.tasklist)
		self.Timer.startLongTimer(2)

	def setWindowTitle(self):
		self.setTitle(_("MyTubePlayer active video downloads"))

	def keyOK(self):
		current = self["tasklist"].getCurrent()
		print(current)
		if current:
			job = current[0]
			from Screens.TaskView import JobView
			self.session.openWithCallback(self.JobViewCB, JobView, job)
	
	def JobViewCB(self, why):
		print("WHY---",why)

	def keyCancel(self):
		self.close()	

	def keySave(self):
		self.close()


class MyTubeHistoryScreen(Screen):
	if esHD():
		skin = skinMyTubeHistoryScreenHD
	else:
		skin = skinMyTubeHistoryScreen


	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.historylist = []
		print("self.historylist",self.historylist)
		self["historylist"] = List(self.historylist)
		self.activeState = False
		
	def activate(self):
		print("activate")
		self.activeState = True
		self.history = config.plugins.mytube.general.history.value.split(',')
		if self.history[0] == '':
			del self.history[0]
		print("self.history",self.history)
		self.historylist = []
		for entry in self.history:
			self.historylist.append(( str(entry),))
		self["historylist"].setList(self.historylist)
		self["historylist"].updateList(self.historylist)

	def deactivate(self):
		print("deactivate")
		self.activeState = False

	def status(self):
		print(self.activeState)
		return self.activeState
	
	def getSelection(self):
		if self["historylist"].getCurrent() is None:
			return None
		#fixed by openspa
		try:
			print(self["historylist"].getCurrent()[0])
			return self["historylist"].getCurrent()[0]
		except:
			return None

	def up(self):
		print("up")
		self["historylist"].selectPrevious()
		return self.getSelection()

	def down(self):
		print("down")
		self["historylist"].selectNext()
		return self.getSelection()
	
	def pageUp(self):
		print("up")
		self["historylist"].selectPrevious()
		return self.getSelection()

	def pageDown(self):
		print("down")
		self["historylist"].selectNext()
		return self.getSelection()

