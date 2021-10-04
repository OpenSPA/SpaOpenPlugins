# -*- coding: utf-8 -*-
# by digiteng...06.2020, 11.2020
# Code by Villak OpenSPA Team for PermanentEvent 2021

from Components.ProgressBar import ProgressBar
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.config import config
from Components.ScrollLabel import ScrollLabel
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from ServiceReference import ServiceReference
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eEPGCache, eTimer, ePixmap
from requests.utils import quote
from PIL import Image
from datetime import datetime
from . import permanent
import Tools.Notifications
import requests
import os, re, random, json
import gettext
import socket
import threading

PluginLanguageDomain = "PermanentEvent"
PluginLanguagePath = "Extensions/PermanentEvent/locale/"

def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))

def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
language.addCallback(localeInit())

if config.plugins.PermanentEvent.tmdbAPI.value != "":
	tmdb_api = config.plugins.PermanentEvent.tmdbAPI.value
else:
	tmdb_api = "f625fc594f8b04576480acac3b71ad6c"
if config.plugins.PermanentEvent.tvdbAPI.value != "":
	tvdb_api = config.plugins.PermanentEvent.tvdbAPI.value
else:
	tvdb_api = "1e4302d517e953bcfe7b12a61fe2f2f8"
if config.plugins.PermanentEvent.fanartAPI.value != "":
	fanart_api = config.plugins.PermanentEvent.fanartAPI.value
else:
	fanart_api = "c87124eab6648e21d2439590af418d83"
	
epgcache = eEPGCache.getInstance()
pathLoc = config.plugins.PermanentEvent.loc.value + "PermanentEvent/"

help_txt = _("Press the green button to start downloads...")
class downloads(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = ["downloadsback"]
		self.setTitle(_("Donwloads..."))
		self["text"] = ScrollLabel("")
		self['status'] = Label()
		self['info'] = Label()
		self['info2'] = Label()
		self['storage'] = Label()
		self['infoall'] = Label()
		self['gain'] = Label()
		self['finalsize'] = Label()
		self['key_red'] = Label(_('Close'))
		self['key_green'] = Label(_('Download'))
		self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.close, 'red': self.close, 'ok':self.save,'green':self.save,"info": self.strg}, -2)
		self['progress'] = ProgressBar()
		self['progress'].setRange((0, 100))
		self['progress'].setValue(0)
		self['int_statu'] = Label()
		self["text"].setText(help_txt)
		self.intCheck()

	def save(self):
			self.selBouquets()

	def selBouquets(self):
			if os.path.exists(pathLoc + "bqts"):
				with open(pathLoc + "bqts", "r") as f:
					refs = f.readlines()
				nl = len(refs)
				eventlist=[]
				for i in range(nl):
					ref = refs[i]
					try:
						events = epgcache.lookupEvent(['IBDCTSERNX', (ref, 1, -1, -1)])
						if config.plugins.PermanentEvent.searchNUMBER.value == _("primetime"):
							n = 50
							for i in range(int(n)):
								title = events[i][4]
								evntNm = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", title).rstrip()
								eventlist.append(evntNm)
						elif config.plugins.PermanentEvent.searchNUMBER.value == _("now-next"):
							n = 20
							for i in range(int(n)):
								title = events[i][4]
								evntNm = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", title).rstrip()
								eventlist.append(evntNm)
						else:
							n = config.plugins.PermanentEvent.searchNUMBER.value
							for i in range(int(n)):
								title = events[i][4]
								evntNm = re.sub("([\(\[]).*?([\)\]])|(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|( -(.*?).*)|(,)|!", "", title).rstrip()
								eventlist.append(evntNm)
					except:
						pass
				self.titles = list(dict.fromkeys(eventlist))
	#			print "EVENTOS DOWNLOADS: ", self.titles
				self.download()

	def strg(self):
		try:
			filepath = pathLoc+ "backdrop/"
			folder_size=sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
			backdrops_sz = "%0.1f" % (folder_size/(1024*1024.0))
			backdrop_nmbr = len(os.listdir(filepath))
			self['storage'].setText(_("Storage folder...") + "\n{}".format (filepath))
			self['infoall'].setText(_("Total Backdrops : ") + "{}".format(backdrop_nmbr))
			self['gain'].setText(_("Size : ") + "{} MB.".format(backdrops_sz))
			self['finalsize'].setText(_(" ").format())
		except:
			pass

	def intCheck(self):
		try:
			socket.setdefaulttimeout(2)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
			self['int_statu'].setText("●")
			# return True
		except:
			return False

	def download(self):
		threading.Thread(target=self.down).start()

####################################################
	def down(self):
		if self.netCheck():
			if config.plugins.PermanentEvent.downalerts.value == True:
				Tools.Notifications.AddNotification(MessageBox, _("PermanentEvent Downloads started!"), MessageBox.TYPE_INFO, timeout = 10)
			else:
				pass
			self['progress'].setValue(0)
			now = datetime.now()
			dt = now.strftime("%d/%m/%Y %H:%M:%S")
			with open("/tmp/permanent_report", "a+") as f:
				f.write(str("\nInicio Descarga : {}\n".format(dt)))
			try:
				tmdb_backdrop_downloaded = 0
				tvdb_backdrop_downloaded = 0
				fanart_backdrop_downloaded = 0
				extra_downloaded = 0
				extra2_downloaded = 0
				title = ""
				n = len(self.titles)
				for i in range(n):
					title = self.titles[i]
					title = title.strip()

	# backdrop() #################################################################

					if config.plugins.PermanentEvent.backdrop.value == True:
						if config.plugins.PermanentEvent.extra.value == True:
							dwnldFile = "{}/backdrop/{}.jpg".format(pathLoc, title)
							if not os.path.exists(dwnldFile):
								url_tvmovie = "http://capi.tvmovie.de/v1/broadcasts/search?q={}&page=1&rows=1".format(title.replace(" ", "+"))
								try:
									url = requests.get(url_tvmovie).json()['results'][0]['images'][0]['filepath']['android-image-320-180']
									open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
									extra_downloaded += 1
									downloaded = extra_downloaded
									source = "TvMovie..."
									self.prgrs(source, downloaded, n)
									self['info'].setText(_("Downloaded from TVMOVIE.DE... ") + "{}".format(title.upper()))
									self.brokenImageRemove()
								except:
									pass
							else:
								self['info'].setText(str(_("This backdrop exists or not found on TVMOVIE.DE... ") + title))

						if config.plugins.PermanentEvent.tmdb.value == True:
							dwnldFile = pathLoc + "backdrop/{}.jpg".format(title)
							if not os.path.exists(dwnldFile):
								srch = "multi"
								lang = config.plugins.PermanentEvent.searchLang.value
								url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote(title), lang)
								try:
									backdrop = requests.get(url_tmdb).json()['results'][0]['backdrop_path']
									if backdrop:
										backdrop_size = config.plugins.PermanentEvent.TMDBbackdropsize.value
										url = "https://image.tmdb.org/t/p/{}{}".format(backdrop_size, backdrop)
										open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
										tmdb_backdrop_downloaded += 1
										downloaded = tmdb_backdrop_downloaded
										source = "TMDB..."
										self.prgrs(source, downloaded, n)
										self['info'].setText(_("Downloaded from TMDB... ") + "{}".format(title.upper()))
										self.brokenImageRemove()
									else:
										self['info'].setText(str(_("This backdrop exists or not found on TMDB... ") + title))
								except:
									pass

						if config.plugins.PermanentEvent.tvdb.value == True:
							dwnldFile = pathLoc + "backdrop/{}.jpg".format(title)
							if not os.path.exists(dwnldFile):
								try:
									url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(quote(title))
									url_read = requests.get(url_tvdb).text
									series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read)[0]
									if series_id:
										lang = config.plugins.PermanentEvent.searchLang.value
										url_tvdb = "https://thetvdb.com/api/{}/series/{}/{}.xml".format(tvdb_api, series_id, lang)
										url_read = requests.get(url_tvdb).text
										backdrop = re.findall('<fanart>(.*?)</fanart>', url_read)[0]
										if backdrop:
											url = "https://artworks.thetvdb.com/banners/{}".format(backdrop)
											if config.plugins.PermanentEvent.TVDBbackdropsize.value == "thumbnail":
												url = url.replace(".jpg", "_t.jpg")
											open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
											tvdb_backdrop_downloaded += 1
											downloaded = tvdb_backdrop_downloaded
											source = "TVDB..."
											self.prgrs(source, downloaded, n)
											self['info'].setText(_("Downloaded from TVDB... ") + "{}".format(title.upper()))
											self.brokenImageRemove()
										else:
											self['info'].setText(str(_("This backdrop exists or not found on TVDB... ") + title))
								except:
									pass

						if config.plugins.PermanentEvent.fanart.value == True:
							dwnldFile = pathLoc + "backdrop/{}.jpg".format(title)
							if not os.path.exists(dwnldFile):
								try:
									srch = "multi"
									url = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
									bckdrp = requests.get(url).json()
									tmdb_id = (bckdrp['results'][0]['id'])
									if tmdb_id:
										m_type = (bckdrp['results'][0]['media_type'])
										if m_type == "movie":
											m_type = (bckdrp['results'][0]['media_type']) + "s"
										else:
											mm_type = m_type
											url = "http://api.tvmaze.com/singlesearch/shows?q={}".format(quote(title))
											bckdrp = requests.get(url).json()
											tvdb_id = (bckdrp['externals']['thetvdb'])
											if tvdb_id:
												try:
													url = "https://webservice.fanart.tv/v3/{}/{}?api_key={}".format(m_type, tvdb_id, fanart_api)
													bckdrp = requests.get(url).json()
													if bckdrp:
														if m_type == "movie":
															url = (bckdrp['moviethumb'][0]['url'])
														else:
															url = (bckdrp['tvthumb'][0]['url'])
														if url:
															open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
															fanart_backdrop_downloaded += 1
															downloaded = fanart_backdrop_downloaded
															source = "FANART..."
															self.prgrs(source, downloaded, n)
															self['info'].setText(_("Downloaded from FANART... ") + "{}".format(title.upper()))
															self.brokenImageRemove()
															scl = config.plugins.PermanentEvent.FANART_Backdrop_Resize.value
															im = Image.open(dwnldFile)
															scl = config.plugins.PermanentEvent.FANART_Backdrop_Resize.value
															im1 = im.resize((im.size[0] // int(scl), im.size[1] // int(scl)), Image.ANTIALIAS)
															im1.save(dwnldFile)
												except:
													pass
								except:
									pass
							else:
								self['info'].setText(str(_("This backdrop exists or not found on FANART... ") + title))

#						if config.plugins.PermanentEvent.extra2.value == True:
#							self.brokenImageRemove()
#							dwnldFile = "{}backdrop/{}.jpg".format(pathLoc, title)
#							if not os.path.exists(dwnldFile):
#								self.brokenImageRemove()
#								try:
#									url = "https://www.google.com/search?q={}&tbm=isch&tbs=sbd:0".format(title.replace(" ", "+"))
#									print 'GOOGLE URL BUSCA IMAGE', url
#									headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}#
#									ff = requests.get(url, stream=True, headers=headers).text
#									p = re.findall('"https://(.*?).jpg"', ff)
#									url = "https://" + p[1] + ".jpg"
#									print 'GOOGLE URL FIN IMAGE', url
#									open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
#									if dwnldFile:
#										self.brokenImageRemove()
#										extra2_downloaded += 1
#										downloaded = extra2_downloaded
#										source = "GOOGLE..."
#										self.prgrs(source, downloaded, n)
#										self['info'].setText(_("Downloaded from GOOGLE... ") + "{}".format(title.upper()))
#									else:
#										pass
#								except:
#									pass
#							else:
#								self['info'].setText(str(_("This backdrop exists or not found on GOOGLE... ") + title))

				now = datetime.now()
				dt = now.strftime("%d/%m/%Y %H:%M:%S")
				rt = pathLoc + "backdrop"
				report = "Descarga finalizada : {}\
					\nTotal Fondo(s) Descargado(s) en... {}\
					\n TMDB : {}\
					\n TVDB : {}\
					\n FANART : {}\
					\n TVMOVIE.de : {}\n\n".format(dt, rt, str(tmdb_backdrop_downloaded), str(tvdb_backdrop_downloaded), str(fanart_backdrop_downloaded), str(extra_downloaded), str(extra2_downloaded))
				self['info'].setText(_("Downloads finished..."))
				self['info2'].setText(report)
				with open("/tmp/permanent_report", "a+") as f:
					f.write(report)
					if config.plugins.PermanentEvent.downalerts.value == True:
						Tools.Notifications.AddNotification(MessageBox, _("PermanentEvent Downloads finished!"), MessageBox.TYPE_INFO, timeout = 10)
					else:
						pass
				return
			except:
				pass
		else:
			Tools.Notifications.AddNotification(MessageBox, _("Error! There is no Internet conection!"), MessageBox.TYPE_INFO, timeout = 10)
			return

	def netCheck(self):
		try:
			socket.setdefaulttimeout(0.5)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
			return True
		except:
			return False

####################################################################################################################################

	def prgrs(self, source, downloaded, n):
		self['status'].setText(_("Download : ") + "{} {} / {}".format(source, downloaded, n))
		self['progress'].setValue(int(100*downloaded/n))

	def brokenImageRemove(self):
		b = os.listdir(pathLoc)
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
			