from . import _, esHD
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Sources.List import List
from Components.Task import Task, Job, job_manager
from Components.config import config, ConfigSelection, ConfigSubsection, ConfigText, ConfigYesNo, getConfigListEntry, ConfigPassword
##, ConfigIP, ConfigNumber, ConfigLocations
from .MyTubeSearch import ConfigTextWithGoogleSuggestions, MyTubeSettingsScreen, MyTubeTasksScreen, MyTubeHistoryScreen
from .MyTubeService import myTubeService
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBarGenerics import InfoBarNotifications, InfoBarSeek
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.LoadPixmap import LoadPixmap

from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, SCOPE_HDD, SCOPE_CURRENT_PLUGIN, fileExists

from Tools.Downloader import downloadWithProgress
from Tools import ASCIItranslit

from enigma import eTimer, ePoint, RT_HALIGN_LEFT, RT_VALIGN_CENTER, gFont, ePicLoad, eServiceReference, iPlayableService, BT_SCALE, BT_KEEP_ASPECT_RATIO
from os import path as os_path, remove as os_remove
from twisted.web import client
from time import sleep


#added by openspa
from .skinsmytube import *
from .skinsmytubeHD import *

#def rutaskin(nombre):
#	if esHD():
#		nombre=nombre+'HD'
#	return nombre    

#class eTPM:
#		TPMD_DT_LEVEL3_CERT = 5
#		TPMD_DT_LEVEL2_CERT = 4
#		def __init__(self):
#			self.TPM = self
#		def getCert(self, *args):
#			return "12345678"
#		def challenge(self, r):
#			return r

#def decrypt_block(a,b):
#		return 80*"-" + a

#def get_rnd():
#		return "12345678"

#def validate_cert(*args):
#		return "12345678"

all_feeds = { 	"most_viewed": _("Most viewed"),
		"top_rated": _("Top rated"),
		"1": _("Film & Animation"),
		"2": _("Autos & Vehicles"),
		"10": _("Music"),
		"15": _("Pets & Animals"),
		"17": _("Sports"),
		"18": _("Short Movies"),
		"19": _("Travel & Events"),
		"20": _("Gaming"),
		"21": _("Videoblogs"),
		"22": _("People & Blogs"),
		"23":_("Comedy"),
		"24":_("Entertainment"),
		"25":_("News & Politic"),
		"26":_("Howto & Style"),
		"27":_("Education"),
		"28":_("Science & Technology"),
		"my_subscriptions": _("My Subscriptions"),
		"my_favorites": _("My Favorites"),
		"my_uploads": _("My Uploads"),
		"my_likes": _("My videos likes"),
		_("Related video entries."): _("Related video entries."),
		_("Response video entries."): _("Response video entries."),
		_("User video entries."): _("User video entries."),

	}


#etpm = eTPM()
#rootkey = ['\x9f', '|', '\xe4', 'G', '\xc9', '\xb4', '\xf4', '#', '&', '\xce', '\xb3', '\xfe', '\xda', '\xc9', 'U', '`', '\xd8', '\x8c', 's', 'o', '\x90', '\x9b', '\\', 'b', '\xc0', '\x89', '\xd1', '\x8c', '\x9e', 'J', 'T', '\xc5', 'X', '\xa1', '\xb8', '\x13', '5', 'E', '\x02', '\xc9', '\xb2', '\xe6', 't', '\x89', '\xde', '\xcd', '\x9d', '\x11', '\xdd', '\xc7', '\xf4', '\xe4', '\xe4', '\xbc', '\xdb', '\x9c', '\xea', '}', '\xad', '\xda', 't', 'r', '\x9b', '\xdc', '\xbc', '\x18', '3', '\xe7', '\xaf', '|', '\xae', '\x0c', '\xe3', '\xb5', '\x84', '\x8d', '\r', '\x8d', '\x9d', '2', '\xd0', '\xce', '\xd5', 'q', '\t', '\x84', 'c', '\xa8', ')', '\x99', '\xdc', '<', '"', 'x', '\xe8', '\x87', '\x8f', '\x02', ';', 'S', 'm', '\xd5', '\xf0', '\xa3', '_', '\xb7', 'T', '\t', '\xde', '\xa7', '\xf1', '\xc9', '\xae', '\x8a', '\xd7', '\xd2', '\xcf', '\xb2', '.', '\x13', '\xfb', '\xac', 'j', '\xdf', '\xb1', '\x1d', ':', '?']

config.plugins.mytube = ConfigSubsection()
config.plugins.mytube.search = ConfigSubsection()


config.plugins.mytube.search.searchTerm = ConfigTextWithGoogleSuggestions("", False)
config.plugins.mytube.search.orderBy = ConfigSelection(
				[
				 ("relevance", _("Relevance")),
				 ("viewCount", _("View Count")),
				 ("date", _("Published")),
				 ("rating", _("Rating"))
				], "relevance")
config.plugins.mytube.search.time = ConfigSelection(
				[
				 ("all_time", _("All Time")),
				 ("this_month", _("This Month")),
				 ("this_week", _("This Week")),
				 ("today", _("Today"))
				], "all_time")
config.plugins.mytube.search.racy = ConfigSelection(
				[
				 ("include", _("Yes")),
				 ("exclude", _("No"))
				], "include")
config.plugins.mytube.search.categories = ConfigSelection(
				[
				 (None, _("All")),
				 ("1", _("Film & Animation")),
				 ("2", _("Autos & Vehicles")),
				 ("10", _("Music")),
				 ("15", _("Pets & Animals")),
				 ("17", _("Sports")),
				 ("19", _("Travel & Events")),
				 ("18", _("Short Movies")),
				 ("20", _("Gaming")),
				 ("23", _("Comedy")),
				 ("22", _("People & Blogs")),
				 ("25", _("News & Politic")),
				 ("24", _("Entertainment")),
				 ("27", _("Education")),
				 ("26", _("Howto & Style")),
				 ("28", _("Science & Technology"))
				], None)
config.plugins.mytube.search.lr = ConfigSelection(
				[
				 (None, _("All")),
				 ("au", _("Australia")),
				 ("br", _("Brazil")),
				 ("ca", _("Canada")),
				 ("cz", _("Czech Republic")),
				 ("fr", _("France")),
				 ("de", _("Germany")),
				 ("gb", _("Great Britain")),
				 ("nl", _("Holland")),
				 ("hk", _("Hong Kong")),
				 ("in", _("India")),
				 ("ie", _("Ireland")),
				 ("il", _("Israel")),
				 ("it", _("Italy")),
				 ("jp", _("Japan")),
				 ("mx", _("Mexico")),
				 ("nz", _("New Zealand")),
				 ("pl", _("Poland")),
				 ("ru", _("Russia")),
				 ("kr", _("South Korea")),
				 ("es", _("Spain")),
				 ("se", _("Sweden")),
				 ("tw", _("Taiwan")),
				 ("us", _("United States")) 
				], None)
config.plugins.mytube.search.sortOrder = ConfigSelection(
				[
				 ("ascending", _("Ascending")),
				 ("descending", _("Descending"))
				], "ascending")

config.plugins.mytube.general = ConfigSubsection()
config.plugins.mytube.general.showHelpOnOpen = ConfigYesNo(default = True)
config.plugins.mytube.general.loadFeedOnOpen = ConfigYesNo(default = True)
config.plugins.mytube.general.startFeed = ConfigSelection(
				[
				 ("hd", _("HD videos")),
				 ("most_viewed", _("Most viewed")),
				 ("top_rated", _("Top rated")),
				 ("recently_featured", _("Recently featured")),
				 ("most_discussed", _("Most discussed")),
				 ("top_favorites", _("Top favorites")),
				 ("most_linked", _("Most linked")),
				 ("most_responded", _("Most responded")),
				 ("most_recent", _("Most recent")),
				 ("most_popular", _("Most popular")),
				 ("most_shared", _("Most shared")),
				 ("on_the_web", _("Trending videos")),
				 ("my_subscriptions", _("My Subscriptions")),
				 ("my_favorites", _("My Favorites")),
				 ("my_uploads", _("My Uploads")),
				 ("my_likes", _("My videos likes")),
				], "top_rated")
config.plugins.mytube.general.on_movie_stop = ConfigSelection(default = "ask", choices = [
	("ask", _("Ask user")), ("quit", _("Return to movie list")), ("playnext", _("Play next video")), ("playagain", _("Play video again")) ])
config.plugins.mytube.general.on_movie_EOF = ConfigSelection(default = "ask", choices = [
	("ask", _("Ask user")), ("quit", _("Return to movie list")), ("playnext", _("Play next video")), ("playagain", _("Play video again")) ])

config.plugins.mytube.general.on_exit = ConfigSelection(default = "ask", choices = [
	("ask", _("Ask user")), ("quit", _("Return to movie list"))])

default = resolveFilename(SCOPE_HDD)
tmp = config.movielist.videodirs.value
if default not in tmp:
	tmp.append(default)
config.plugins.mytube.general.videodir = ConfigSelection(default = default, choices = tmp)
config.plugins.mytube.general.history = ConfigText(default="")
config.plugins.mytube.general.clearHistoryOnClose = ConfigYesNo(default = False)
config.plugins.mytube.general.AutoLoadFeeds = ConfigYesNo(default = True)
config.plugins.mytube.general.resetPlayService = ConfigYesNo(default = False)
#config.plugins.mytube.general.username = ConfigText(default="", fixed_size = False)
#config.plugins.mytube.general.password = ConfigPassword(default="")
config.plugins.mytube.general.logininit = ConfigYesNo(default = True)
config.plugins.mytube.general.searchvideos = ConfigYesNo(default = True)
config.plugins.mytube.general.searchchannels = ConfigYesNo(default = False)

config.plugins.mytube.general.showadult = ConfigYesNo(default = False)
config.plugins.mytube.refreshToken = ConfigText(default='')

#config.plugins.mytube.general.useHTTPProxy = ConfigYesNo(default = False)
#config.plugins.mytube.general.ProxyIP = ConfigIP(default=[0,0,0,0])
#config.plugins.mytube.general.ProxyPort = ConfigNumber(default=8080)

plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/MyTube"

def getpluginpath():
	return plugin_path

class downloadJob(Job):
	def __init__(self, url, file, title):
		Job.__init__(self, title)
		downloadTask(self, url, file)

class downloadTask(Task):
	def __init__(self, job, url, file):
		Task.__init__(self, job, ("download task"))
		self.end = 100
		self.url = url
		self.local = file

	def prepare(self):
		self.error = None

	def run(self, callback):
		self.callback = callback
		self.download = downloadWithProgress(self.url,self.local)
		self.download.addProgress(self.http_progress)
		self.download.start().addCallback(self.http_finished).addErrback(self.http_failed)
	
	def http_progress(self, recvbytes, totalbytes):
		#print "[http_progress] recvbytes=%d, totalbytes=%d" % (recvbytes, totalbytes)
		self.progress = int(self.end*recvbytes/float(totalbytes))
	
	def http_finished(self, string=""):
		print("[http_finished]" + str(string))
		Task.processFinished(self, 0)
	
	def http_failed(self, failure_instance=None, error_message=""):
		if error_message == "" and failure_instance is not None:
			error_message = failure_instance.getErrorMessage()
			print("[http_failed] " + error_message)
			Task.processFinished(self, 1)





class MyTubePlayerMainScreen(Screen, ConfigListScreen):
	BASE_STD_FEEDURL = "http://gdata.youtube.com/feeds/api/standardfeeds/"
	Details = {}
	#(entry, Title, Description, TubeID, thumbnail, PublishedDate,Views,duration,ratings )	
	if esHD():
		skin = skinMyTubePlayerMainScreenHD
	else:
		skin = skinMyTubePlayerMainScreen    
		
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
#		self.l2key = l2key
#		self.l3key = None
		self.skin_path = plugin_path
		self.FeedURL = None
		self.ytfeed = None
		self.currentFeedName = None
		self.videolist = []
		self.queryThread = None
		self.queryRunning = False
		self.oauth = None

		try:
			import ssl
			self.https_context = ssl._create_default_https_context
			ssl._create_default_https_context = ssl._create_unverified_context
		except:
			pass

		self.video_playlist = []
		self.statuslist = []
		self.mytubeentries = None

		self.thumbnails = []
		self.index = 0
		self.maxentries = 0

		self.screenshotList = []
		self.pixmaps_to_load = []
		self.picloads = {}

		self.oldfeedentrycount = 0
		self.appendEntries = False
		self.lastservice = session.nav.getCurrentlyPlayingServiceOrGroup()
		self.propagateUpDownNormally = True
		self.FirstRun = True
		self.HistoryWindow = None
		self.History = None
		self.searchtext = _("Welcome to the MyTube Youtube Player.\n\nWhile entering your search term(s) you will get suggestions displayed matching your search term.\n\nTo select a suggestion press DOWN on your remote, select the desired result and press OK on your remote to start the search.\n\nPress exit to get back to the input field.")
		self.feedtext = _("Welcome to the MyTube Youtube Player.\n\nUse the Bouqet+ button to navigate to the search field and the Bouqet- to navigate to the video entries.\n\nTo play a movie just press OK on your remote control.\n\nPress info to see the movie description.\n\nPress the Menu button for additional options.\n\nThe Help button shows this help again.")
		self.currList = "configlist"
		self.oldlist = None

		self["feedlist"] = List(self.videolist)
		self["thumbnail"] = Pixmap()
		self["thumbnail"].hide()
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Std. Feeds"))
		self["key_yellow"] = Button(_("History"))
		self["ButtonBlue"] = Pixmap()
		self["VKeyIcon"] = Pixmap()
		self["ButtonBlue"].hide()
		self["VKeyIcon"].hide()		
		self["result"] = Label("")
		self["user"] = Label()
		self["cviews"] = Label()
		self["cvideowatch"] = Label()
		self["csubscriptors"] = Label()
		self["cuser_uploads"] = Label()
		self["subscriptors"] = Label()
		self["views"] = Label()
		self["videowatch"] = Label()
		self["user_uploads"] = Label()
		self["feed"] = Label()
		self["icon"] = Pixmap()
		self.icon = None
		# Get FrameBuffer Scale for ePicLoad()
		sc = AVSwitch().getFramebufferScale()
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.showIconPixmap)
		self.picload.setPara((85, 85, sc[0], sc[1], 0, 1, "#00e0e0e0"))


		self["searchactions"] = ActionMap(["ShortcutActions", "WizardActions", "HelpActions", "MediaPlayerActions", "DirectionActions"],
		{
			"ok": self.keyOK,
			"back": self.leavePlayer,
			"red": self.leavePlayer,
			"blue": self.openKeyboard,
			"yellow": self.handleHistory,
			"up": self.keyUp,
			"down": self.handleSuggestions,
			"left": self.keyLeft,
			"right": self.keyRight,
			"prevBouquet": self.switchToFeedList,
			"nextBouquet": self.switchToConfigList,
			"displayHelp": self.handleHelpWindow,
			"menu" : self.handleMenu,
		}, -2)

		self["suggestionactions"] = ActionMap(["ShortcutActions", "WizardActions", "MediaPlayerActions", "HelpActions", "DirectionActions", "NumberActions"],
		{
			"ok": self.keyOK,
			"back": self.switchToConfigList,
			"red": self.switchToConfigList,
			"nextBouquet": self.switchToConfigList,
			"prevBouquet": self.switchToFeedList,
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
			"0": self.toggleScreenVisibility
		}, -2)


		self["videoactions"] = ActionMap(["ShortcutActions", "WizardActions", "MediaPlayerActions", "MovieSelectionActions", "HelpActions", "DirectionActions"],
		{
			"ok": self.keyOK,
			"back": self.leavePlayer,
			"red": self.leavePlayer,
			"yellow": self.handleHistory,
			"up": self.keyUp,
			"down": self.keyDown,	
			"nextBouquet": self.switchToConfigList,
			"green": self.keyStdFeed,
			"showEventInfo": self.showVideoInfo,
			"displayHelp": self.handleHelpWindow,
			"menu" : self.handleMenu,
		}, -2)

		self["statusactions"] = ActionMap(["ShortcutActions", "WizardActions", "HelpActions", "MediaPlayerActions"],
		{
			"back": self.leavePlayer,
			"red": self.leavePlayer,
			"nextBouquet": self.switchToConfigList,
			"green": self.keyStdFeed,
			"yellow": self.handleHistory,
			"menu": self.handleMenu
		}, -2)

		self["historyactions"] = ActionMap(["ShortcutActions", "WizardActions", "MediaPlayerActions", "MovieSelectionActions", "HelpActions", "DirectionActions"],
		{
			"ok": self.keyOK,
			"back": self.closeHistory,
			"red": self.closeHistory,
			"yellow": self.handleHistory,
			"up": self.keyUp,
			"down": self.keyDown,	
			"left": self.keyLeft,
			"right": self.keyRight,
		}, -2)

		self["videoactions"].setEnabled(False)
		self["statusactions"].setEnabled(False)
		self["historyactions"].setEnabled(False)
		
		self.timer_startDownload = eTimer()
		self.timer_startDownload.timeout.callback.append(self.downloadThumbnails)
		self.timer_thumbnails = eTimer()
		self.timer_thumbnails.timeout.callback.append(self.updateFeedThumbnails)

		self.SearchConfigEntry = None
		self.searchContextEntries = []
		config.plugins.mytube.search.searchTerm.value = ""
		ConfigListScreen.__init__(self, self.searchContextEntries, session)
		self.createSetup()		
		self.onLayoutFinish.append(self.layoutFinished)
		self.onShown.append(self.setWindowTitle)
		self.onClose.append(self.__onClose)
		self.Timer = eTimer()
		self.Timer.callback.append(self.TimerFire)
		
	def __onClose(self):
		if myTubeService.is_auth() is True and config.plugins.mytube.general.logininit.value is False:
			if self.icon != None:
				if fileExists(self.icon, 'r'):
					os_remove(self.icon)

		myTubeService.resetAuthState()
		del self.Timer
		del self.timer_startDownload
		del self.timer_thumbnails
		try:
			import ssl
			ssl._create_default_https_context = self.https_context
		except:
			pass
		self.Details = {}
		self.session.nav.playService(self.lastservice)
		
	def layoutFinished(self):
		self.currList = "status"
		current = self["config"].getCurrent()
		if current[1].help_window.instance is not None:
			current[1].help_window.instance.hide()

#		l3cert = etpm.getCert(eTPM.TPMD_DT_LEVEL3_CERT)
#		if l3cert is None or l3cert is "":
#			self["videoactions"].setEnabled(False)
#			self["searchactions"].setEnabled(False)
#			self["config_actions"].setEnabled(False)
#			self["historyactions"].setEnabled(False)
#			self["statusactions"].setEnabled(True)
#			self.hideSuggestions()
#			self.statuslist = []
#			self.statuslist.append(( _("Genuine Dreambox validation failed!"), _("Verify your Dreambox authenticity by running the genuine dreambox plugin!" ) ))
#			self["feedlist"].style = "state"
#			self['feedlist'].setList(self.statuslist)
#			return

#		self.l3key = validate_cert(l3cert, self.l2key)
#		if self.l3key is None:
#			print("l3cert invalid")
#			return
#		rnd = get_rnd()
#		if rnd is None:
#			print("random error")
#			return

#		val = etpm.challenge(rnd)
#		result = decrypt_block(val, self.l3key)

		self.statuslist = []
#		if result[80:88] == rnd:

		# we need to login here; startService() is fired too often for external curl
		if self.tryUserLogin():
			self.statuslist.append(( _("Fetching feed entries"), _("Trying to download the Youtube feed entries. Please wait..." ) ))
			self.Timer.start(200)
		self["feedlist"].style = "state"
		self['feedlist'].setList(self.statuslist)
#		else:
#			self.statuslist.append(( _("Genuine Dreambox validation failed!"), _("Verify your Dreambox authenticity by running the genuine dreambox plugin!" ) ))
#			self["feedlist"].style = "state"
#			self['feedlist'].setList(self.statuslist)		
	
	def TimerFire(self):
		self.Timer.stop()
		if config.plugins.mytube.general.loadFeedOnOpen.value:
			self.setState('getFeed')
		else:
			self.setState('byPass')
		
	def setWindowTitle(self):
		self.setTitle(_("MyTubePlayer"))

	def createSetup(self):
		self.searchContextEntries = []
		self.SearchConfigEntry = getConfigListEntry(_("Search Term(s)"), config.plugins.mytube.search.searchTerm)
		self.searchContextEntries.append(self.SearchConfigEntry)
		self["config"].list = self.searchContextEntries
		self["config"].l.setList(self.searchContextEntries)


	def tryUserLogin(self):
		if config.plugins.mytube.refreshToken.value != "" and config.plugins.mytube.general.logininit.value:
			try:
				self.oauth = myTubeService.auth_user()
				if self.oauth:
					accessToken = self.oauth.get_access_token(config.plugins.mytube.refreshToken.value)
					start = myTubeService.startService(accessToken)
					if not start:
						self.statuslist.append(( _("Login Error"), _("Please, type your CLIENT_ID & CLIENT_SECRET in /etc/keys/mytube.key" ) ))
						return False
				else:
					self.statuslist.append(( _("Error"), _("Please, type your YOUTUBE API KEY in /etc/keys/mytube.key" ) ))
					return False
				name = self.getuserData()
				self.statuslist.append(( _("Login OK"), _('Hello') + ' ' + str(name)))
			except Exception as e:
				print('Login-Error: ' + str(e))
				self.statuslist.append(( _("Login failed"), str(e)))
				return False
		else:
			start = myTubeService.startService()
			if not start:
				self.statuslist.append(( _("Error"), _("Please, type your YOUTUBE API KEY in /etc/keys/mytube.key" ) ))
				return False
		return True

	def getUserEntry(self, user="default"):
#		username, img_url, view_count, video_watch_count, subscriber_count, favorite_count, user_subscription, user_liveevent, user_favorites, user_contacts, user_uploads = myTubeService.getUserEntry(user)
		return myTubeService.getUserEntry(user)

	def getuserData(self):
		if myTubeService.is_auth() is True:
			username, img_url, view_count, coment_count, subscriber_count, video_count = self.getUserEntry()
			self["user"].setText(username)
			self["csubscriptors"].setText(_("Subscriptors")+":")
			self["cviews"].setText(_("My videos uploaded viewed")+":")
			#self["cvideowatch"].setText(_("Comments")+":")
			self["cuser_uploads"].setText(_("Videos uploaded")+":")
			self["subscriptors"].setText("%d" % int(subscriber_count))
			self["views"].setText("%d" % int(view_count))
			#self["videowatch"].setText("%d" % int(coment_count))
			self["user_uploads"].setText("%d" % int(video_count))
			self.icon = self.skin_path + "/img/" + img_url.split("/")[-1]
			if fileExists(self.icon, 'r'):
				self.goticon()
			else:
				client.downloadPage(img_url.encode("utf-8"), self.icon, agent="Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.2) Gecko/2008091620 Firefox/3.0.2").addCallback(self.goticon).addErrback(self.showThumbError)
			return username
			
	def goticon(self, data=""):
		if self.icon != None:
			self.picload.startDecode(str(self.icon))

	def showIconPixmap(self, picInfo=None):
		ptr = self.picload.getData()
		if ptr != None:
			self["icon"].instance.setPixmap(ptr.__deref__())
			self["icon"].show()

	def showThumbError(self, error):
		pass

	def setState(self,status = None):
		if status:
			self.currList = "status"
			self["videoactions"].setEnabled(False)
			self["searchactions"].setEnabled(False)
			self["config_actions"].setEnabled(False)
			self["historyactions"].setEnabled(False)
			self["statusactions"].setEnabled(True)
			self["ButtonBlue"].hide()
			self["VKeyIcon"].hide()	
			self.statuslist = []
			self.hideSuggestions()
			result = None
#			if self.l3key is not None:
#				rnd = get_rnd()
#				if rnd is None:
#					return
#				val = etpm.challenge(rnd)
#				result = decrypt_block(val, self.l3key)
#			if not result or result[80:88] != rnd:
#				self["key_green"].show()
#				self.statuslist.append(( _("Genuine Dreambox validation failed!"), _("Verify your Dreambox authenticity by running the genuine dreambox plugin!" ) ))
#				self["feedlist"].style = "state"
#				self['feedlist'].setList(self.statuslist)
#			else:
			print("Genuine Dreambox validation passed")
			if self.FirstRun == True:
				self.appendEntries = False
#					myTubeService.startService()
				if myTubeService.is_auth():
					myTubeService.getuserplaylist()
			if self.HistoryWindow is not None:
				self.HistoryWindow.deactivate()
				self.HistoryWindow.instance.hide()
			if status == 'getFeed':
				self.statuslist.append(( _("Fetching feed entries"), _("Trying to download the Youtube feed entries. Please wait..." ) ))
			elif status == 'getSearchFeed':
				self.statuslist.append(( _("Fetching search entries"), _("Trying to download the Youtube search results. Please wait..." ) ))
			elif status == 'Error':
				self.statuslist.append(( _("An error occured."), _("There was an error getting the feed entries. Please try again." ) ))
			elif status == 'noVideos':
				self["key_green"].show()
				self.statuslist.append(( _("No videos to display"), _("Please select a standard feed or try searching for videos." ) ))
			elif status == 'byPass':
				self.statuslist.append(( _("Not fetching feed entries"), _("Please enter your search term." ) ))
				self["feedlist"].style = "state"
				self['feedlist'].setList(self.statuslist)
				self.switchToConfigList()
			self["feedlist"].style = "state"
			self['feedlist'].setList(self.statuslist)
			if self.FirstRun == True:
				self.FirstRun = False
				if config.plugins.mytube.general.loadFeedOnOpen.value:
					self.getFeed(self.BASE_STD_FEEDURL, str(config.plugins.mytube.general.startFeed.value))

	def handleHelpWindow(self):
		print("[handleHelpWindow]")
		if self.currList == "configlist":
			self.hideSuggestions()
			self.session.openWithCallback(self.ScreenClosed, MyTubeVideoHelpScreen, self.skin_path, wantedinfo = self.searchtext, wantedtitle = _("MyTubePlayer Help") )
		elif self.currList == "feedlist":
			self.session.openWithCallback(self.ScreenClosed, MyTubeVideoHelpScreen, self.skin_path, wantedinfo = self.feedtext, wantedtitle = _("MyTubePlayer Help") )
			
	def handleFirstHelpWindow(self):
		print("[handleFirstHelpWindow]")
		if config.plugins.mytube.general.showHelpOnOpen.value is True:
			if self.currList == "configlist":
				self.hideSuggestions()
				self.session.openWithCallback(self.firstRunHelpClosed, MyTubeVideoHelpScreen, self.skin_path,wantedinfo = self.feedtext, wantedtitle = _("MyTubePlayer Help") )
		else:
			self.FirstRun = False
			
	def firstRunHelpClosed(self):
		if self.FirstRun == True:	
			self.FirstRun = False
			self.switchToConfigList()

	def handleMenu(self):
		if self.currList == "configlist" or self.currList == "status":
			menulist = (
					(_("MyTube Settings"), "settings"),
				)
			self.hideSuggestions()
			self.session.openWithCallback(self.openMenu, ChoiceBox, title=_("Select your choice."), list = menulist)

		elif self.currList == "feedlist":
			current = self[self.currList].getCurrent()
			vtype = "youtube#video"
			if current:
				myentry = current[0]
				if myentry is not None:
					vtype = myentry.getType()
			menulist = [(_("MyTube Settings"), "settings")]
			if not myTubeService.is_auth():
				menulist.extend((
						(_("Login"), "login"),
					))
			if vtype == "youtube#video":
				menulist.extend((
						(_("View related videos"), "related"),
					))
			if self.ytfeed != "my_subscriptions" and self.ytfeed != "my_favorites" and self.ytfeed != "my_history" and self.ytfeed != "my_watch_later" and self.ytfeed != "my_uploads" and self.ytfeed != "my_likes":
				menulist.extend((
						(_("View user videos"), "user_videos"),
					))
			
			if myTubeService.is_auth() is True and self.ytfeed != "my_subscriptions" and self.ytfeed != "my_favorites" and self.ytfeed != "my_history" and self.ytfeed != "my_watch_later" and self.ytfeed != "my_uploads" and self.ytfeed != "my_likes":
				menulist.extend((
						(_("Subscribe to user"), "subscribe"),
					))
				if vtype == "youtube#video":
					menulist.extend((
							(_("Add to favorites"), "favorite"),
							(_("Like this video"), "like"),
							(_("Dislike this video"), "dislike"),
						))				
			if self.ytfeed == "my_subscriptions":
				menulist.extend((
						(_("Remove Subscription"), "unsubscribe"),
					))
			if self.ytfeed == "my_favorites":
				menulist.extend((
						(_("Remove From Favorites"), "deletefav"),
					))
			if config.usage.setup_level.index >= 2: # expert+
				if vtype == "youtube#video":
					menulist.extend((
						(_("Download Video"), "download"),
					))
				menulist.extend((
					(_("View active downloads"), "downview"),
				))
						
			self.hideSuggestions()
			self.session.openWithCallback(self.openMenu, ChoiceBox, title=_("Select your choice."), list = menulist)

	def openMenu(self, answer):
		answer = answer and answer[1]
		if answer == "login":
			if not self.oauth:
				self.oauth = myTubeService.auth_user()

			if not self.oauth:
				self.session.open(MessageBox, _("Please, type your CLIENT_ID & CLIENT_SECRET in /etc/keys/mytube.key"), MessageBox.TYPE_ERROR)
				config.plugins.mytube.refreshToken.value = ''
				config.plugins.mytube.refreshToken.save()
			else:
				self.splitTaimer = eTimer()
				self.splitTaimer.timeout.callback.append(self.splitTaimerStop)
				userCode = str(self.oauth.get_user_code())
				msg = _('Go to %s\nAnd enter the code %s') % (str(self.oauth.verification_url), userCode)
				print("[YouTube] ", msg)
				self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
				self.splitTaimer.start(9000)
		if answer == "settings":
			print("settings selected")
			self.session.openWithCallback(self.ScreenClosed,MyTubeSettingsScreen, self.skin_path )
		elif answer == "related":
			current = self["feedlist"].getCurrent()[0]
			self.setState('getFeed')
			self.getRelatedVideos(current)
		elif answer == "user_videos":
			current = self["feedlist"].getCurrent()[0]
			self.setState('getFeed')
			self.getUserVideos(current)
		elif answer == "subscribe":
			current = self["feedlist"].getCurrent()[0]
			self.session.open(MessageBox, current.subscribeToUser(), MessageBox.TYPE_INFO)
		elif answer == "unsubscribe":
			current = self["feedlist"].getCurrent()[0]
			self.session.open(MessageBox, current.UnsubscribeToUser(), MessageBox.TYPE_INFO)
			sleep(5)
			self.openStandardFeedClosed((_("My Subscriptions"), "my_subscriptions"))			
		elif answer == "favorite":
			current = self["feedlist"].getCurrent()[0]
			sleep(3)
			self.session.open(MessageBox, current.addToFavorites(), MessageBox.TYPE_INFO)
		elif answer == "like":
			current = self["feedlist"].getCurrent()[0]
			current.like()			
		elif answer == "dislike":
			current = self["feedlist"].getCurrent()[0]
			current.dislike()			
		elif answer == "deletefav":
			current = self["feedlist"].getCurrent()[0]
			self.session.open(MessageBox, current.deletefromFavorites(), MessageBox.TYPE_INFO)
			self.openStandardFeedClosed((_("My Favorites"), "my_favorites"))			
		elif answer == "response":
			current = self["feedlist"].getCurrent()[0]
			self.setState('getFeed')
			self.getResponseVideos(current)
		elif answer == "download":
			if self.currList == "feedlist":
				current = self[self.currList].getCurrent()
				if current:
					myentry = current[0]
					if myentry:
						myurl = myentry.getVideoUrl()
						filename = str(config.plugins.mytube.general.videodir.value)+ ASCIItranslit.legacyEncode(str(myentry.getTitle()).strip()) + '.mp4'
						job_manager.AddJob(downloadJob(myurl,filename, str(myentry.getTitle())[:30]))
		elif answer == "downview":
			self.tasklist = []
			for job in job_manager.getPendingJobs():
				self.tasklist.append((job,job.name,job.getStatustext(),int(100*job.progress/float(job.end)) ,str(100*job.progress/float(job.end)) + "%" ))
			self.session.open(MyTubeTasksScreen, self.skin_path , self.tasklist)		
		elif answer == None:
			self.ScreenClosed()
	
	def splitTaimerStop(self):
		self.splitTaimer.stop()
		# Here we waiting until the user enter a code
		refreshToken, retryInterval = self.oauth.get_new_token()
		if not refreshToken:
			self.splitTaimer.start(retryInterval * 1000)
		else:
			print("[YouTube] Get refresh token")
			if self.mbox:
				self.mbox.close()
			config.plugins.mytube.refreshToken.value = refreshToken
			config.plugins.mytube.refreshToken.save()
			del self.splitTaimer
			accessToken = self.oauth.get_access_token(refreshToken)
			myTubeService.startService(accessToken)
			self.mbox = None
			name = self.getuserData()
			#self.oauth = None

	def openKeyboard(self):
		self.hideSuggestions()
		# fixed by openspa team
		from Tools.Directories import fileExists
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.pyo") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.py") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.pyc") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.so"):
			from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
			self.session.openWithCallback(self.SearchEntryCallback, spzVirtualKeyboard, titulo = _("Enter your search term(s)"), texto = config.plugins.mytube.search.searchTerm.value)
		else:
			self.session.openWithCallback(self.SearchEntryCallback, VirtualKeyBoard, title = (_("Enter your search term(s)")), text = config.plugins.mytube.search.searchTerm.value)

	def ScreenClosed(self):
		print("ScreenCLosed, restoring old window state")
		if self.currList == "historylist":
			if self.HistoryWindow.status() is False:
				self.HistoryWindow.activate()
				self.HistoryWindow.instance.show()
		elif self.currList == "configlist":
			self.switchToConfigList()
			ConfigListScreen.keyOK(self)
		elif self.currList == "feedlist":
			self.switchToFeedList()

	def SearchEntryCallback(self, callback = None):
		if callback is not None and len(callback):
			config.plugins.mytube.search.searchTerm.value = callback
			ConfigListScreen.keyOK(self)
			self["config"].getCurrent()[1].getSuggestions()
		current = self["config"].getCurrent()
		if current[1].help_window.instance is not None:
			current[1].help_window.instance.show()	
		if current[1].suggestionsWindow.instance is not None:
			current[1].suggestionsWindow.instance.show()
		self.propagateUpDownNormally = True

	def openStandardFeedClosed(self, answer):
		answer = answer and answer[1]
		if answer is not None:
			self.setState('getFeed')
			self.appendEntries = False
			self.getFeed(self.BASE_STD_FEEDURL, str(answer))

	def handleLeave(self, how):
		self.is_closing = True
		if how == "ask":
			if self.currList == "configlist":
				list = (
					(_("Yes"), "quit"),
					(_("No"), "continue"),
					(_("No, but switch to video entries."), "switch2feed")
				)
			else:
				list = (
					(_("Yes"), "quit"),
					(_("No"), "continue"),
					(_("No, but switch to video search."), "switch2search")
				)					
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Really quit MyTube Player?"), list = list)
		else:
			self.leavePlayerConfirmed([True, how])

	def leavePlayer(self):
		print("leavePlayer")
		if self.HistoryWindow is not None:
			self.HistoryWindow.deactivate()
			self.HistoryWindow.instance.hide()
		if self.currList == "configlist":
			current = self["config"].getCurrent()
			if current[1].suggestionsWindow.activeState is True:
				self.propagateUpDownNormally = True
				current[1].deactivateSuggestionList()
				self["config"].invalidateCurrent()
			else:
				self.hideSuggestions()
				self.handleLeave(config.plugins.mytube.general.on_exit.value)
		else:
			self.hideSuggestions()
			self.handleLeave(config.plugins.mytube.general.on_exit.value)

	def leavePlayerConfirmed(self, answer):
		answer = answer and answer[1]
		if answer == "quit":
			self.doQuit()
		elif answer == "continue":
			if self.currList == "historylist":
				if self.HistoryWindow.status() is False:
					self.HistoryWindow.activate()
					self.HistoryWindow.instance.show()
			elif self.currList == "configlist":
				self.switchToConfigList()
			elif self.currList == "feedlist":
				self.switchToFeedList()				
		elif answer == "switch2feed":
			self.switchToFeedList()
		elif answer == "switch2search":
			self.switchToConfigList()
		elif answer == None:
			if self.currList == "historylist":
				if self.HistoryWindow.status() is False:
					self.HistoryWindow.activate()
					self.HistoryWindow.instance.show()
			elif self.currList == "configlist":
				self.switchToConfigList()
			elif self.currList == "feedlist":
				self.switchToFeedList()

	def doQuit(self):
		if self["config"].getCurrent()[1].suggestionsWindow is not None:
			self.session.deleteDialog(self["config"].getCurrent()[1].suggestionsWindow)
		if self.HistoryWindow is not None:
			self.session.deleteDialog(self.HistoryWindow)
		if config.plugins.mytube.general.showHelpOnOpen.value is True:
			config.plugins.mytube.general.showHelpOnOpen.value = False
			config.plugins.mytube.general.showHelpOnOpen.save()
		if not config.plugins.mytube.general.clearHistoryOnClose.value:
			if self.History and len(self.History):
				config.plugins.mytube.general.history.value = ",".join(self.History)
		else:
			config.plugins.mytube.general.history.value = ""
		config.plugins.mytube.general.history.save()
		config.plugins.mytube.general.save()
		config.plugins.mytube.save()
		self.cancelThread()
		self.close()
			
	def keyOK(self):
		print("self.currList im KeyOK",self.currList)
		if self.currList == "configlist" or self.currList == "suggestionslist":
			self["config"].invalidateCurrent()
			if config.plugins.mytube.search.searchTerm.value != "":
				self.add2History()
				searchContext = config.plugins.mytube.search.searchTerm.value
				print("Search searchcontext",searchContext)
				if isinstance(self["config"].getCurrent()[1], ConfigTextWithGoogleSuggestions) and not self.propagateUpDownNormally:
					self.propagateUpDownNormally = True
					self["config"].getCurrent()[1].deactivateSuggestionList()
				self.setState('getSearchFeed')
				self.runSearch(searchContext)
		elif self.currList == "feedlist":
			current = self[self.currList].getCurrent()
			if current:
				print(current)
				myentry = current[0]
				if myentry is not None:
					vtype = myentry.getType()
					if vtype == "youtube#video":
						myurl = myentry.getVideoUrl()
						print("Playing URL",myurl)
						if myurl is not None:
							if myurl == "age":
								self.session.open(MessageBox, _("Sorry, Video has age restriction!"), MessageBox.TYPE_INFO)
							elif myurl == "unavailable":
								self.session.open(MessageBox, _("Sorry, video is not available!"), MessageBox.TYPE_INFO)
							elif myurl == "format":
								self.session.open(MessageBox, _("Sorry, No supported formats found in video info!"), MessageBox.TYPE_INFO)
							else:
								myreference = eServiceReference(4097,0,myurl)
								myreference.setName(myentry.getTitle())
								self.session.openWithCallback(self.onPlayerClosed, MyTubePlayer, myreference, self.lastservice, infoCallback = self.showVideoInfo, nextCallback = self.getNextEntry, prevCallback = self.getPrevEntry )
						else:
							self.session.open(MessageBox, _("Sorry, video is not available!"), MessageBox.TYPE_INFO)
					elif vtype == "youtube#channel":
						self.setState('getFeed')
						self.appendEntries = False
						self.getFeed(myentry.getTubeId(),"channel")
		elif self.currList == "historylist":
			if self.HistoryWindow is not None:
				config.plugins.mytube.search.searchTerm.value = self.HistoryWindow.getSelection()
			self["config"].invalidateCurrent()
			if config.plugins.mytube.search.searchTerm.value != "":
				searchContext = config.plugins.mytube.search.searchTerm.value
				print("Search searchcontext",searchContext)
				self.setState('getSearchFeed')
				self.runSearch(searchContext)

	def onPlayerClosed(self):
		if config.plugins.mytube.general.resetPlayService.value is True:
			self.session.nav.playService(self.lastservice)

	def toggleScreenVisibility(self):
		if self.shown is True:
			self.hide()
		else:
			self.show()

	def keyUp(self):
		print("self.currList im KeyUp",self.currList)
		if self.currList == "suggestionslist":
			if config.plugins.mytube.search.searchTerm.value != "":
				if not self.propagateUpDownNormally:
					self["config"].getCurrent()[1].suggestionListUp()
					self["config"].invalidateCurrent()
		elif self.currList == "feedlist":
			self[self.currList].selectPrevious()
		elif self.currList == "historylist":
			if self.HistoryWindow is not None and self.HistoryWindow.shown:
				self.HistoryWindow.up()

	def keyDown(self):
		print("self.currList im KeyDown",self.currList)
		if self.currList == "suggestionslist":
			if config.plugins.mytube.search.searchTerm.value != "":
				if not self.propagateUpDownNormally:
					self["config"].getCurrent()[1].suggestionListDown()
					self["config"].invalidateCurrent()
		elif self.currList == "feedlist":
			print(self[self.currList].count())
			print(self[self.currList].index)
			if self[self.currList].index == self[self.currList].count()-1 and myTubeService.getNextFeedEntriesURL() is not None:
				# load new feeds on last selected item
				if config.plugins.mytube.general.AutoLoadFeeds.value is False:
					self.session.openWithCallback(self.getNextEntries, MessageBox, _("Do you want to see more entries?"))
				else:
					self.getNextEntries(True)
			else:
				self[self.currList].selectNext()
		elif self.currList == "historylist":
			if self.HistoryWindow is not None and self.HistoryWindow.shown:
				self.HistoryWindow.down()
	def keyRight(self):
		print("self.currList im KeyRight",self.currList)
		if self.propagateUpDownNormally:
			ConfigListScreen.keyRight(self)
		else:
			if self.currList == "suggestionslist":
				if config.plugins.mytube.search.searchTerm.value != "":
					self["config"].getCurrent()[1].suggestionListPageDown()
					self["config"].invalidateCurrent()
			elif self.currList == "historylist":
				if self.HistoryWindow is not None and self.HistoryWindow.shown:
					self.HistoryWindow.pageDown()

	def keyLeft(self):
		print("self.currList im kEyLeft",self.currList)
		if self.propagateUpDownNormally:
			ConfigListScreen.keyLeft(self)
		else:
			if self.currList == "suggestionslist":
				if config.plugins.mytube.search.searchTerm.value != "":
					self["config"].getCurrent()[1].suggestionListPageUp()
					self["config"].invalidateCurrent()
			elif self.currList == "historylist":
				if self.HistoryWindow is not None and self.HistoryWindow.shown:
					self.HistoryWindow.pageDown()
					
	def keyStdFeed(self):
		self.hideSuggestions()
		menulist = []
		
		if myTubeService.is_auth() is True:
			menulist.extend((
				(_("My Subscriptions"), "my_subscriptions"),
				(_("My Favorites"), "my_favorites"),
				(_("My Uploads"), "my_uploads"),
				(_("My videos likes"),"my_likes"),


			))

		menulist.extend((
			(_("Top rated"), "top_rated"),
			(_("Most viewed"), "most_viewed"),
			(_("Film & Animation"), "1"),
			(_("Autos & Vehicles"), "2"),
			(_("Music"), "10"),
			(_("Pets & Animals"), "15"),
			(_("Sports"), "17"),
			(_("Short Movies"), "18"),
			(_("Travel & Events"), "19"),
			(_("Gaming"), "20"),
			(_("Videoblogs"), "21"),
			(_("People & Blogs"), "22"),
			(_("Comedy"), "23"),
			(_("Entertainment"), "24"),
			(_("News & Politic"), "25"),
			(_("Howto & Style"), "26"),
			(_("Education"), "27"),
			(_("Science & Technology"), "28")
		))
		self.session.openWithCallback(self.openStandardFeedClosed, ChoiceBox, title=_("Select new feed to view."), list = menulist)

	def handleSuggestions(self):
		print("handleSuggestions")
		print("self.currList",self.currList)
		if self.currList == "configlist":
			self.switchToSuggestionsList()
		elif self.currList == "historylist":
			if self.HistoryWindow is not None and self.HistoryWindow.shown:
				self.HistoryWindow.down()

	def switchToSuggestionsList(self):
		print("switchToSuggestionsList")
		self.currList = "suggestionslist"
		self["ButtonBlue"].hide()
		self["VKeyIcon"].hide()	
		self["statusactions"].setEnabled(False)
		self["config_actions"].setEnabled(False)	
		self["videoactions"].setEnabled(False)
		self["searchactions"].setEnabled(False)
		self["suggestionactions"].setEnabled(True)
		self["historyactions"].setEnabled(False)
		self["key_green"].hide()
		self.propagateUpDownNormally = False
		self["config"].invalidateCurrent()
		if self.HistoryWindow is not None and self.HistoryWindow.shown:
			self.HistoryWindow.deactivate()
			self.HistoryWindow.instance.hide()
	
	def switchToConfigList(self):
		print("switchToConfigList")
		self.currList = "configlist"
		self["config_actions"].setEnabled(True)	
		self["historyactions"].setEnabled(False)
		self["statusactions"].setEnabled(False)
		self["videoactions"].setEnabled(False)
		self["suggestionactions"].setEnabled(False)
		self["searchactions"].setEnabled(True)
		self["key_green"].hide()
		self["ButtonBlue"].show()
		self["VKeyIcon"].show()
		self["config"].invalidateCurrent()
		helpwindowpos = self["HelpWindow"].getPosition()
		current = self["config"].getCurrent()
		if current[1].help_window.instance is not None:
			current[1].help_window.instance.move(ePoint(helpwindowpos[0],helpwindowpos[1]))
			current[1].help_window.instance.show()
		if current[1].suggestionsWindow.instance is not None:
			current[1].suggestionsWindow.instance.show()
			self["config"].getCurrent()[1].getSuggestions()
		self.propagateUpDownNormally = True
		if self.HistoryWindow is not None and self.HistoryWindow.shown:
			self.HistoryWindow.deactivate()
			self.HistoryWindow.instance.hide()
		if self.FirstRun == True:
			self.handleFirstHelpWindow()

	def switchToFeedList(self, append = False):
		print("switchToFeedList")
		print("switching to feedlist from:",self.currList)
		print("len(self.videolist):",len(self.videolist))
		if self.HistoryWindow is not None and self.HistoryWindow.shown:
			self.HistoryWindow.deactivate()
			self.HistoryWindow.instance.hide()
		self.hideSuggestions()
		if len(self.videolist):
			self.currList = "feedlist"
			self["ButtonBlue"].hide()
			self["VKeyIcon"].hide()	
			self["videoactions"].setEnabled(True)
			self["suggestionactions"].setEnabled(False)
			self["searchactions"].setEnabled(False)
			self["statusactions"].setEnabled(False)
			self["historyactions"].setEnabled(False)
			self["key_green"].show()
			self["config_actions"].setEnabled(False)
			if not append:
				self[self.currList].setIndex(0)
			self["feedlist"].updateList(self.videolist)
		else:
			self.setState('noVideos')


	def switchToHistory(self):
		print("switchToHistory")
		self.oldlist = self.currList
		self.currList = "historylist"
		print("switchToHistory currentlist",self.currList)
		print("switchToHistory oldlist",self.oldlist)
		self.hideSuggestions()
		self["ButtonBlue"].hide()
		self["VKeyIcon"].hide()	
		self["key_green"].hide()
		self["videoactions"].setEnabled(False)
		self["suggestionactions"].setEnabled(False)
		self["searchactions"].setEnabled(False)
		self["statusactions"].setEnabled(False)
		self["config_actions"].setEnabled(False)
		self["historyactions"].setEnabled(True)
		self.HistoryWindow.activate()
		self.HistoryWindow.instance.show()	

	def handleHistory(self):
		if self.HistoryWindow is None:
			self.HistoryWindow = self.session.instantiateDialog(MyTubeHistoryScreen)
		if self.currList in ("configlist","feedlist"):
			if self.HistoryWindow.status() is False:
				print("status is FALSE,switchToHistory")
				self.switchToHistory()
		elif self.currList == "historylist":
			self.closeHistory()

	def closeHistory(self):
		print("closeHistory currentlist",self.currList)
		print("closeHistory oldlist",self.oldlist)
		if self.currList == "historylist":
			if self.HistoryWindow.status() is True:
				print("status is TRUE, closing historyscreen")
				self.HistoryWindow.deactivate()
				self.HistoryWindow.instance.hide()
				if self.oldlist == "configlist":
					self.switchToConfigList()
				elif self.oldlist == "feedlist":
					self.switchToFeedList()

	def add2History(self):
		if self.History is None:
			self.History = config.plugins.mytube.general.history.value.split(',')
		if self.History[0] == '':
			del self.History[0]
		print("self.History im add",self.History)
		if config.plugins.mytube.search.searchTerm.value in self.History:
			self.History.remove((config.plugins.mytube.search.searchTerm.value))
		self.History.insert(0,(config.plugins.mytube.search.searchTerm.value))
		if len(self.History) == 30:
			self.History.pop()
		config.plugins.mytube.general.history.value = ",".join(self.History)
		config.plugins.mytube.general.history.save()
		print("configvalue",config.plugins.mytube.general.history.value)

	def hideSuggestions(self):
		current = self["config"].getCurrent()
		if current[1].help_window.instance is not None:
			current[1].help_window.instance.hide()	
		if current[1].suggestionsWindow.instance is not None:
			current[1].suggestionsWindow.instance.hide()
		self.propagateUpDownNormally = True

	def getFeed(self, feedUrl, feedName):
		try:
			current = self[self.currList].getCurrent()
		except:
			current = None
		name = None
		if current:
			print(current)
			myentry = current[0]
			if myentry is not None:
				name = myentry.getTitle()
		self.queryStarted()
		self.queryThread = myTubeService.getFeed(feedUrl, feedName, self.gotFeed, self.gotFeedError)
		if feedName in all_feeds:
			self["feed"].setText(all_feeds[feedName])
		if feedName == "channel" and name:
			self["feed"].setText(_("Channel")+": "+str(name))

		self.ytfeed = feedName

	def getNextEntries(self, result):
		if not result:
			return
		nextUrl = myTubeService.getNextFeedEntriesURL()
		if nextUrl is not None:
			self.appendEntries = True
			self.getFeed(nextUrl, _("More video entries."))

	def getRelatedVideos(self, myentry):
		if myentry:
			myurl =  myentry.getTubeId()
			print("TubeID--->",myurl)
			if myurl is not None:
				self.appendEntries = False
				self.getFeed(myurl, _("Related video entries."))

	def getResponseVideos(self, myentry):
		if myentry:
			myurl =  myentry.getResponseVideos()
			print("RESPONSEURL--->",myurl)
			if myurl is not None:
				self.appendEntries = False
				self.getFeed(myurl, _("Response video entries."))
				
	def getUserVideos(self, myentry):
		if myentry:
			myurl =  myentry.getChannelID()
			print("ChannelID--->",myurl)
			if myurl is not None:
				self.appendEntries = False
				self.getFeed(myurl, _("User video entries."))

	def runSearch(self, searchContext = None):
		print("[MyTubePlayer] runSearch")
		if searchContext is not None:
			print("[MyTubePlayer] searchDialogClosed: ", searchContext)
			self.searchFeed(searchContext)

	def searchFeed(self, searchContext, vals = None):
		print("[MyTubePlayer] searchFeed")		
		
		defaults = {
			'time': config.plugins.mytube.search.time.value,
			'orderby': config.plugins.mytube.search.orderBy.value,
			'startIndex': 1,
			'maxResults': 25,
		}

		# vals can overwrite default values; so search parameter are overwritable on function call
		if vals is not None:
			defaults.update(vals)

		self.queryStarted()		
		self.appendEntries = False
		self.queryThread = myTubeService.search(searchContext, 
					orderby = defaults['orderby'],
					time = defaults['time'],
					maxResults = defaults['maxResults'],
					startIndex = defaults['startIndex'],
					lr = config.plugins.mytube.search.lr.value,
					categories = [ config.plugins.mytube.search.categories.value ],
					sortOrder = config.plugins.mytube.search.sortOrder.value,
					callback = self.gotSearchFeed, errorback = self.gotSearchFeedError)
	
	def queryStarted(self):
		if self.queryRunning:
			self.cancelThread()
		self.queryRunning = True		
	
	def queryFinished(self):
		self.queryRunning = False
	
	def cancelThread(self):
		print("[MyTubePlayer] cancelThread")
		if self.queryThread is not None:
			self.queryThread.cancel()
		self.queryFinished()
	
	def gotFeed(self, feed):
		print("[MyTubePlayer] gotFeed")
		self.queryFinished()
		#if feed is not None:
		#	self.ytfeed = feed
		self.buildEntryList()
		text = _("Results:") +" %s - " % str(myTubeService.getTotalResults()) + _("Page:") + " %s " % str(myTubeService.getCurrentPage())
		
		#auth_username = myTubeService.getAuthedUsername()
		#if auth_username:
		#	text = auth_username + ' - ' + text
		
		self["result"].setText(text)
	
	def gotFeedError(self, exception):
		print("[MyTubePlayer] gotFeedError")
		self.queryFinished()
		self.setState('Error')
	
	def gotSearchFeed(self, feed):
		if self.FirstRun:	
			self.FirstRun = False
		self.ytfeed = feed
		self["feed"].setText(_("Search results"))
		self.gotFeed(feed)
	
	def gotSearchFeedError(self, exception):
		if self.FirstRun:	
			self.FirstRun = False
		self.gotFeedError(exception)
	
	def buildEntryList(self):
		self.mytubeentries = None
		self.screenshotList = []
		self.maxentries = 0
		self.mytubeentries = myTubeService.getEntries()
		self.maxentries = len(self.mytubeentries)-1
		if self.mytubeentries and len(self.mytubeentries):
			if self.appendEntries == False:
				self.videolist = []
				for entry in self.mytubeentries:
					TubeID = entry.getTubeId()
					thumbnailUrl = None
					thumbnailUrl = entry.getThumbnailUrl(0)				
					if thumbnailUrl is not None:
						self.screenshotList.append((TubeID,thumbnailUrl))
					if TubeID not in self.Details:
						self.Details[TubeID] = { 'thumbnail': None}
#					if entry.getType() == "youtube#video" or self.ytfeed == "my_subscriptions" or (entry.getType() == "youtube#channel" and entry.getlive() == "upcoming"):
					self.videolist.append(self.buildEntryComponent(entry, TubeID))
				if len(self.videolist):
					self["feedlist"].style = "default"
					self["feedlist"].disable_callbacks = True
					self["feedlist"].list = self.videolist
					self["feedlist"].disable_callbacks = False
					self["feedlist"].setIndex(0)
					self["feedlist"].setList(self.videolist)
					self["feedlist"].updateList(self.videolist)
					if self.FirstRun and not config.plugins.mytube.general.loadFeedOnOpen.value:
						self.switchToConfigList()
					else:
						self.switchToFeedList()
			else:		
				self.oldfeedentrycount = self["feedlist"].count()
				for entry in self.mytubeentries:
					TubeID = entry.getTubeId()
					thumbnailUrl = None
					thumbnailUrl = entry.getThumbnailUrl(0)				
					if thumbnailUrl is not None:
						self.screenshotList.append((TubeID,thumbnailUrl))
					if TubeID not in self.Details:
						self.Details[TubeID] = { 'thumbnail': None}
					if entry.getType() == "youtube#video" or self.ytfeed == "my_subscriptions" or (entry.getType() == "youtube#channel" and entry.getlive() == "upcoming"):
						self.videolist.append(self.buildEntryComponent(entry, TubeID))
				if len(self.videolist):
					self["feedlist"].style = "default"
					old_index = self["feedlist"].index
					self["feedlist"].disable_callbacks = True
					self["feedlist"].list = self.videolist
					self["feedlist"].disable_callbacks = False
					self["feedlist"].setList(self.videolist)
					self["feedlist"].setIndex(old_index)
					self["feedlist"].updateList(self.videolist)
					self["feedlist"].selectNext()
					self.switchToFeedList(True)
			if not self.timer_startDownload.isActive():
				print("STARRTDOWNLOADTIMER IM BUILDENTRYLIST")
				self.timer_startDownload.start(5)
		else:
			self.setState('Error')
			pass
	
	def buildEntryComponent(self, entry,TubeID):
		Title = entry.getTitle()
		print("Title-->",Title)
		Description = entry.getDescription()
		channel = entry.getAuthor()
		myTubeID = TubeID
		PublishedDate = entry.getPublishedDate()
		if PublishedDate is not "unknown":
			published = PublishedDate.split("T")[0]
		else:
			published = "unknown"
		vtype = entry.getType()
		tpng = None
		if vtype == "youtube#channel":
			channel = vtype
			if esHD():
				png = self.skin_path + "/img/channelHD.png"
			else:
				png = self.skin_path + "/img/channel.png"
			if fileExists(png, 'r'):
				tpng = LoadPixmap(png)


		#Views = entry.getViews()
		#if Views is not "not available":
		#	views = Views
		#else:
		#	views = "not available"
		#Duration = entry.getDuration()
		#if Duration is not 0:
		#	durationInSecs = int(Duration)
		#	mins = int(durationInSecs / 60)
		#	secs = durationInSecs - mins * 60
		#	duration = "%d:%02d" % (mins, secs)
		#else:
		#	duration = "not available"
		#Ratings = entry.getNumRaters()
		#if Ratings is not "":
		#	ratings = Ratings
		#else:
		#	ratings = ""
		thumbnail = None
		if self.Details[myTubeID]["thumbnail"]:
			thumbnail = self.Details[myTubeID]["thumbnail"]
		return((entry, Title, Description, myTubeID, thumbnail, _("Added: ") + str(published), _("by") + " " + str(channel),tpng))	

	def getNextEntry(self):
		i = self["feedlist"].getIndex() + 1
		if i < len(self.videolist):
			self["feedlist"].selectNext()
			current = self["feedlist"].getCurrent()
			if current:
				myentry = current[0]
				if myentry:
					myurl = myentry.getVideoUrl()
					if myurl is not None:
						print("Got a URL to stream")
						myreference = eServiceReference(4097,0,myurl)
						myreference.setName(myentry.getTitle())
						return myreference,False
					else:
						print("NoURL im getNextEntry")
						return None,True
						
		print("no more entries to play")
		return None,False

	def getPrevEntry(self):
		i = self["feedlist"].getIndex() - 1
		if i >= 0:
			self["feedlist"].selectPrevious()
			current = self["feedlist"].getCurrent()
			if current:
				myentry = current[0]
				if myentry:
					myurl = myentry.getVideoUrl()
					if myurl is not None:
						print("Got a URL to stream")
						myreference = eServiceReference(4097,0,myurl)
						myreference.setName(myentry.getTitle())
						return myreference,False
					else:
						return None,True
		return None,False

	def showVideoInfo(self):
		if self.currList == "feedlist":
			self.openInfoScreen()

	def openInfoScreen(self):
		if self.currList == "feedlist":
			current = self[self.currList].getCurrent()
			if current:
				myentry = current[0]
				if myentry.getType() == "youtube#video":
					print("Title im showVideoInfo",myentry.getTitle())
					videoinfos = myentry.PrintEntryDetails()
					self.session.open(MyTubeVideoInfoScreen, self.skin_path, videoinfo = videoinfos )

	def downloadThumbnails(self):
		self.timer_startDownload.stop()
		for entry in self.screenshotList:
			thumbnailUrl = entry[1]
			tubeid = entry[0]
			thumbnailFile = "/tmp/"+str(tubeid)+".jpg"
			if tubeid in self.Details:
				if self.Details[tubeid]["thumbnail"] is None:
					if thumbnailUrl is not None:
						if tubeid not in self.pixmaps_to_load:
							self.pixmaps_to_load.append(tubeid)
							if (os_path.exists(thumbnailFile) == True):
								self.fetchFinished(False,tubeid)
							else:
								client.downloadPage(thumbnailUrl.encode("utf-8"),thumbnailFile).addCallback(self.fetchFinished,str(tubeid)).addErrback(self.fetchFailed,str(tubeid))
					else:
						if tubeid not in self.pixmaps_to_load:
							self.pixmaps_to_load.append(tubeid)
							self.fetchFinished(False,tubeid, failed = True)

	def fetchFailed(self,string,tubeid):
		print("thumbnail-fetchFailed for: ",tubeid,string.getErrorMessage())
		self.fetchFinished(False,tubeid, failed = True)

	def fetchFinished(self,x,tubeid, failed = False):
		print("thumbnail-fetchFinished for:",tubeid)
		self.pixmaps_to_load.remove(tubeid)
		if failed:
			thumbnailFile = resolveFilename(SCOPE_CURRENT_PLUGIN, "Extensions/MyTube/plugin.png")
		else:
			thumbnailFile = "/tmp/"+str(tubeid)+".jpg"
		sc = AVSwitch().getFramebufferScale()
		if (os_path.exists(thumbnailFile) == True):
			self.picloads[tubeid] = ePicLoad()
			self.picloads[tubeid].PictureData.get().append(boundFunction(self.finish_decode, tubeid))
			self.picloads[tubeid].setPara((self["thumbnail"].instance.size().width(), self["thumbnail"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
			self.picloads[tubeid].startDecode(thumbnailFile)
		else:
			self.pixmaps_to_load.append(tubeid)
			self.fetchFinished(False,tubeid, failed = True)

	def finish_decode(self,tubeid,info):
		print("thumbnail finish_decode:", tubeid,info)
		ptr = self.picloads[tubeid].getData()
		thumbnailFile = "/tmp/"+str(tubeid)+".jpg"
		if ptr != None:
			if tubeid in self.Details:
				self.Details[tubeid]["thumbnail"] = ptr
			if (os_path.exists(thumbnailFile) == True):
				os_remove(thumbnailFile)
			del self.picloads[tubeid]
		else:
			del self.picloads[tubeid]
			if tubeid in self.Details:
				self.Details[tubeid]["thumbnail"] = None
		self.timer_thumbnails.start(1)

	def updateFeedThumbnails(self):
		self.timer_thumbnails.stop()
		if len(self.picloads) != 0:
			self.timer_thumbnails.start(1)
		else:
			idx = 0
			for entry in self.videolist:
				tubeid = entry[3]
				if tubeid in self.Details:
					if self.Details[tubeid]["thumbnail"] is not None:
						thumbnail = entry[4]
						if thumbnail == None:
							myentry = entry[0]
							self.videolist[idx] = self.buildEntryComponent(myentry, tubeid )
				idx += 1
			if self.currList == "feedlist":
				self["feedlist"].updateList(self.videolist)		


class MyTubeVideoInfoScreen(Screen):
	
	if esHD():
		skin = skinMyTubeVideoInfoScreenHD
	else:
		skin = skinMyTubeVideoInfoScreen

	def __init__(self, session, plugin_path, videoinfo = None):
		Screen.__init__(self, session)
		self.session = session
		self.skin_path = plugin_path
		self.videoinfo = videoinfo
		self.infolist = []
		self.thumbnails = []
		self.picloads = {}
		self["title"] = Label()
		self["key_red"] = Button(_("Close"))
		self["thumbnail"] = Pixmap()
		self["thumbnail"].hide()
		self["detailtext"] = ScrollLabel()
		self["like"] = Pixmap()
		self["dislike"] = Pixmap()
#		self["starsbg"] = Pixmap()
#		self["stars"] = ProgressBar()
		self["llike"] = Label()
		self["ldislike"] = Label()
		self["duration"] = Label()
		self["author"] = Label()
		self["published"] = Label()
		self["views"] = Label()
		self["tags"] = Label()
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "MovieSelectionActions", "DirectionActions"],
		{
			"back": self.close,
			"red": self.close,
			"up": self.pageUp,
			"down":	self.pageDown,
			"left":	self.pageUp,
			"right": self.pageDown,
		}, -2)
		
		self["infolist"] = List(self.infolist)
		self.timer = eTimer()
		self.timer.callback.append(self.picloadTimeout)
		self.onLayoutFinish.append(self.layoutFinished)
		self.onShown.append(self.setWindowTitle)

	def layoutFinished(self):
		self.statuslist = []
		self.statuslist.append(( _("Downloading screenshots. Please wait..." ),_("Downloading screenshots. Please wait..." ) ))
		self["infolist"].style = "state"
		self['infolist'].setList(self.statuslist)
		self.loadPreviewpics()		
		if self.videoinfo["Title"] is not None:
			self["title"].setText(self.videoinfo["Title"])
		self["llike"].setText(str(self.videoinfo["Rating"]))
		self["ldislike"].setText(str(self.videoinfo["DisRating"]))
		Description = None
		if self.videoinfo["Description"] is not None:
			Description = self.videoinfo["Description"]
		else:
			Description = None
		if Description is not None:
			self["detailtext"].setText(str(Description.strip()))

#		if self.videoinfo["RatingAverage"] is not 0:
#			ratingStars = int(round(20 * float(self.videoinfo["RatingAverage"]), 0))
#			self["stars"].setValue(ratingStars)
#		else:
#			self["stars"].hide()
#			self["starsbg"].hide()
		
		if self.videoinfo["Duration"] is not 0:
			durationInSecs = int(self.videoinfo["Duration"])
			mins = int(durationInSecs / 60)
			secs = durationInSecs - mins * 60
			duration = "%d:%02d" % (mins, secs)
			self["duration"].setText(_("Duration: ") + str(duration))
		
		if self.videoinfo["Author"] is not None or '':
			self["author"].setText(_("Author: ") + str(self.videoinfo["Author"]))

		if self.videoinfo["Published"] is not "unknown":
			self["published"].setText(_("Added: ") + str(self.videoinfo["Published"]).split("T")[0])
			
		if self.videoinfo["Views"] is not "not available":
			self["views"].setText(_("Views: ") + str(self.videoinfo["Views"]))

		if self.videoinfo["Tags"] is not "not available":
			self["tags"].setText(_("Tags: ") + str(self.videoinfo["Tags"]))

	def setWindowTitle(self):
		self.setTitle(_("MyTubeVideoInfoScreen"))

	def pageUp(self):
		self["detailtext"].pageUp()

	def pageDown(self):
		self["detailtext"].pageDown()

	def loadPreviewpics(self):
		self.thumbnails = []
		self.mythumbubeentries = None
		self.index = 0
		self.maxentries = 0
		self.picloads = {}
		self.mythumbubeentries = self.videoinfo["Thumbnails"]
		self.maxentries = len(self.mythumbubeentries)-1
		if self.mythumbubeentries and len(self.mythumbubeentries):
			currindex = 0
			for entry in self.mythumbubeentries:
				TubeID = self.videoinfo["TubeID"]
				ThumbID = TubeID + str(currindex)
				thumbnailFile = "/tmp/" + ThumbID + ".jpg"
				currPic = [currindex,ThumbID,thumbnailFile,None]
				self.thumbnails.append(currPic)
				thumbnailUrl = None
				thumbnailUrl = entry
				if thumbnailUrl is not None:
					client.downloadPage(thumbnailUrl.encode("utf-8"),thumbnailFile).addCallback(self.fetchFinished,currindex,ThumbID).addErrback(self.fetchFailed,currindex,ThumbID)
				currindex +=1
		else:
			pass

	def fetchFailed(self, string, index, id):
		print("[fetchFailed] for index:" + str(index) + "for ThumbID:" + id + string.getErrorMessage())

	def fetchFinished(self, string, index, id):
		print("[fetchFinished] for index:" + str(index) + " for ThumbID:" + id)
		self.decodePic(index)

	def decodePic(self, index):
		sc = AVSwitch().getFramebufferScale()
		self.picloads[index] = ePicLoad()
		self.picloads[index].PictureData.get().append(boundFunction(self.finish_decode, index))
		for entry in self.thumbnails:
			if entry[0] == index:
				self.index = index
				thumbnailFile = str(entry[2])
				if (os_path.exists(thumbnailFile) == True):
					print("[decodePic] DECODING THUMBNAIL for INDEX:"+  str(self.index) + "and file: " + thumbnailFile)
					self.picloads[index].setPara((self["thumbnail"].instance.size().width(), self["thumbnail"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
					self.picloads[index].startDecode(thumbnailFile)
				else:
					print("[decodePic] Thumbnail file NOT FOUND !!!-->:",thumbnailFile)

	def finish_decode(self, picindex = None, picInfo=None):
		print("finish_decode - of INDEX", picindex)
		ptr = self.picloads[picindex].getData()
		if ptr != None:
			self.thumbnails[picindex][3] = ptr
			if (os_path.exists(self.thumbnails[picindex][2]) == True):
				print("removing", self.thumbnails[picindex][2])
				os_remove(self.thumbnails[picindex][2])
				del self.picloads[picindex]
				if len(self.picloads) == 0:
					self.timer.startLongTimer(3)

	def picloadTimeout(self):
		self.timer.stop()
		if len(self.picloads) == 0:
				self.buildInfoList()
		else:
			self.timer.startLongTimer(2)

	def buildInfoList(self):
		self.infolist = []
		Thumbail0 = None
		Thumbail1 = None
		Thumbail2 = None
		Thumbail3 = None
		if self.thumbnails[0][3] is not None:
			Thumbail0 = self.thumbnails[0][3]
		if self.thumbnails[1][3] is not None:
			Thumbail1 = self.thumbnails[1][3]
		if self.thumbnails[2][3] is not None:
			Thumbail2 = self.thumbnails[2][3]
		if self.thumbnails[3][3] is not None:
			Thumbail3 = self.thumbnails[2][3]
		self.infolist.append(( Thumbail0, Thumbail1, Thumbail2, Thumbail3))
		if len(self.infolist):
			self["infolist"].style = "default"
			self["infolist"].disable_callbacks = True
			self["infolist"].list = self.infolist
			self["infolist"].disable_callbacks = False
			self["infolist"].setIndex(0)
			self["infolist"].setList(self.infolist)
			self["infolist"].updateList(self.infolist)


class MyTubeVideoHelpScreen(Screen):
	if esHD():
		skin = skinMyTubeVideoHelpScreenHD
	else:
		skin = skinMyTubeVideoHelpScreen
		
	def __init__(self, session, plugin_path, wantedinfo = None, wantedtitle = None):
		Screen.__init__(self, session)
		self.session = session
		self.skin_path = plugin_path
		self.wantedinfo = wantedinfo
		self.wantedtitle = wantedtitle
		self["title"] = Label()
		self["key_red"] = Button(_("Close"))
		self["detailtext"] = ScrollLabel()
		
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "DirectionActions"],
		{
			"back": self.close,
			"red": self.close,
			"up": self.pageUp,
			"down":	self.pageDown,
			"left":	self.pageUp,
			"right": self.pageDown,
		}, -2)
		
		self.onLayoutFinish.append(self.layoutFinished)
		self.onShown.append(self.setWindowTitle)

	def layoutFinished(self):
		if self.wantedtitle is None:
			self["title"].setText(_("Help"))
		else:
			self["title"].setText(self.wantedtitle)
		if self.wantedinfo is None:
			self["detailtext"].setText(_("This is the help screen. Feed me with something to display."))
		else:
			self["detailtext"].setText(self.wantedinfo)
	
	def setWindowTitle(self):
		self.setTitle(_("MyTubeVideohelpScreen"))

	def pageUp(self):
		self["detailtext"].pageUp()

	def pageDown(self):
		self["detailtext"].pageDown()

class MyTubePlayer(Screen, InfoBarNotifications, InfoBarSeek):
	STATE_IDLE = 0
	STATE_PLAYING = 1
	STATE_PAUSED = 2
	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True
	if esHD():
		skin = skinMyTubePlayerHD
	else:
		skin = skinMyTubePlayer

	def __init__(self, session, service, lastservice, infoCallback = None, nextCallback = None, prevCallback = None):
		Screen.__init__(self, session)
		InfoBarNotifications.__init__(self)
		InfoBarSeek.__init__(self)
		self.session = session
		self.service = service
		self.infoCallback = infoCallback
		self.nextCallback = nextCallback
		self.prevCallback = prevCallback
		self.screen_timeout = 5000
		self.nextservice = None

		print("evEOF=%d" % iPlayableService.evEOF)
		self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
			{
				iPlayableService.evSeekableStatusChanged: self.__seekableStatusChanged,
				iPlayableService.evStart: self.__serviceStarted,
				iPlayableService.evEOF: self.__evEOF,
			})
		
		self["actions"] = ActionMap(["OkCancelActions", "MediaPlayerSeekActions", "MediaPlayerActions", "MovieSelectionActions", "DirectionActions"],
		{
				"ok": self.ok,
				"cancel": self.leavePlayer,
				"stop": self.leavePlayer,
				"playpauseService": self.playpauseService,
				"seekFwd": self.playNextFile,
				"seekBack": self.playPrevFile,
				"showEventInfo": self.showVideoInfo,
				"right": self.keyright,
				"left": self.keyleft,
			}, -2)


		self.lastservice = lastservice

		self.hidetimer = eTimer()
		self.hidetimer.timeout.get().append(self.ok)
		self.returning = False

		self.state = self.STATE_PLAYING
		self.lastseekstate = self.STATE_PLAYING

		self.onPlayStateChanged = [ ]
		self.__seekableStatusChanged()
	
		self.play()
		self.onClose.append(self.__onClose)
		
	def __onClose(self):
		self.session.nav.stopService()

	def __evEOF(self):
		print("evEOF=%d" % iPlayableService.evEOF)
		print("Event EOF")
		self.pauseService()
		self.handleLeave(config.plugins.mytube.general.on_movie_EOF.value)

	def __setHideTimer(self):
		self.hidetimer.start(self.screen_timeout)

	def showInfobar(self):
		self.show()
		if self.state == self.STATE_PLAYING:
			self.__setHideTimer()
		else:
			pass

	def hideInfobar(self):
		self.hide()
		self.hidetimer.stop()


	def keyright(self):
		try:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TimeSleep/plugin.pyo") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TimeSleep/plugin.so") and config.plugins.TimeSleep.activar.value:
				from Plugins.Extensions.TimeSleep.plugin import timesleep
				timesleep(self, True)
			else:
				InfoBarSeek.seekFwdManual(self)
		except:
			InfoBarSeek.seekFwdManual(self)

	def keyleft(self):
		try:
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TimeSleep/plugin.pyo") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TimeSleep/plugin.so") and config.plugins.TimeSleep.activar.value:
				from Plugins.Extensions.TimeSleep.plugin import timesleep
				timesleep(self, False)
			else:
				InfoBarSeek.seekBackManual(self)
		except:
			InfoBarSeek.seekBackManual(self)

	def ok(self):
		if self.shown:
			self.hideInfobar()
		else:
			self.showInfobar()

	def showVideoInfo(self):
		if self.shown:
			self.hideInfobar()
		if self.infoCallback is not None:	
			self.infoCallback()

	def playNextFile(self):
		print("playNextFile")
		nextservice,error = self.nextCallback()
		print("nextservice--->",nextservice)
		if nextservice is None:
			self.handleLeave(config.plugins.mytube.general.on_movie_stop.value, error)
		else:
			self.playService(nextservice)
			self.showInfobar()

	def playPrevFile(self):
		print("playPrevFile")
		prevservice,error = self.prevCallback()
		if prevservice is None:
			self.handleLeave(config.plugins.mytube.general.on_movie_stop.value, error)
		else:
			self.playService(prevservice)
			self.showInfobar()

	def playagain(self):
		print("playagain")
		if self.state != self.STATE_IDLE:
			self.stopCurrent()
		self.play()
	
	def playService(self, newservice):
		if self.state != self.STATE_IDLE:
			self.stopCurrent()
		self.service = newservice
		self.play()

	def play(self):
		if self.state == self.STATE_PAUSED:
			if self.shown:
				self.__setHideTimer()	
		self.state = self.STATE_PLAYING
		self.session.nav.playService(self.service)
		if self.shown:
			self.__setHideTimer()

	def stopCurrent(self):
		print("stopCurrent")
		self.session.nav.stopService()
		self.state = self.STATE_IDLE

	def playpauseService(self):
		print("playpauseService")
		if self.state == self.STATE_PLAYING:
			self.pauseService()
		elif self.state == self.STATE_PAUSED:
			self.unPauseService()

	def pauseService(self):
		print("pauseService")
		if self.state == self.STATE_PLAYING:
			self.setSeekState(self.STATE_PAUSED)
		
	def unPauseService(self):
		print("unPauseService")
		if self.state == self.STATE_PAUSED:
			self.setSeekState(self.STATE_PLAYING)


	def getSeek(self):
		service = self.session.nav.getCurrentService()
		if service is None:
			return None

		seek = service.seek()

		if seek is None or not seek.isCurrentlySeekable():
			return None

		return seek

	def isSeekable(self):
		if self.getSeek() is None:
			return False
		return True

	def __seekableStatusChanged(self):
		print("seekable status changed!")
		if not self.isSeekable():
			self["SeekActions"].setEnabled(False)
			self.setSeekState(self.STATE_PLAYING)
		else:
			self["SeekActions"].setEnabled(True)
			print("seekable")

	def __serviceStarted(self):
		self.state = self.STATE_PLAYING
		self.__seekableStatusChanged()

	def setSeekState(self, wantstate, onlyGUI = False):
		print("setSeekState")
		if wantstate == self.STATE_PAUSED:
			print("trying to switch to Pause- state:",self.STATE_PAUSED)
		elif wantstate == self.STATE_PLAYING:
			print("trying to switch to playing- state:",self.STATE_PLAYING)
		service = self.session.nav.getCurrentService()
		if service is None:
			print("No Service found")
			return False
		pauseable = service.pause()
		if pauseable is None:
			print("not pauseable.")
			self.state = self.STATE_PLAYING

		if pauseable is not None:
			print("service is pausable")
			if wantstate == self.STATE_PAUSED:
				print("WANT TO PAUSE")
				pauseable.pause()
				self.state = self.STATE_PAUSED
				if not self.shown:
					self.hidetimer.stop()
					self.show()
			elif wantstate == self.STATE_PLAYING:
				print("WANT TO PLAY")
				pauseable.unpause()
				self.state = self.STATE_PLAYING
				if self.shown:
					self.__setHideTimer()

		for c in self.onPlayStateChanged:
			c(self.state)
		
		return True

	def handleLeave(self, how, error = False):
		self.is_closing = True
		if how == "ask":
			list = (
				(_("Yes"), "quit"),
				(_("No, but play video again"), "playagain"),
				(_("Yes, but play next video"), "playnext"),
				(_("Yes, but play previous video"), "playprev"),
			)
			if error is False:
				self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)
			else:
				self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("No playable video found! Stop playing this movie?"), list = list)
		else:
			self.leavePlayerConfirmed([True, how])

	def leavePlayer(self):
		self.handleLeave(config.plugins.mytube.general.on_movie_stop.value)

	def leavePlayerConfirmed(self, answer):
		answer = answer and answer[1]
		if answer == "quit":
			print('quited')
			self.close()
		elif answer == "playnext":
			self.playNextFile()
		elif answer == "playprev":
			self.playPrevFile()
		elif answer == "playagain":
			self.playagain()

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing :
			return
		self.handleLeave(config.usage.on_movie_eof.value)


def MyTubeMain(session, **kwargs):
#	l2 = False
#	l2cert = etpm.getCert(eTPM.TPMD_DT_LEVEL2_CERT)
#	if l2cert is None:
#		print("l2cert not found")
#		return
	
#	l2key = validate_cert(l2cert, rootkey)
#	if l2key is None:
#		print("l2cert invalid")
#		return
#	l2 = True
#	if l2:
	session.open(MyTubePlayerMainScreen)


def Plugins(**kwargs):
#	global plugin_path
#	plugin_path = path
	return PluginDescriptor(
		name=_("My TubePlayer"),
		description=_("Play YouTube movies"),
		where = [ PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU ],
		icon = "plugin.png", fnc = MyTubeMain)
