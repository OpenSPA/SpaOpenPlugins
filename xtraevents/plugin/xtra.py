# -*- coding: utf-8 -*-
# by digiteng...06.2020, 11.2020
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
import Tools.Notifications
import os, re, random, datetime
from Components.SelectionList import SelectionList, SelectionEntryComponent
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigText, ConfigInteger, ConfigSelectionNumber, ConfigDirectory
from Components.ConfigList import ConfigListScreen
from enigma import eTimer, eLabel, eServiceCenter, eServiceReference, ePixmap, eSize, ePoint, loadJPG, iServiceInformation, eEPGCache, getBestPlayableServiceReference, getDesktop
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.VirtualKeyBoard import VirtualKeyBoard
from PIL import Image, ImageDraw, ImageFilter
from Screens.LocationBox import LocationBox
import socket
import requests
import threading
from Components.ProgressBar import ProgressBar
from Screens.ChoiceBox import ChoiceBox
import shutil
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext
import os

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("xtraEvent", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/xtraEvent/locale/"))

def _(txt):
	t = gettext.dgettext("xtraEvent", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

desktop_size = getDesktop(0).size().width()
epgcache = eEPGCache.getInstance()

config.plugins.xtraEvent = ConfigSubsection()
config.plugins.xtraEvent.skinSelect = ConfigSelection(default = "default", choices = [("default"), ("skin_2"), ("skin_3")])
config.plugins.xtraEvent.loc = ConfigDirectory(default='')
config.plugins.xtraEvent.searchMOD = ConfigSelection(default = "Current Channel", choices = [("Bouquets"), ("Current Channel")])
# config.plugins.xtraEvent.searchNUMBER = ConfigSelectionNumber(0, 999, 1, default=0)
imglist = []
for i in range(0, 999):
	if i == 0:
		imglist.append(("0 EPG"))
	else:
		imglist.append(("%d" % i))
config.plugins.xtraEvent.searchNUMBER = ConfigSelection(default = "0 EPG", choices = imglist)

config.plugins.xtraEvent.timer = ConfigSelectionNumber(1, 168, 1, default=1)
config.plugins.xtraEvent.apis = ConfigYesNo(default = False)
config.plugins.xtraEvent.tmdbAPI = ConfigText(default="", visible_width=100, fixed_size=False)
config.plugins.xtraEvent.tvdbAPI = ConfigText(default="", visible_width=100, fixed_size=False)
config.plugins.xtraEvent.omdbAPI = ConfigText(default="", visible_width=100, fixed_size=False)
config.plugins.xtraEvent.fanartAPI = ConfigText(default="", visible_width=100, fixed_size=False)

config.plugins.xtraEvent.searchLang = ConfigText(default="en", visible_width=100, fixed_size=False)
config.plugins.xtraEvent.timerMod = ConfigYesNo(default = False)

config.plugins.xtraEvent.tmdb = ConfigYesNo(default = False)
config.plugins.xtraEvent.tvdb = ConfigYesNo(default = False)
config.plugins.xtraEvent.maze = ConfigYesNo(default = False)
config.plugins.xtraEvent.fanart = ConfigYesNo(default = False)

config.plugins.xtraEvent.poster = ConfigYesNo(default = False)
config.plugins.xtraEvent.banner = ConfigYesNo(default = False)
config.plugins.xtraEvent.backdrop = ConfigYesNo(default = False)
config.plugins.xtraEvent.info = ConfigYesNo(default = False)

config.plugins.xtraEvent.days = ConfigSelectionNumber (default = 30, stepwidth = 1, min = 00, max = 30, wraparound = True)
config.plugins.xtraEvent.opt_Images = ConfigYesNo(default = False)
config.plugins.xtraEvent.cnfg = ConfigYesNo(default = False)
config.plugins.xtraEvent.cnfgSel = ConfigSelection(default = "poster", choices = [("poster"), ("banner"), ("backdrop")])

config.plugins.xtraEvent.TMDBpostersize = ConfigSelection(default="w185", choices = [
	("w92", "92x138"), 
	("w154", "154x231"), 
	("w185", "185x278"), 
	("w342", "342x513"), 
	("w500", "500x750"), 
	("w780", "780x1170"), 
	("original", "ORIGINAL")])
config.plugins.xtraEvent.TVDBpostersize = ConfigSelection(default="thumbnail", choices = [
	("thumbnail", "340x500"), 
	("fileName", "original(680x1000)")])

config.plugins.xtraEvent.TMDBbackdropsize = ConfigSelection(default="w300", choices = [
	("w300", "300x170"), 
	("w780", "780x440"), 
	("w1280", "1280x720"),
	("original", "ORIGINAL")])

config.plugins.xtraEvent.TVDBbackdropsize = ConfigSelection(default="thumbnail", choices = [
	("thumbnail", "640x360"), 
	("fileName", "original(1920x1080)")])

config.plugins.xtraEvent.FANART_Poster_Resize = ConfigSelection(default="10", choices = [
	("10", "100x142"), 
	("5", "200x285"), 
	("3", "333x475"), 
	("2", "500x713"), 
	("1", "1000x1426")])

config.plugins.xtraEvent.FANART_Backdrop_Resize = ConfigSelection(default="10", choices = [
	("2", "original/2"), 
	("1", "original")])

config.plugins.xtraEvent.imdb_Poster_size = ConfigSelection(default="10", choices = [
	("185", "185x278"), 
	("344", "344x510"), 
	("500", "500x750")])

config.plugins.xtraEvent.PB = ConfigSelection(default="posters", choices = [
	("posters", "Poster"), 
	("backdrops", "Backdrop")])

config.plugins.xtraEvent.FanartSearchType = ConfigSelection(default="tv", choices = [
	('tv', 'TV'),
	('movies', 'MOVIE')])

class xtra(Screen, ConfigListScreen):

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		skin = None
		if desktop_size <= 1280:
			if config.plugins.xtraEvent.skinSelect.value == "default":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/xtra_720_default.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_2":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/xtra_720_2.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_3":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/xtra_720_3.xml"
		else:
			if config.plugins.xtraEvent.skinSelect.value == "default":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/xtra_1080_default.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_2":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/xtra_1080_2.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_3":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/xtra_1080_3.xml"
		with open(skin, 'r') as f:
			self.skin = f.read()

		list = []
		ConfigListScreen.__init__(self, list, session=session)

		self['key_red'] = Label(_('Close'))
		self['key_green'] = Label(_('Search'))
		self['key_yellow'] = Label(_('Delete files'))
#		self['key_blue'] = Label(_('Manual Search'))

		self["actions"] = ActionMap(["OkCancelActions", "SetupActions", "DirectionActions", "ColorActions", "EventViewActions", "VirtualKeyboardAction"],
		{
			"left": self.keyLeft,
			"down": self.keyDown,
			"up": self.keyUp,
			"right": self.keyRight,
			"red": self.exit,
			"green": self.search,
			"yellow": self.erasemenu,
#			"blue": self.ms,
			"cancel": self.exit,
			"ok": self.keyOK,
			"info": self.strg,
#			"menu": self.menuS
		},-1)
		
		self.setTitle(_("xtraEvent... 2.0"))
		self['status'] = Label()
		self['info'] = Label()
		self['storage'] = Label()
		self['gain'] = Label()
		self['finalsize'] = Label()
		self['int_statu'] = Label()
		self['info'].setText(" ")
		self['storage'].setText(" ")
		self['status'].setText(" ")
		self['gain'].setText(" ")
		self['finalsize'].setText(" ")
		self["help"] = StaticText()
		
		self.timer = eTimer()
		self.timer.callback.append(self.xtraList)
		self.onLayoutFinish.append(self.xtraList)
		self.intCheck()
		
	def intCheck(self):
		try:
			socket.setdefaulttimeout(2)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
			self['int_statu'].setText("●")
			# return True
		except:
			return False

	def strg(self):
		try:
			path_poster = pathLoc+ "poster/"
			path_banner = pathLoc+ "banner/"
			path_backdrop = pathLoc+ "backdrop/"
			path_info = pathLoc+ "infos/"
			
			folder_size1=sum([sum([os.path.getsize(os.path.join(path_poster, fname)) for fname in files]) for path_poster, folders, files in os.walk(path_poster)])
			posters_sz = "%0.1f" % (folder_size1/(1024*1024.0))
			poster_nmbr = len(os.listdir(path_poster))

			folder_size2=sum([sum([os.path.getsize(os.path.join(path_banner, fname)) for fname in files]) for path_banner, folders, files in os.walk(path_banner)])
			banners_sz = "%0.1f" % (folder_size2/(1024*1024.0))
			banner_nmbr = len(os.listdir(path_banner))

			folder_size3=sum([sum([os.path.getsize(os.path.join(path_backdrop, fname)) for fname in files]) for path_backdrop, folders, files in os.walk(path_backdrop)])
			backdrops_sz = "%0.1f" % (folder_size3/(1024*1024.0))
			backdrop_nmbr = len(os.listdir(path_backdrop))

			folder_size4=sum([sum([os.path.getsize(os.path.join(path_info, fname)) for fname in files]) for path_info, folders, files in os.walk(path_info)])
			infos_sz = "%0.1f" % (folder_size4/(1024*1024.0))
			info_nmbr = len(os.listdir(path_info))
			new_siz = (float(folder_size1) + float(folder_size2)+ float(folder_size3)+ float(folder_size4))
			new_size = "%0.1f" % (new_siz/(1024*1024.0))
			finalsize = (float(new_size))
			self['storage'].setText(_(" "))
			self['gain'].setText(_(" "))
			self['finalsize'].setText(_(" "))
			self['status'].setText(_("Storage ;"))
			self['info'].setText(_(
				"Poster : {} poster {} MB".format(poster_nmbr, posters_sz)+ 
				"\nBanner : {} banner {} MB".format(banner_nmbr, banners_sz)+
				"\nBackdrop : {} backdrop {} MB".format(backdrop_nmbr, backdrops_sz)+
				"\nInfo : {} info {} MB".format(info_nmbr, infos_sz)+
				"\n\n\nTotal : {} MB".format (new_size)))
		except:
			pass

	def keyOK(self):
		if self['config'].getCurrent()[1] is config.plugins.xtraEvent.loc:
			self.session.openWithCallback(self.pathSelected, LocationBox, text=_('Default Folder'), currDir=config.plugins.xtraEvent.loc.getValue(), minFree=100)

		if self['config'].getCurrent()[1] is config.plugins.xtraEvent.cnfgSel:
			self.compressImg()

	def pathSelected(self, res):
		if res is not None:
			config.plugins.xtraEvent.loc.value = res
			pathLoc = config.plugins.xtraEvent.loc.value + "xtraEvent/"
			if not os.path.isdir(pathLoc):
				os.makedirs(pathLoc + "poster")
				os.makedirs(pathLoc + "banner")
				os.makedirs(pathLoc + "backdrop")
				os.makedirs(pathLoc + "infos")
				self.exit()

	def delay(self):
		self.timer.start(100, True)

	def xtraList(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()
		list = []
		list.append(getConfigListEntry("—"*100))
# CONFIG_________________________________________________________________________________________________________________
		list.append(getConfigListEntry ("CONFIG MENU", config.plugins.xtraEvent.cnfg, _("adjust your settings and close ... your settings are valid ...")))
		list.append(getConfigListEntry("—"*100))
		if config.plugins.xtraEvent.cnfg.value:
			list.append(getConfigListEntry("	LOCALIZACION", config.plugins.xtraEvent.loc, _("'OK' select location downloads...")))
			list.append(getConfigListEntry("	SKIN", config.plugins.xtraEvent.skinSelect, _("* reOpen plugin...")))
			list.append(getConfigListEntry (" 	ELIMINA ARCHIVOS", config.plugins.xtraEvent.days, _("delete files older than (days)")))
			list.append(getConfigListEntry("	OPTIMIZA IMAGENES", config.plugins.xtraEvent.opt_Images, _("optimize images...")))
			if config.plugins.xtraEvent.opt_Images.value:
				list.append(getConfigListEntry("\tSELECCIONA IMAGENES A OPTIMIZAR", config.plugins.xtraEvent.cnfgSel, _("'OK' select for optimize images...")))
			list.append(getConfigListEntry("	TUS API'S", config.plugins.xtraEvent.apis, _("...")))
			if config.plugins.xtraEvent.apis.value:
				list.append(getConfigListEntry("	TMDB API", config.plugins.xtraEvent.tmdbAPI, _("enter your own api key...")))
				list.append(getConfigListEntry("	TVDB API", config.plugins.xtraEvent.tvdbAPI, _("enter your own api key...")))
				list.append(getConfigListEntry("	OMDB API", config.plugins.xtraEvent.omdbAPI, _("enter your own api key...")))
				list.append(getConfigListEntry("	FANART API", config.plugins.xtraEvent.fanartAPI, _("enter your own api key...")))
			list.append(getConfigListEntry("—"*100))

			list.append(getConfigListEntry("	MODO BUSQUEDA", config.plugins.xtraEvent.searchMOD, _("select search mode...")))		
			list.append(getConfigListEntry("	BUSCAR SIGUIENTES EVENTOS", config.plugins.xtraEvent.searchNUMBER, _("enter the number of next events...")))

			list.append(getConfigListEntry("	LENGUAJE DE BUSQUEDA", config.plugins.xtraEvent.searchLang, _("select search language...")))
			list.append(getConfigListEntry("	TEMPORIZADOR", config.plugins.xtraEvent.timerMod, _("select timer update for events..")))
			if config.plugins.xtraEvent.timerMod.value == True:
				list.append(getConfigListEntry("\tTEMPORIZADOR(horas)", config.plugins.xtraEvent.timer, _("..."),))
		list.append(getConfigListEntry("—"*100))
		list.append(getConfigListEntry("FUENTES IMAGENES"))
		list.append(getConfigListEntry("—"*100))

# poster__________________________________________________________________________________________________________________
		list.append(getConfigListEntry("POSTER", config.plugins.xtraEvent.poster, _("active poster download")))
		if config.plugins.xtraEvent.poster.value == True:
			list.append(getConfigListEntry("\tTMDB", config.plugins.xtraEvent.tmdb, _("source for poster..."),))
			if config.plugins.xtraEvent.tmdb.value :
				list.append(getConfigListEntry("\tTMDB TAMAÑO DE POSTER", config.plugins.xtraEvent.TMDBpostersize, _(" ")))
				list.append(getConfigListEntry("-"*100))
			list.append(getConfigListEntry("\tTVDB", config.plugins.xtraEvent.tvdb, _("source for poster...")))
			if config.plugins.xtraEvent.tvdb.value :
				list.append(getConfigListEntry("\tTVDB TAMAÑO DE POSTER", config.plugins.xtraEvent.TVDBpostersize, _(" ")))
				list.append(getConfigListEntry("_"*100))
			list.append(getConfigListEntry("\tFANART", config.plugins.xtraEvent.fanart, _("source for poster...")))	
			if config.plugins.xtraEvent.fanart.value:
				list.append(getConfigListEntry("\tFANART TAMAÑO DE POSTER", config.plugins.xtraEvent.FANART_Poster_Resize, _(" ")))
				list.append(getConfigListEntry("—"*100))
			list.append(getConfigListEntry("\tMAZE(TV SHOWS)", config.plugins.xtraEvent.maze, _("source for poster...")))
# banner__________________________________________________________________________________________________________________
		list.append(getConfigListEntry("BANNER", config.plugins.xtraEvent.banner, _("active banner download")))

# backdrop_______________________________________________________________________________________________________________
		list.append(getConfigListEntry("BACKDROP", config.plugins.xtraEvent.backdrop, _("active backdrop download")))
		if config.plugins.xtraEvent.backdrop.value == True:
			list.append(getConfigListEntry("\tTMDB", config.plugins.xtraEvent.tmdb, _("source for backdrop...")))
			if config.plugins.xtraEvent.tmdb.value :
				list.append(getConfigListEntry("\tTMDB TAMAÑO DE BACKDROP", config.plugins.xtraEvent.TMDBbackdropsize, _(" ")))
				list.append(getConfigListEntry("_"*100))
			list.append(getConfigListEntry("\tTVDB", config.plugins.xtraEvent.tvdb, _("source for backdrop...")))
			if config.plugins.xtraEvent.tvdb.value :
				list.append(getConfigListEntry("\tTVDB TAMAÑO DE BACKDROP", config.plugins.xtraEvent.TVDBbackdropsize, _(" ")))
				list.append(getConfigListEntry("_"*100))
			list.append(getConfigListEntry("\tFANART", config.plugins.xtraEvent.fanart, _("source for backdrop...")))
			if config.plugins.xtraEvent.fanart.value:
				list.append(getConfigListEntry("\tFANART TAMAÑO DE BACKDROP", config.plugins.xtraEvent.FANART_Backdrop_Resize, _("resize of backdrop")))
				list.append(getConfigListEntry("_"*100))
			list.append(getConfigListEntry("—"*100))
# info___________________________________________________________________________________________________________________
		list.append(getConfigListEntry("INFO", config.plugins.xtraEvent.info, _("Program information with OMDB...")))
		list.append(getConfigListEntry("—"*100))

		self["config"].list = list
		self["config"].l.setList(list)
		self.help()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.delay()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.delay()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.delay()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.delay()

	def pageUp(self):
		self["config"].instance.moveSelection(self["config"].instance.pageDown)
		self.delay()

	def pageDown(self):
		self["config"].instance.moveSelection(self["config"].instance.pageUp)
		self.delay()

	def help(self):
		cur = self["config"].getCurrent()
		if cur:
			self["help"].text = cur[2]

	def erasemenu(self):
		list = [(_('Delete files...Older(days)'), self.erase), (_('Broken Images Remove'), self.brokenImageRemove), (_('Delete infos files of daily limit exceeded (OMDb)'), self.Removelimit) , (_('No(Exit)'), self.exit)]
		self.session.openWithCallback(self.menuCallback, ChoiceBox, title=_('XtraEvent Delete Menu...'), list=list)

	def compressImg(self):
		import sys
		self['storage'].setText(_(" "))
		self['gain'].setText(_(" "))
		self['finalsize'].setText(_(" "))
		filepath = pathLoc + config.plugins.xtraEvent.cnfgSel.value
		folder_size = sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
		old_size = "%0.1f" % (folder_size/(1024*1024.0))
		if os.path.exists(filepath):
			lstdr = os.listdir(filepath)
			for j in lstdr:
				try:
					if os.path.isfile(filepath+"/"+j):
						im = Image.open(filepath+"/"+j)
						im.save(filepath+"/"+j, optimize=True, quality=75)
				except:
					pass
			folder_size = sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
			new_size = "%0.1f" % (folder_size/(1024*1024.0))
			finalsize = (float(old_size) - float(new_size))
			self.strg()
			self['status'].setText(_("Total Images Optimized : ") + "{}".format(len(lstdr)))
			self['gain'].setText(_("Gain : ") + "{}MB. ↪️ {}MB.".format (finalsize,old_size))
			self['finalsize'].setText(_("Final Size : ") + "{}MB".format (new_size))

	def Removelimit(self):
		rmvd = 0
		path = [pathLoc+'infos']
		for folder in path :
			print(folder)
			llista = os.listdir(folder)
			for file in llista:
#				print(file)
				archivo = folder + os.sep + file
				estado = os.stat(archivo)
				if estado.st_size == 56:
					os.remove(archivo)
					rmvd += 1
				else:
					pass
		self['storage'].setText(_(" "))
		self['gain'].setText(_(" "))
		self['finalsize'].setText(_(" "))
		self.strg()
		self['status'].setText(_("Removed limit execedeed Infos : ") + "{}".format(str(rmvd)))


	def brokenImageRemove(self):
		self['storage'].setText(_(" "))
		self['gain'].setText(_(" "))
		self['finalsize'].setText(_(" "))
		b = os.listdir(pathLoc)
		path_poster = pathLoc+ "poster/"
		path_banner = pathLoc+ "banner/"
		path_backdrop = pathLoc+ "backdrop/"
		path_info = pathLoc+ "infos/"
		folder_size1=sum([sum([os.path.getsize(os.path.join(path_poster, fname)) for fname in files]) for path_poster, folders, files in os.walk(path_poster)])
		posters_sz = "%0.1f" % (folder_size1/(1024*1024.0))
		poster_nmbr = len(os.listdir(path_poster))
		folder_size2=sum([sum([os.path.getsize(os.path.join(path_banner, fname)) for fname in files]) for path_banner, folders, files in os.walk(path_banner)])
		banners_sz = "%0.1f" % (folder_size2/(1024*1024.0))
		banner_nmbr = len(os.listdir(path_banner))
		folder_size3=sum([sum([os.path.getsize(os.path.join(path_backdrop, fname)) for fname in files]) for path_backdrop, folders, files in os.walk(path_backdrop)])
		backdrops_sz = "%0.1f" % (folder_size3/(1024*1024.0))
		backdrop_nmbr = len(os.listdir(path_backdrop))
		folder_size4=sum([sum([os.path.getsize(os.path.join(path_info, fname)) for fname in files]) for path_info, folders, files in os.walk(path_info)])
		infos_sz = "%0.1f" % (folder_size4/(1024*1024.0))
		info_nmbr = len(os.listdir(path_info))
		old_siz = (float(folder_size1) + float(folder_size2)+ float(folder_size3)+ float(folder_size4))
		old_size = "%0.1f" % (old_siz/(1024*1024.0))
		rmvd = 0
		try:
			for i in b:
				bb = pathLoc + "{}/".format(i)
				fc = os.path.isdir(bb)
				if fc != False:	
					for f in os.listdir(bb):
						if f.endswith('.jpg'):
							try:
								img = Image.open(bb+f)
								img.verify()
							except:
								try:
									os.remove(bb+f)
									rmvd += 1
								except:
									pass
		except:
			pass
		folder_size1=sum([sum([os.path.getsize(os.path.join(path_poster, fname)) for fname in files]) for path_poster, folders, files in os.walk(path_poster)])
		posters_sz = "%0.1f" % (folder_size1/(1024*1024.0))
		poster_nmbr = len(os.listdir(path_poster))
		folder_size2=sum([sum([os.path.getsize(os.path.join(path_banner, fname)) for fname in files]) for path_banner, folders, files in os.walk(path_banner)])
		banners_sz = "%0.1f" % (folder_size2/(1024*1024.0))
		banner_nmbr = len(os.listdir(path_banner))
		folder_size3=sum([sum([os.path.getsize(os.path.join(path_backdrop, fname)) for fname in files]) for path_backdrop, folders, files in os.walk(path_backdrop)])
		backdrops_sz = "%0.1f" % (folder_size3/(1024*1024.0))
		backdrop_nmbr = len(os.listdir(path_backdrop))
		folder_size4=sum([sum([os.path.getsize(os.path.join(path_info, fname)) for fname in files]) for path_info, folders, files in os.walk(path_info)])
		infos_sz = "%0.1f" % (folder_size4/(1024*1024.0))
		info_nmbr = len(os.listdir(path_info))
		new_siz = (float(folder_size1) + float(folder_size2)+ float(folder_size3)+ float(folder_size4))
		new_size = "%0.1f" % (new_siz/(1024*1024.0))
		finalsize = (float(old_size) - float(new_size))
		self.strg()
		self['status'].setText(_("Removed Broken Images : ") + "{}".format(str(rmvd)))
		self['gain'].setText(_("Gain : ") + "{}MB. ↪️ {}MB.".format (finalsize,old_size))
#		self['finalsize'].setText(_("Final Size : ") + "{}MB".format (new_size))

	def menuCallback(self, ret = None):
		ret and ret[1]()

	def search(self):
		from . import download
		if config.plugins.xtraEvent.searchMOD.value == "Current Channel":
			self.session.open(download.downloads)
		if config.plugins.xtraEvent.searchMOD.value == "Bouquets":
			self.session.open(selBouquets)

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()
		configfile.save()
		self.close()

	def erase(self):
		try:
			import sys
			self['storage'].setText(_(" "))
			self['gain'].setText(_(" "))
			self['finalsize'].setText(_(" "))
			rmvd = 0
			path = [pathLoc+'poster', pathLoc+'banner', pathLoc+'infos', pathLoc+'backdrop']
			path_poster = pathLoc+ "poster/"
			path_banner = pathLoc+ "banner/"
			path_backdrop = pathLoc+ "backdrop/"
			path_info = pathLoc+ "infos/"
			formato = '%d-%m-%y'
			hoy = datetime.datetime.now()
			daysn = config.plugins.xtraEvent.days.value
			dia = hoy - datetime.timedelta(days=daysn)
			print(hoy)
			print(dia)
			folder_size1=sum([sum([os.path.getsize(os.path.join(path_poster, fname)) for fname in files]) for path_poster, folders, files in os.walk(path_poster)])
			posters_sz = "%0.1f" % (folder_size1/(1024*1024.0))
			poster_nmbr = len(os.listdir(path_poster))
			folder_size2=sum([sum([os.path.getsize(os.path.join(path_banner, fname)) for fname in files]) for path_banner, folders, files in os.walk(path_banner)])
			banners_sz = "%0.1f" % (folder_size2/(1024*1024.0))
			banner_nmbr = len(os.listdir(path_banner))
			folder_size3=sum([sum([os.path.getsize(os.path.join(path_backdrop, fname)) for fname in files]) for path_backdrop, folders, files in os.walk(path_backdrop)])
			backdrops_sz = "%0.1f" % (folder_size3/(1024*1024.0))
			backdrop_nmbr = len(os.listdir(path_backdrop))
			folder_size4=sum([sum([os.path.getsize(os.path.join(path_info, fname)) for fname in files]) for path_info, folders, files in os.walk(path_info)])
			infos_sz = "%0.1f" % (folder_size4/(1024*1024.0))
			info_nmbr = len(os.listdir(path_info))
			old_siz = (float(folder_size1) + float(folder_size2)+ float(folder_size3)+ float(folder_size4))
			old_size = "%0.1f" % (old_siz/(1024*1024.0))
			for folder in path :
				print(folder)
				llista = os.listdir(folder)
				for file in llista:
					print(file)
					archivo = folder + os.sep + file
					estado = os.stat(archivo)
					modificado = datetime.datetime.fromtimestamp(estado.st_mtime)
					print(modificado)
					if modificado < dia :
						os.remove(archivo)
						rmvd += 1
			folder_size1=sum([sum([os.path.getsize(os.path.join(path_poster, fname)) for fname in files]) for path_poster, folders, files in os.walk(path_poster)])
			posters_sz = "%0.1f" % (folder_size1/(1024*1024.0))
			poster_nmbr = len(os.listdir(path_poster))
			folder_size2=sum([sum([os.path.getsize(os.path.join(path_banner, fname)) for fname in files]) for path_banner, folders, files in os.walk(path_banner)])
			banners_sz = "%0.1f" % (folder_size2/(1024*1024.0))
			banner_nmbr = len(os.listdir(path_banner))
			folder_size3=sum([sum([os.path.getsize(os.path.join(path_backdrop, fname)) for fname in files]) for path_backdrop, folders, files in os.walk(path_backdrop)])
			backdrops_sz = "%0.1f" % (folder_size3/(1024*1024.0))
			backdrop_nmbr = len(os.listdir(path_backdrop))
			folder_size4=sum([sum([os.path.getsize(os.path.join(path_info, fname)) for fname in files]) for path_info, folders, files in os.walk(path_info)])
			infos_sz = "%0.1f" % (folder_size4/(1024*1024.0))
			info_nmbr = len(os.listdir(path_info))
			new_siz = (float(folder_size1) + float(folder_size2)+ float(folder_size3)+ float(folder_size4))
			new_size = "%0.1f" % (new_siz/(1024*1024.0))
			finalsize = (float(old_size) - float(new_size))
			self.strg()
			self['status'].setText(_("Removed older archives : ") + "{}".format(str(rmvd)))
			self['gain'].setText(_("Gain : ") + "{}MB. ↪️ {}MB.".format (finalsize,old_size))
#			self['finalsize'].setText(_("Final Size : ") + "{}MB".format (new_size))
		except:
			pass

def bqtList():
	bouquets = []
	serviceHandler = eServiceCenter.getInstance()
	list = serviceHandler.list(eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
	if list:
		while True:
			bqt = list.getNext()
			if not bqt.valid(): break
			info = serviceHandler.info(bqt)
			if info:
				bouquets.append((info.getName(bqt), bqt))
		return bouquets
	return 

def chList(bqtNm):
	channels = []
	serviceHandler = eServiceCenter.getInstance()
	chlist = serviceHandler.list(eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
	if chlist :
		while True:
			chh = chlist.getNext()
			if not chh.valid(): break
			info = serviceHandler.info(chh)
			if chh.flags & eServiceReference.isDirectory:
				info = serviceHandler.info(chh)
			if info.getName(chh) in bqtNm:
				chlist = serviceHandler.list(chh)
				while True:
					chhh = chlist.getNext()
					if not chhh.valid(): break
					channels.append((chhh.toString()))
		return channels
	return

class selBouquets(Screen):
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)

		skin = None
		if desktop_size <= 1280:
			if config.plugins.xtraEvent.skinSelect.value == "default":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/selBouquets_720_default.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_2":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/selBouquets_720_2.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_3":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/selBouquets_720_3.xml"
		else:
			if config.plugins.xtraEvent.skinSelect.value == "default":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/selBouquets_1080_default.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_2":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/selBouquets_1080_2.xml"
			elif config.plugins.xtraEvent.skinSelect.value == "skin_3":
				skin = "/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/skins/selBouquets_1080_3.xml"
		with open(skin, 'r') as f:
			self.skin = f.read()

		self.bouquets = bqtList()
		# self.epgcache = eEPGCache.getInstance()
		self.setTitle(_("Bouquet Selection"))
		self.sources = [SelectionEntryComponent(s[0], s[1], 0, (s[0] in ["sources"])) for s in self.bouquets]
		self["list"] = SelectionList(self.sources)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"red": self.cancel,
				"green": self.bouquetEpgs,
				"yellow": self["list"].toggleSelection,
				"blue": self["list"].toggleAllSelection,

				"ok": self["list"].toggleSelection
			}, -2)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))
		self["key_yellow"] = Label(_("Select(OK)"))
		self["key_blue"] = Label(_("All Select"))
		
		self['status'] = Label()
		self['info'] = Label()

	def bouquetEpgs(self):
		if os.path.exists(pathLoc+"bqts"):
			os.remove(pathLoc+"bqts")
		if os.path.exists(pathLoc+"events"):
			os.remove(pathLoc+"events")
		try:
			self.sources = []
			for idx,item in enumerate(self["list"].list):
				item = self["list"].list[idx][0]
				if item[3]:
					self.sources.append(item[0])

			for p in self.sources:
				serviceHandler = eServiceCenter.getInstance()
				refs = chList(p)

				eventlist=[]
				for ref in refs:
					open(pathLoc + "bqts", "a+").write("%s\n"% str(ref))
					# try:
						# events = epgcache.lookupEvent(['IBDCTSERNX', (ref, 1, -1, -1)])
						# n = config.plugins.xtraEvent.searchNUMBER.value
						# for i in range(int(n)):
							# title = events[i][4]
							# evntNm = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", title).rstrip()
							# eventlist.append(evntNm)
						# open(pathLoc+"events","w").write(str(eventlist))

					# except:
						# pass

			else:
				list = [(_('With Plugin Download'), self.withPluginDownload), (_('With Timer Download'), self.withTimerDownload), (_('No(Exit)'), self.cancel)]
				self.session.openWithCallback(self.menuCallback, ChoiceBox, title=_('Download ?'), list=list)

		except:
			pass

	def withPluginDownload(self):
		if not os.path.exists(pathLoc+"bqts"):
			self.session.open(MessageBox, _("Bouquet list not found! Before launching search, choose bouquet list!"), MessageBox.TYPE_INFO, timeout = 10)
		else:
			from . import download
			self.session.open(download.downloads)

	def withTimerDownload(self):
		if config.plugins.xtraEvent.timerMod.value == False:
			self.session.open(MessageBox, _("PLEASE TURN ON AND SET THE TIMER! ..."), MessageBox.TYPE_INFO, timeout = 10)
		else:
			if not os.path.exists(pathLoc+"bqts"):
				self.session.open(MessageBox, _("Bouquet list not found! Before launching search, choose bouquet list!"), MessageBox.TYPE_INFO, timeout = 10)
			else:
				self.session.openWithCallback(self.restart, MessageBox, _("NOW AND RESTART TO SEARCH AND DOWNLOAD IN BACKGROUND WITH TIMER?"), MessageBox.TYPE_YESNO, timeout = 20)

	def menuCallback(self, ret = None):
		ret and ret[1]()

	def restart(self, answer):
		if answer is True:
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

	def cancel(self):
		self.close(self.session, False)

class pathLocation():
	def __init__(self):
		self.location()

	def location(self):
		pathLoc = ""
		if not os.path.isdir(config.plugins.xtraEvent.loc.value):
			pathLoc = "/tmp/xtraEvent/"
			try:
				if not os.path.isdir(pathLoc):
					os.makedirs(pathLoc + "poster")
					os.makedirs(pathLoc + "banner")
					os.makedirs(pathLoc + "backdrop")
					os.makedirs(pathLoc + "infos")
			except:
				pass
		else:	
			pathLoc = config.plugins.xtraEvent.loc.value + "xtraEvent/"
			try:
				if not os.path.isdir(pathLoc):
					os.makedirs(pathLoc + "poster")
					os.makedirs(pathLoc + "banner")
					os.makedirs(pathLoc + "backdrop")
					os.makedirs(pathLoc + "infos")
			except:
				pass

		return pathLoc
pathLoc = pathLocation().location()

if config.plugins.xtraEvent.tmdbAPI.value != "":
	tmdb_api = config.plugins.xtraEvent.tmdbAPI.value
else:
	tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

if config.plugins.xtraEvent.fanartAPI.value != "":
	fanart_api = config.plugins.xtraEvent.fanartAPI.value
else:
	fanart_api = "6d231536dea4318a88cb2520ce89473b"
