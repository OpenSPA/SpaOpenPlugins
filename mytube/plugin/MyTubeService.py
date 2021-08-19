# -*- coding: iso-8859-1 -*-

from . import _
from enigma import ePythonMessagePump

from __init__ import decrypt_block
from ThreadQueue import ThreadQueue
import gdata.youtube
import gdata.youtube.service
from gdata.service import BadAuthentication

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
#from oauth2client.tools import run_flow
from Tools.Directories import fileExists


from twisted.web import client
from twisted.internet import reactor
from urllib2 import Request, URLError, urlopen as urlopen2

from socket import gaierror, error
import os, socket, httplib
from urllib import quote, unquote_plus, unquote, urlencode
from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
from Components.config import config

from urlparse import parse_qs, parse_qsl, urljoin
from threading import Thread
import codecs
import re
import json
from jsinterp import JSInterpreter
from swfinterp import SWFInterpreter
from urllib2 import urlopen, URLError
from os import mkdir, path as os_path

YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
DEVELOPER_KEY = None #"AIzaSyDYhIXx2lmga1aJJ7T-zTozmFWw-2ZB9s0"
YOUTUBE_API_CLIENT_ID = None #'928352881596-msmi2f4uje1mt556ug6hueuiersm9l60.apps.googleusercontent.com'
YOUTUBE_API_CLIENT_SECRET = None #'UKnl9CYqv8AI0WTeV9iJOnBD'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


HTTPConnection.debuglevel = 1

PRIORITY_VIDEO_FORMAT = []

def try_get(src, getter, expected_type=None):
    if not isinstance(getter, (list, tuple)):
        getter = [getter]
    for get in getter:
        try:
            v = get(src)
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        else:
            if expected_type is None or isinstance(v, expected_type):
                return v

def createPriorityFormats():
	global PRIORITY_VIDEO_FORMAT
	video_format = {
			'38':['38', '266', '264', '138'],  # 4096x3072
			'37':['37', '96', '301', '137', '299'],  # 1920x1080
			'22':['22', '95', '300', '136', '298'],  # 1280x720
			'35':['35', '59', '78', '94', '135', '212'],  # 854x480
			'18':['18', '93', '34', '6', '134'],  # 640x360
			'5':['5', '36', '92', '132', '133'],  # 400x240
			'17':['17', '91', '13', '151', '160']  # 176x144
		}
	for itag in ['17', '5', '18', '35', '22', '37', '38']:
		PRIORITY_VIDEO_FORMAT = video_format[itag] + PRIORITY_VIDEO_FORMAT

createPriorityFormats()


DASHMP4_FORMAT = [
		'133', '134', '135', '136', '137', '138',
		'160', '212', '264', '266', '298', '299'
	]

IGNORE_VIDEO_FORMAT = [
		'43', '44', '45', '46',  # webm
		'82', '83', '84', '85',  # 3D
		'100', '101', '102',  # 3D
		'167', '168', '169',  # webm
		'170', '171', '172',  # webm
		'218', '219',  # webm
		'242', '243', '244', '245', '246', '247', '248',  # webm
		'249', '250', '251',  # webm
		'271', '272',  # webm
		'302', '303', '308',  # webm
		'313', '315'  # webm
]

def uppercase_escape(s):
	unicode_escape = codecs.getdecoder('unicode_escape')
	return re.sub(
		r'\\U[0-9a-fA-F]{8}',
		lambda m: unicode_escape(m.group(0))[0],
		s)

def compat_urllib_parse_unquote(string, encoding='utf-8', errors='replace'):
	if string == '':
		return string
	res = string.split('%')
	if len(res) == 1:
		return string
	if encoding is None:
		encoding = 'utf-8'
	if errors is None:
		errors = 'replace'
	# pct_sequence: contiguous sequence of percent-encoded bytes, decoded
	pct_sequence = b''
	string = res[0]
	for item in res[1:]:
		try:
			if not item:
				raise ValueError
			pct_sequence += item[:2].decode('hex')
			rest = item[2:]
			if not rest:
				# This segment was just a single percent-encoded character.
				# May be part of a sequence of code units, so delay decoding.
				# (Stored in pct_sequence).
				continue
		except ValueError:
			rest = '%' + item
		# Encountered non-percent-encoded characters. Flush the current
		# pct_sequence.
		string += pct_sequence.decode(encoding, errors) + rest
		pct_sequence = b''
	if pct_sequence:
		# Flush the final pct_sequence
		string += pct_sequence.decode(encoding, errors)
	return string

def _parse_qsl(qs, keep_blank_values=False, strict_parsing=False,
			encoding='utf-8', errors='replace'):
	qs, _coerce_result = qs, unicode
	pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
	r = []
	for name_value in pairs:
		if not name_value and not strict_parsing:
			continue
		nv = name_value.split('=', 1)
		if len(nv) != 2:
			if strict_parsing:
				raise ValueError("bad query field: %r" % (name_value,))
			# Handle case of a control-name with no equal sign
			if keep_blank_values:
				nv.append('')
			else:
				continue
		if len(nv[1]) or keep_blank_values:
			name = nv[0].replace('+', ' ')
			name = compat_urllib_parse_unquote(
				name, encoding=encoding, errors=errors)
			name = _coerce_result(name)
			value = nv[1].replace('+', ' ')
			value = compat_urllib_parse_unquote(
				value, encoding=encoding, errors=errors)
			value = _coerce_result(value)
			r.append((name, value))
	return r


def compat_parse_qs(qs, keep_blank_values=False, strict_parsing=False,
					encoding='utf-8', errors='replace'):
	parsed_result = {}
	pairs = _parse_qsl(qs, keep_blank_values, strict_parsing,
					encoding=encoding, errors=errors)
	for name, value in pairs:
		if name in parsed_result:
			parsed_result[name].append(value)
		else:
			parsed_result[name] = [value]
	return parsed_result



if 'HTTPSConnection' not in dir(httplib):
	# python on enimga2 has no https socket support
	gdata.youtube.service.YOUTUBE_USER_FEED_URI = 'http://gdata.youtube.com/feeds/api/users'

def validate_cert(cert, key):
	buf = decrypt_block(cert[8:], key) 
	if buf is None:
		return None
	return buf[36:107] + cert[139:196]

def get_rnd():
	try:
		rnd = os.urandom(8)
		return rnd
	except:
		return None

std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}

#config.plugins.mytube = ConfigSubsection()
#config.plugins.mytube.general = ConfigSubsection()
#config.plugins.mytube.general.useHTTPProxy = ConfigYesNo(default = False)
#config.plugins.mytube.general.ProxyIP = ConfigIP(default=[0,0,0,0])
#config.plugins.mytube.general.ProxyPort = ConfigNumber(default=8080)
#class MyOpener(FancyURLopener):
#	version = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12'


class GoogleSuggestions():
	def __init__(self):
		self.hl = "en"
		self.conn = None

	def prepareQuery(self):
		#GET /complete/search?output=toolbar&client=youtube-psuggest&xml=true&ds=yt&hl=en&jsonp=self.gotSuggestions&q=s
		self.prepQuerry = "/complete/search?output=toolbar&client=youtube&xml=true&ds=yt&"
		if self.hl is not None:
			self.prepQuerry = self.prepQuerry + "hl=" + self.hl + "&"
		self.prepQuerry = self.prepQuerry + "jsonp=self.gotSuggestions&q="
		print "[MyTube - GoogleSuggestions] prepareQuery:",self.prepQuerry

	def getSuggestions(self, queryString):
		self.prepareQuery()
		if queryString is not "":
			query = self.prepQuerry + quote(queryString)
			self.conn = HTTPConnection("google.com")
			try:
				self.conn = HTTPConnection("google.com")
				self.conn.request("GET", query, "", {"Accept-Encoding": "UTF-8"})
			except (CannotSendRequest, gaierror, error):
				self.conn.close()
				print "[MyTube - GoogleSuggestions] Can not send request for suggestions"
				return None
			else:
				try:
					response = self.conn.getresponse()
				except BadStatusLine:
					self.conn.close()
					print "[MyTube - GoogleSuggestions] Can not get a response from google"
					return None
				else:
					if response.status == 200:
						data = response.read()
						header = response.getheader("Content-Type", "text/xml; charset=ISO-8859-1")
						charset = "ISO-8859-1"
						try:
							charset = header.split(";")[1].split("=")[1]
							print "[MyTube - GoogleSuggestions] Got charset %s" %charset
						except:
							print "[MyTube - GoogleSuggestions] No charset in Header, falling back to %s" %charset
						data = data.decode(charset).encode("utf-8")
						self.conn.close()
						return data
					else:
						self.conn.close()
						return None
		else:
			return None

class MyTubeFeedEntry():

	def __init__(self, feed, entry, favoritesFeed = False):
		global youtube
		self.feed = feed
		self.entry = entry
		self.favoritesFeed = favoritesFeed
		self.thumbnail = {}
		"""self.myopener = MyOpener()
		urllib.urlopen = MyOpener().open
		if config.plugins.mytube.general.useHTTPProxy.value is True:
			proxy = {'http': 'http://'+str(config.plugins.mytube.general.ProxyIP.getText())+':'+str(config.plugins.mytube.general.ProxyPort.value)}
			self.myopener = MyOpener(proxies=proxy)
			urllib.urlopen = MyOpener(proxies=proxy).open
		else:
			self.myopener = MyOpener()
			urllib.urlopen = MyOpener().open"""
		self.request = None
		#self.request = youtube.videos().list(part="snippet,statistics,contentDetails",id=self.entry["id"]["videoId"]).execute()
		
		
	def isPlaylistEntry(self):
		return False

	def getTubeId(self):
		#print "[MyTubeFeedEntry] getTubeId"
		try:
			return self.entry["id"]["videoId"] 
		except:
			try:
				return self.entry["snippet"]["resourceId"]["videoId"]
			except:
				try:
					return self.entry["snippet"]["resourceId"]["channelId"]
				except:
					return self.entry["id"]["channelId"]
				
	def getId(self):
		try:
			return self.entry["id"]
		except:
			return None

	def getType(self):
		try:
			return self.entry["id"]["kind"] 
		except:
			try:
				return self.entry["snippet"]["resourceId"]["kind"]
			except:
				return "youtube#video"
		
	def getlive(self):
		try:
			return self.entry["snippet"]["liveBroadcastContent"]
		except:
			return "none"

	def getTitle(self):
		#print "[MyTubeFeedEntry] getTitle",self.entry.media.title.text
		try:
			return str(self.entry["snippet"]["title"]).encode('utf-8').strip()
		except KeyError:
			return ""

	def getDescription(self):
		#print "[MyTubeFeedEntry] getDescription"
		try:
			return self.entry["snippet"]["description"].encode('utf-8').strip()
		except KeyError:
			return "not vailable"

	def getMoreDescription(self):
		try:
			return self.request["items"][0]["snippet"]["description"].encode('utf-8').strip()
		except KeyError:
			return None

	def getThumbnailUrl(self, index = 0):
		#print "[MyTubeFeedEntry] getThumbnailUrl"
		try:
			return str(self.entry["snippet"]["thumbnails"]["default"]["url"])
		except KeyError:
			return None

	def getPublishedDate(self):
		try:
			return self.entry["snippet"]["publishedAt"]
		except KeyError:
			return "unknown"

	def getViews(self):
		try:
			return int(self.request["items"][0]["statistics"]["viewCount"])
		except:
			return 0
	
	def getDuration(self):
		try:
			dur = self.request["items"][0]["contentDetails"]["duration"]
		except:
			return None
		dur = dur.replace("PT","")
		h = 0
		m = 0
		s = 0
		f = dur.find('H')
		if f > 0:
			h = int(dur[:f])
			dur = dur[f+1:]
		f = dur.find('M')
		if f > 0:
			m = int(dur[:f])
			dur = dur[f+1:]
		f = dur.find('S')
		if f > 0:
			s = int(dur[:f])
		return (h*60*60)+(m*60)+s

	def getDimension(self):
		try:
			return self.request["items"][0]["contentDetails"]["dimension"]
		except:
			return ""

	def getDefinition(self):
		try:
			return self.request["items"][0]["contentDetails"]["definition"]
		except:
			return ""

	def getRatingAverage(self):
		total = self.getNumRaters() + self.getNumDeRaters()
		try:
			return (self.getNumRaters()/total)*100
		except:
			return 0

	def getCategoryId(self):
		try:
			return self.request["items"][0]["snippet"]["categoryId"]
		except:
			return None

	def getNumRaters(self):
		try:
			return int(self.request["items"][0]["statistics"]["likeCount"])
		except:
			return 0
	def getNumDeRaters(self):
		try:
			return int(self.request["items"][0]["statistics"]["dislikeCount"])
		except:
			return 0

	def getTags(self):
		try:
			return str(self.request["items"][0]["snippet"]["tags"])
		except:
			return ""

	def getAuthor(self):
		try:
			return self.entry["snippet"]["channelTitle"]
		except:
			try:
				return self.entry["snippet"]["resourceId"]["kind"]
			except:
				return None

	def getChannelID(self):
		try:
			return self.entry["snippet"]["channelId"]
		except:
			try:
				return self.entry["snippet"]["resourceId"]["channelId"]
			except KeyError:
				return None


	def getUserFeedsUrl(self):
		for author in self.entry.author:
			return author.uri.text

		return False

	def getUserId(self):
		try:
			return self.entry["snippet"]["channelTitle"]
		except:
			try:
				return self.entry["snippet"]["title"]
			except:
				return ""

	def subscribeToUser(self):
		return myTubeService.SubscribeToUser(self.getChannelID())

	def UnsubscribeToUser(self):
		return myTubeService.UnSubscribeToUser(self.getId())
		
	def addToFavorites(self):
		return myTubeService.addToFavorites(self.getTubeId(),self.getType())

	def deletefromFavorites(self):
		return myTubeService.deletefromFavorites(self.getId())

	def like(self):
		myTubeService.setlike(self.getTubeId())

	def dislike(self):
		myTubeService.setdislike(self.getTubeId())

	def PrintEntryDetails(self):
		self.request = youtube.videos().list(part="snippet,statistics,contentDetails",id=self.getTubeId()).execute()
		EntryDetails = { 'Title': None, 'TubeID': None, 'Published': None, 'Published': None, 'Description': None, 'Category': None, 'Tags': None, 'Duration': None, 'Views': None, 'Rating': None, 'Thumbnails': None}
		EntryDetails['Title'] = str(self.entry["snippet"]["title"]).encode('utf-8').strip()
		EntryDetails['TubeID'] = self.getTubeId()
		if self.getMoreDescription():
			EntryDetails['Description'] = self.getMoreDescription()
		else:
			EntryDetails['Description'] = self.getDescription()
		EntryDetails['Category'] = self.getCategoryId()
		EntryDetails['Tags'] = self.getDimension()+' '+self.getDefinition()+' '+self.getTags()
		EntryDetails['Published'] = self.getPublishedDate()
		EntryDetails['Views'] = self.getViews()
		EntryDetails['Duration'] = self.getDuration()
		EntryDetails['Rating'] = self.getNumRaters()
		EntryDetails['DisRating'] = self.getNumDeRaters()
		EntryDetails['RatingAverage'] = self.getRatingAverage()
		EntryDetails['Author'] = self.getAuthor()
		EntryDetails['ratingaverage'] = self.getRatingAverage()
		# show thumbnails
		list = []
		for thumbnail in self.entry["snippet"]["thumbnails"]:
			print 'Thumbnail url: %s' % self.entry["snippet"]["thumbnails"][thumbnail]["url"]
			list.append(str(self.entry["snippet"]["thumbnails"][thumbnail]["url"]))
		EntryDetails['Thumbnails'] = list
		#print EntryDetails
		return EntryDetails
		

	def getPage(self,url):
		watchvideopage = None
		watchrequest = Request(url, None, std_headers)
		try:
			print "[MyTube] trying to find out if a HD Stream is available",url
			watchvideopage = urlopen2(watchrequest).read()
		except (URLError, HTTPException, socket.error), err:
			print "[MyTube] Error: Unable to retrieve watchpage - Error code: ", str(err)
			return None
		return watchvideopage

	def _get_ytplayer_config(self, webpage):
		# User data may contain arbitrary character sequences that may affect
		# JSON extraction with regex, e.g. when '};' is contained the second
		# regex won't capture the whole JSON. Yet working around by trying more
		# concrete regex first keeping in mind proper quoted string handling
		# to be implemented in future that will replace this workaround (see
		# https://github.com/rg3/youtube-dl/issues/7468,
		# https://github.com/rg3/youtube-dl/pull/7599)
		patterns = [
			r';ytplayer\.config\s*=\s*({.+?});ytplayer',
			r';ytplayer\.config\s*=\s*({.+?});',
		]
		for pattern in patterns:
			config = self._search_regex(pattern, webpage)
			if config:
				return json.loads(uppercase_escape(config))

	def getVideoUrl(self):
		VIDEO_FMT_PRIORITY_MAP = {
			'38' : 1, #MP4 Original (HD)
			'37' : 2, #MP4 1080p (HD)
			'22' : 3, #MP4 720p (HD)
			'18' : 4, #MP4 360p
			'35' : 5, #FLV 480p
			'34' : 6, #FLV 360p
		}
		video_id = str(self.getTubeId())
		url = 'https://www.youtube.com/watch?v=%s&gl=US&hl=en&has_verified=1&bpctr=9999999999' % video_id

		if fileExists("/usr/lib/python2.7/site-packages/youtube_dl/YoutubeDL.pyo"):
			res=None		
			try:
				from youtube_dl import YoutubeDL
				with YoutubeDL({}) as ydl:
					res=ydl.extract_info(url, download=False)
			except:
				pass

			if res:
				formats = res['formats']
				last_id=10
				video_url=None
				for fmt in formats:
					if VIDEO_FMT_PRIORITY_MAP.has_key(str(fmt['format_id'])):
						if VIDEO_FMT_PRIORITY_MAP[str(fmt['format_id'])]<last_id:
							last_id = VIDEO_FMT_PRIORITY_MAP[str(fmt['format_id'])]
							video_url = fmt['url']
				if video_url:
					return str(video_url)
			else:
				return "unavailable"


		# Get video webpage
		video_webpage = self.getPage(url)
		if not video_webpage:
			raise Exception('Video webpage not found!')

		# Attempt to extract SWF player URL
		mobj = re.search(r'swfConfig.*?"(https?:\\/\\/.*?watch.*?-.*?\.swf)"', video_webpage)
		if mobj is not None:
			player_url = re.sub(r'\\(.)', r'\1', mobj.group(1))
		else:
			player_url = None

		is_live = None
		player_response = {}

		# Get video info
		embed_webpage = None
		if re.search(r'player-age-gate-content">', video_webpage) is not None:
			age_gate = True

        		if config.plugins.mytube.general.showadult.value == False:
				return "age"

			# We simulate the access to the video from www.youtube.com/v/{video_id}
			# this can be viewed without login into Youtube
			url = 'https://www.youtube.com/embed/%s' % video_id
			embed_webpage = self.getPage(url)
			data = urlencode({
					'video_id': video_id,
					'eurl': 'https://youtube.googleapis.com/v/' + video_id,
					'sts': self._search_regex(r'"sts"\s*:\s*(\d+)', embed_webpage),
				})
			video_info_url = 'https://www.youtube.com/get_video_info?' + data
			video_info_webpage = self.getPage(video_info_url)
			video_info = compat_parse_qs(video_info_webpage)
		else:
			age_gate = False
			video_info = None
			sts = None
			# Try looking directly into the video webpage
			ytplayer_config = self._get_ytplayer_config(video_webpage)
			if ytplayer_config:
				args = ytplayer_config['args']
				if args.get('url_encoded_fmt_stream_map'):
					# Convert to the same format returned by compat_parse_qs
					video_info = dict((k, [v]) for k, v in args.items())
				if args.get('livestream') == '1' or args.get('live_playback') == 1:
					is_live = True
				sts = ytplayer_config.get('sts')
			else:
				return None

			if not player_response:
				pl_response = args.get('player_response')
				if pl_response:
					pl_response = json.loads(pl_response)
					if isinstance(pl_response, dict):
						player_response = pl_response

			if not video_info:
				# We also try looking in get_video_info since it may contain different dashmpd
				# URL that points to a DASH manifest with possibly different itag set (some itags
				# are missing from DASH manifest pointed by webpage's dashmpd, some - from DASH
				# manifest pointed by get_video_info's dashmpd).
				# The general idea is to take a union of itags of both DASH manifests (for example
				# video with such 'manifest behavior' see https://github.com/rg3/youtube-dl/issues/6093)
				for el in ('info', 'embedded', 'detailpage', 'vevo', ''):
					query = {
							'video_id': video_id,
							'ps': 'default',
							'eurl': '',
							'gl': 'US',
							'hl': 'en',
						}
					if el:
						query['el'] = el
					if sts:
						query['sts'] = sts
					data = urlencode(query)

					video_info_url = 'https://www.youtube.com/get_video_info?' + data
					video_info_webpage = self.getPage(video_info_url)
					if not video_info_webpage:
						continue
					get_video_info = compat_parse_qs(video_info_webpage)
		                        if not video_info:
                        			video_info = get_video_info
                    			get_token = self.extract_token(get_video_info)
                    			if get_token:
                        			# Different get_video_info requests may report different results, e.g.
                        			# some may report video unavailability, but some may serve it without
                        			# any complaint (see https://github.com/ytdl-org/youtube-dl/issues/7362,
                        			# the original webpage as well as el=info and el=embedded get_video_info
                        			# requests report video unavailability due to geo restriction while
                        			# el=detailpage succeeds and returns valid data). This is probably
                       				# due to YouTube measures against IP ranges of hosting providers.
                        			# Working around by preferring the first succeeded video_info containing
                        			# the token if no such video_info yet was found.
                        			token = self.extract_token(video_info)
                        			if not token:
                            				video_info = get_video_info
                        			break
						if not token:
							if 'reason' in video_info:
								print '[MyTube] %s' % video_info['reason'][0]
							else:
								print '[MyTube] "token" parameter not in video info for unknown reason'

		# Start extracting information
		if 'conn' in video_info and video_info['conn'][0][:4] == 'rtmp':
			url = video_info['conn'][0]
		elif not is_live and (len(video_info.get('url_encoded_fmt_stream_map', [''])[0]) >= 1 or \
			len(video_info.get('adaptive_fmts', [''])[0]) >= 1):
			encoded_url_map = video_info.get('url_encoded_fmt_stream_map', [''])[0] + \
				',' + video_info.get('adaptive_fmts', [''])[0]
			if 'rtmpe%3Dyes' in encoded_url_map:
				raise Exception('rtmpe downloads are not supported, see https://github.com/rg3/youtube-dl/issues/343')

			# Find the best format from our format priority map
			encoded_url_map = encoded_url_map.split(',')
			url_map_str = [None, None]
			for our_format in PRIORITY_VIDEO_FORMAT:
				our_format = 'itag=' + our_format
				for encoded_url in encoded_url_map:
					if our_format in encoded_url and 'url=' in encoded_url:
						url_map_str[0] = encoded_url
						break
				if url_map_str[0]:
					break
			# If DASH MP4 video add link also on Dash MP4 Audio
			if url_map_str[0] and our_format[5:] in DASHMP4_FORMAT:
				for our_format in ['itag=141', 'itag=140', 'itag=139',
						'itag=258', 'itag=265', 'itag=325', 'itag=328']:
					for encoded_url in encoded_url_map:
						if our_format in encoded_url and 'url=' in encoded_url:
							url_map_str[1] = encoded_url
							break
					if url_map_str[1]:
						break
			# If anything not found, used first in the list if it not in ignore map
			if not url_map_str[0]:
				for encoded_url in encoded_url_map:
					if 'url=' in encoded_url:
						url_map_str = encoded_url
						for ignore_format in IGNORE_VIDEO_FORMAT:
							ignore_format = 'itag=' + ignore_format
							if ignore_format in encoded_url:
								url_map_str[0] = None
								break
					if url_map_str[0]:
						break
			if not url_map_str[0]:
				url_map_str[0] = encoded_url_map[0]

			url = ''
			for url_map in url_map_str:
				if not url_map:
					break
				url_data = compat_parse_qs(url_map)
				if url:
					url += '&suburi='
				url += url_data['url'][0]

				if 's' in url_data:
					ASSETS_RE = r'"assets":.+?"js":\s*("[^"]+")'
					jsplayer_url_json = self._search_regex(ASSETS_RE,
						embed_webpage if age_gate else video_webpage)
					if not jsplayer_url_json and not age_gate:
						# We need the embed website after all
						if embed_webpage is None:
							embed_url = 'https://www.youtube.com/embed/%s' % video_id
							embed_webpage = self.getPage(embed_url)
						jsplayer_url_json = self._search_regex(ASSETS_RE, embed_webpage)

					player_url = json.loads(jsplayer_url_json)
					if player_url is None:
						player_url_json = self._search_regex(
							r'ytplayer\.config.*?"url"\s*:\s*("[^"]+")',
							video_webpage)
						player_url = json.loads(player_url_json)

				if 'sig' in url_data:
					url += '&signature=' + url_data['sig'][0]
				elif 's' in url_data:
					encrypted_sig = url_data['s'][0]

					signature = self._decrypt_signature(
						encrypted_sig, video_id, player_url, age_gate)
					sp = try_get(url_data, lambda x: x['sp'][0], unicode) or 'signature'
					url += '&%s=%s' % (sp, signature)

				if 'ratebypass' not in url:
					url += '&ratebypass=yes'
		else:
			manifest_url = player_response.get('streamingData')
			if manifest_url:
				manifest_url = manifest_url.get('hlsManifestUrl')
			if not manifest_url and player_response.get('hlsvp'):
				manifest_url = player_response['hlsvp'][0]
			if manifest_url:
				url = None
				url_map = self._extract_from_m3u8(manifest_url)

				# Find the best format from our format priority map
				for our_format in PRIORITY_VIDEO_FORMAT:
					if url_map.get(our_format):
						url = url_map[our_format]
						break
				# If anything not found, used first in the list if it not in ignore map
				if not url:
					for url_map_key in url_map.keys():
						if url_map_key not in IGNORE_VIDEO_FORMAT:
							url = url_map[url_map_key]
							break
				if not url:
					url = url_map.values()[0]
			else:
				return "format"

		return str(url)

        def extract_token(self,v_info):
            return self.dict_get(v_info, ('account_playback_token', 'accountPlaybackToken', 'token'))

	def dict_get(self,d, key_or_keys, default=None, skip_false_values=True):
	    if isinstance(key_or_keys, (list, tuple)):
	        for key in key_or_keys:
	            if key not in d or d[key] is None or skip_false_values and not d[key]:
	                continue
	            return d[key]
	        return default
	    return d.get(key_or_keys, default)

	def _signature_cache_id(self, example_sig):
		""" Return a string representation of a signature """
		return '.'.join(unicode(len(part)) for part in example_sig.split('.'))

	def extract(self):
		VIDEO_FMT_PRIORITY_MAP = {
			'38' : 1, #MP4 Original (HD)
			'37' : 2, #MP4 1080p (HD)
			'22' : 3, #MP4 720p (HD)
			'18' : 4, #MP4 360p
			'35' : 5, #FLV 480p
			'34' : 6, #FLV 360p
		}
		video_url = None
		video_id = str(self.getTubeId())

		# Getting video webpage
		#URLs for YouTube video pages will change from the format http://www.youtube.com/watch?v=ylLzyHk54Z0 to http://www.youtube.com/watch#!v=ylLzyHk54Z0.
		watch_url = 'http://www.youtube.com/watch?v=%s&gl=US&hl=en&has_verified=1&bpctr=9999999999' % video_id
		for x in range(0, 10): 
			watchvideopage = self.getPage(watch_url)
			if watchvideopage != None:
				break

		#watchrequest = Request(watch_url, None, std_headers)
		#try:
		#	print "[MyTube] trying to find out if a HD Stream is available",watch_url
		#	watchvideopage = urlopen2(watchrequest).read()
		#except (URLError, HTTPException, socket.error), err:
		#	print "[MyTube] Error: Unable to retrieve watchpage - Error code: ", str(err)
		if watchvideopage == None:
			return video_url

		# Get video info
		#### For age verify jump
       		age_gate = False
        	if re.search('player-age-gate-content">', watchvideopage) is not None:
		      	#<meta property="og:restrictions:age" content="18+">
            		age_gate = True

        		if config.plugins.mytube.general.showadult.value == False:
				return "age"

			url = 'http://www.youtube.com/embed/%s' % video_id
			embed_webpage = self.getPage(url)
            		# We simulate the access to the video from www.youtube.com/v/{video_id}
            		# this can be viewed without login into Youtube
            		info_url = 'http://www.youtube.com/get_video_info?video_id=%s&el=embedded&gl=US&hl=en&eurl=%s&asv=3&sts=%s' % (video_id, "https://youtube.googleapis.com/v/" + video_id,self._search_regex(r'"sts"\s*:\s*(\d+)', embed_webpage))
			request = Request(info_url, None, std_headers)
			try:
				infopage = urlopen2(request).read()
				videoinfo = parse_qs(infopage)
			except (URLError, HTTPException, socket.error), err:
				print "[MyTube] Error: unable to download video infopage",str(err)
				return video_url
        	else:
			videoinfo = None
			for el in ['', '&el=detailpage', '&el=vevo', '&el=embedded']:
				info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el))
				for x in range(0, 10): 
					infopage = self.getPage(info_url)
					if infopage != None:
						break
				if infopage == None:
					return video_url

				#request = Request(info_url, None, std_headers)
				try:
				#	infopage = urlopen2(request).read()
					videoinfo = parse_qs(infopage)
					if ('url_encoded_fmt_stream_map' or 'fmt_url_map') in videoinfo:
						break
				except:
					pass				
				#except (URLError, HTTPException, socket.error), err:
				#	print "[MyTube] Error: unable to download video infopage",str(err)
				#	return video_url
			if videoinfo == None:
				print "[MyTube] Error: unable to download video infopage"
				return video_url

        	try:
           		mobj = re.search(r';ytplayer.config = ({.*?});', watchvideopage)
            		info = json.loads(mobj.group(1))
            		args = info['args']
            		if args.get('ptk','') == 'vevo' or '&s=' in str(args):
                		# Vevo videos with encrypted signatures
				print '[MyTube] %s: Vevo video detected with encrypted signature.' % video_id
                		videoinfo['url_encoded_fmt_stream_map'] = [str(args['url_encoded_fmt_stream_map'])]
        	except:
            		pass



		if ('url_encoded_fmt_stream_map' or 'fmt_url_map') not in videoinfo:
			# Attempt to see if YouTube has issued an error message
			if 'reason' not in videoinfo:
				print '[MyTube] Error: unable to extract "fmt_url_map" or "url_encoded_fmt_stream_map" parameter for unknown reason'
			else:
				reason = unquote_plus(videoinfo['reason'][0])
				print '[MyTube] Error: YouTube said: %s' % reason.decode('utf-8')
			return video_url

		video_fmt_map = {}
		fmt_infomap = {}
		if videoinfo.has_key('url_encoded_fmt_stream_map'):
			tmp_fmtUrlDATA = videoinfo['url_encoded_fmt_stream_map'][0].split(',')
		else:
			tmp_fmtUrlDATA = videoinfo['fmt_url_map'][0].split(',')
		for fmtstring in tmp_fmtUrlDATA:
			fmturl = fmtid = fmtsig = ""
			if videoinfo.has_key('url_encoded_fmt_stream_map'):
				try:
					for arg in fmtstring.split('&'):
						if arg.find('=') >= 0:
							print arg.split('=')
							key, value = arg.split('=')
							if key == 'itag':
								if len(value) > 3:
									value = value[:2]
								fmtid = value
							elif key == 'url':
								fmturl = value
							elif key == 'sig':
								fmtsig = value
                   					elif key == 's':
#								if age_gate:
#                       							fmtsig = self._decrypt_signature_age_gate(value)
#								else:
									ASSETS_RE = r'"assets":.+?"js":\s*("[^"]+")'
									jsplayer_url_json = self._search_regex(ASSETS_RE,embed_webpage if age_gate else watchvideopage)
									if not jsplayer_url_json and not age_gate:
										# We need the embed website after all
										#if watchvideopage is None:
										#	embed_url = 'https://www.youtube.com/embed/%s' % video_id
										#	watchvideopage = self._download_webpage(embed_url)
										jsplayer_url_json = self._search_regex(ASSETS_RE, watchvideopage)

									player_url = json.loads(jsplayer_url_json)
									if player_url is None:
										player_url_json = self._search_regex(r'ytplayer\.config.*?"url"\s*:\s*("[^"]+")',		watchvideopage)
										player_url = json.loads(player_url_json)

									fmtsig = self._decrypt_signature(value, video_id, player_url)
 																
					if fmtid != "" and fmturl != "" and VIDEO_FMT_PRIORITY_MAP.has_key(fmtid):
						video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = { 'fmtid': fmtid, 'fmturl': unquote_plus(fmturl), 'fmtsig': fmtsig }
						if fmtsig != "":
							fmt_infomap[int(fmtid)] = "%s&signature=%s" %(unquote_plus(fmturl), fmtsig)
						elif "%26signature%3D" in fmturl:
							fmt_infomap[int(fmtid)] = unquote_plus(fmturl)

					fmturl = fmtid = fmtsig = ""

				except:
					print "error parsing fmtstring:",fmtstring
					
			else:
				(fmtid,fmturl) = fmtstring.split('|')  
				if VIDEO_FMT_PRIORITY_MAP.has_key(fmtid) and fmtid != "":
					video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = { 'fmtid': fmtid, 'fmturl': unquote_plus(fmturl) }
					fmt_infomap[int(fmtid)] = unquote_plus(fmturl)
		print "[MyTube] got",sorted(fmt_infomap.iterkeys())
		if video_fmt_map and len(video_fmt_map):
			print "[MyTube] found best available video format:",video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]['fmtid']
			best_video = video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]
			video_url = "%s&signature=%s" %(best_video['fmturl'].split(';')[0], best_video['fmtsig'])
			print "[MyTube] found best available video url:",video_url

		return str(video_url)
	

    	def _decrypt_signature_age_gate(self, s):
        	# The videos with age protection use another player, so the algorithms
        	# can be different.
        	if len(s) == 86:
        	    	return s[2:63] + s[82] + s[64:82] + s[63]
        	else:
        	    	# Fallback to the other algortihms
        	    	return self._decrypt_signature2(s)


	def _download_webpage(self, url):
		""" Returns a tuple (page content as string, URL handle) """
		try:
			urlh = urlopen(url)
		except URLError, e:
			raise Exception(e.reason)
		return urlh.read()

	def _search_regex(self, pattern, string, group=None):
		"""
		Perform a regex search on the given string, using a single or a list of
		patterns returning the first matching group.
		"""
		if group is None:
			mobj = re.search(pattern, string, 0)
		else:
			for p in pattern:
				mobj = re.search(p, string, 0)
				if mobj:
					break
		if mobj:
			if group is None:
				# return the first matching group
				return next(g for g in mobj.groups() if g is not None)
			else:
				return mobj.group(group)
		else:
			return None
			#raise Exception('Unable extract pattern from string!')

	def _decrypt_signature(self, s, video_id, player_url, age_gate=False):
		"""Turn the encrypted s field into a working signature"""

		if player_url is None:
			print 'Cannot decrypt signature without player_url'

		if player_url.startswith('//'):
			player_url = 'https:' + player_url
		elif not re.match(r'https?://', player_url):
			player_url = urljoin(
				'https://www.youtube.com', player_url)
		try:
			func = self._extract_signature_function(
					video_id, player_url, s
				)
			return func(s)
		except:
			raise Exception('Signature extraction failed!')

	def _decrypt_signature_old(self, s, player_url):
		"""Turn the encrypted s field into a working signature"""

		if player_url is None:
			raise Exception('Cannot decrypt signature without player_url!')

		if player_url[:2] == '//':
			player_url = 'https:' + player_url
		elif not re.match(r'https?://', player_url):
			player_url = urljoin('https://www.youtube.com', player_url)
		try:
			func = self._extract_signature_function(player_url,s)
			return func(s)
		except:
			raise Exception('Signature extraction failed!')

	def _extract_signature_function(self, video_id, player_url,example_sig):
		id_m = re.match(
			r'.*?-(?P<id>[a-zA-Z0-9_-]+)(?:/watch_as3|/html5player(?:-new)?|(?:/[a-z]{2,3}_[A-Z]{2})?/base)?\.(?P<ext>[a-z]+)$',
			player_url)
		if not id_m:
			raise Exception('Cannot identify player %r' % player_url)

		player_type = id_m.group('ext')
		player_id = id_m.group('id')

		#read function from file
#		import plugin
#		if player_id:
#			cypher = ""
#			try:
#				f = open(plugin.plugin_path+"/mytube.dic", "r")
#				for line in f:
#					if player_id in line:
#						cypher=line.split(":")[1].split(",")
#						break
#				f.close()
#			except:
#				pass
#			if cypher != "": 
#           			return lambda s: ''.join(s[int(i)] for i in cypher)


		code = self._download_webpage(player_url)
		res = None
		if player_type == 'js':
			res=self._parse_sig_js(code)
		elif player_type == 'swf':
			res=self._parse_sig_swf(code)
		else:
			raise Exception('Invalid player type %r!' % player_type)

		test_string = ''.join(map(unicode, range(len(example_sig))))
		cache_res = res(test_string)
		cache_spec = [ord(c) for c in cache_res]

#		l = ''.join(str(i)+"," for i in cache_spec)
#		import datetime
#		open(plugin.plugin_path+"/mytube.dic","w").write("%s:%s:%s\n" % (player_id,l[:-1],datetime.datetime.now().strftime("%d %b %Y")))

		return res

	def _parse_sig_js(self, jscode):
		funcname = self._search_regex(
            		(r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'(?P<sig>[a-zA-Z0-9$]+)\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)',
             		# Obsolete patterns
             		 r'(["\'])signature\1\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'yt\.akamaized\.net/\)\s*\|\|\s*.*?\s*[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?:encodeURIComponent\s*\()?\s*(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'\bc\s*&&\s*a\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
             		 r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
			 r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\('),
			 jscode, group='sig')

		jsi = JSInterpreter(jscode)
		initial_function = jsi.extract_function(funcname)
		return lambda s: initial_function([s])

	def _parse_sig_swf(self, file_contents):
		swfi = SWFInterpreter(file_contents)
		TARGET_CLASSNAME = 'SignatureDecipher'
		searched_class = swfi.extract_class(TARGET_CLASSNAME)
		initial_function = swfi.extract_function(searched_class, 'decipher')
		return lambda s: initial_function([s])



	# 24-Jun-2013: When use_cipher_signature=True, the signature must be
	# translated from lengths ranging from 82 to 88 back down to the 
	# original, unciphered length of 81 (40.40).
	#
	# This is not crypto or a hash, just a character-rearrangement cipher.
	# Total security through obscurity.  Total dick move.
	#
	# The implementation of this cipher used by the Youtube HTML5 video
	# player lives in a Javascript file with a name like:
	#   http://s.ytimg.com/yts/jsbin/html5player-VERSION.js
	# where VERSION changes periodically.  Sometimes the algorithm in the
	# Javascript changes, also.  So we name each algorithm according to
	# the VERSION string, and dispatch off of that.  Each time Youtube
	# rolls out a new html5player file, we will need to update the
	# algorithm accordingly.  See guessjs(), below. 
	#
	# So far, only three commands are used in the ciphers, so we can represent
	# them compactly:
	#
	# - r  = reverse the string;
	# - sN = slice from character N to the end;
	# - wN = swap 0th and Nth character.
	def _decrypt_signature2(self, s, js, name):
		cyphers = {'vflNzKG7n': 's3 r s2 r s1 r w67',   	    # 30 Jan 2013, untested
  			'vfllMCQWM':'s2 w46 r w27 s2 w43 s2 r',	    # 15 Feb 2013, untested
  			'vflJv8FA8':'s1 w51 w52 r',		    # 12 Mar 2013, untested
  			'vflR_cX32':'s2 w64 s3',			    # 11 Apr 2013, untested
  			'vflveGye9':'w21 w3 s1 r w44 w36 r w41 s1',    # 02 May 2013, untested
  			'vflj7Fxxt':'r s3 w3 r w17 r w41 r s2',	    # 14 May 2013, untested
  			'vfltM3odl':'w60 s1 w49 r s1 w7 r s2 r',	    # 23 May 2013
  			'vflDG7-a-':'w52 r s3 w21 r s3 r',  	    # 06 Jun 2013
  			'vfl39KBj1':'w52 r s3 w21 r s3 r',  	    # 12 Jun 2013
  			'vflmOfVEX':'w52 r s3 w21 r s3 r',  	    # 21 Jun 2013
  			'vflJwJuHJ':'r s3 w19 r s2',		    # 25 Jun 2013
  			'vfl_ymO4Z':'r s3 w19 r s2',		    # 26 Jun 2013
  			'vfl26ng3K':'r s2 r',			    # 08 Jul 2013
  			'vflcaqGO8':'w24 w53 s2 w31 w4',		    # 11 Jul 2013
  			'vflQw-fB4':'s2 r s3 w9 s3 w43 s3 r w23',      # 16 Jul 2013
  			'vflSAFCP9':'r s2 w17 w61 r s1 w7 s1',         # 18 Jul 2013
  			'vflART1Nf':'s3 r w63 s2 r s1',                # 22 Jul 2013
  			'vflLC8JvQ':'w34 w29 w9 r w39 w24',            # 25 Jul 2013
  			'vflm_D8eE':'s2 r w39 w55 w49 s3 w56 w2',      # 30 Jul 2013
  			'vflTWC9KW':'r s2 w65 r',                      # 31 Jul 2013
  			'vflRFcHMl':'s3 w24 r',                        # 04 Aug 2013
  			'vflM2EmfJ':'w10 r s1 w45 s2 r s3 w50 r',      # 06 Aug 2013
  			'vflz8giW0':'s2 w18 s3',                       # 07 Aug 2013
			'vfl_wGgYV':'w60 s1 r s1 w9 s3 r s3 r',        # 09 Aug 2013
			'vfl1HXdPb':'w52 r w18 r s1 w44 w51 r s1',     # 14 ago 2013
  			'vfl2LOvBh':'w34 w19 r s1 r s3 w24 r',         # 17 ago 2013
			'vflZK4ZYR':'w19 w68 s1',        	       # 23 ago 2013
			'vflh9ybst':'w48 s3 w37 s2',                   # 25 ago 2013
			'vflg0g8PQ':'w36 s3 r s2',		       # 29 ago 2013
			'vflg0g8PQ':'w36 s3 r s2',		       # 30 ago 2013
			'vflHOr_nV':'w58 r w50 s1 r s1 r w11 s3',      # 01 sep 2013
			'vfluy6kdb':'r w12 w32 r w34 s3 w35 w42 s2',   # 07 sep 2013
			'vflkuzxcs':'w22 w43 s3 r s1 w43',	       # 11 sep 2013
			'vflGNjMhJ':'w43 w2 w54 r w8 s1',	       # 13 sep 2013
			'vfldJ8xgI':'w11 r w29 s1 r s3',	       # 17 sep 2013
			}

		if js == None: return ""
    		if js in cyphers:
    			arr=cyphers[js]    
    		else:
 			arr = self.guessjs(js,name)

		return self.decode(s, arr)

    	def decode(self,sig, arr):
		sigA=sig
		if arr == "": return ""
		arr2 = arr.split(' ')
		for act in arr2:
			if act[0] == 'w':
				sigA = self.swap(sigA, act[1:])
			elif act == 'r':
				sigA = sigA[::-1]
			else:
				act2 = int(act[1:])
				sigA = sigA[act2:]
       		result=sigA
		if len(result) == 81:
			return result
		else:
      			return ""

	def swap(self,a,b):
		al = list(a)
		b=int(b)%len(a)
		c = al[0]
		al[0]=al[int(b)]
		al[int(b)]=c
		return ''.join(al)

	#### For download javascript and compose the algo to decode
	### the algo is writed in plugin_path/mytube.dic
	def guessjs(self,ver,name):
		import plugin
		cypher = ""
		try:
			f = open(plugin.plugin_path+"/mytube.dic", "r")
			for line in f:
				if ver in line:
					cypher=line.split(":")[1]
					break
			f.close()
		except:
			pass
		if cypher != "": return cypher

		url = "http://s.ytimg.com/yts/jsbin/html5player-%s.js" % ver

		try:
			script = urlopen2(url).read()
		except:
			print "[myTube] unable to download javascript code"
			return ""

 		if script:
  			# Find Wq in g=e.sig||Wq(e.s)
			try:
           			nameFunct = re.search('=.\.sig\|\|(.*?)\(', script).group(1)
			except:
				print "[myTube] unable to find decode name function"
				return ""

 			# Find body of function kj(D) { ... }
			try:
				Funct = re.search('function %s[^{]+{(.*?)}' % nameFunct.replace('$','\$'), script).group(1)
				print "[myTube] Function for decrypter is %s" %Funct
			except:
				print "[myTube] unable to find decode function %s" %nameFunct
				return ""

			try:
				for f in Funct.split(";"):
					if not "split" in f and not "join" in f and not "b=" in f and not "=b" in f:
						if ("reverse" in f):
							cypher = cypher + "r "    #reverse function
						elif "a.length" in f:
							par = f.split("%")[0].split("=")[1].split("[")[-1]
							cypher = cypher + "w%s " % par    #swap function
						elif "." in f and not "=" in f:
							par =  re.search('\((.*?)\)', f).group(1)
							par = par.split(",")[1]
							cypher = cypher + self.getfunction(f,script,par)
						else:
							par =  re.search('\((.*?)\)', f).group(1)
							if len(par.split(",")) == 2:
								par = par.split(",")[1]
								cypher = cypher + "w%s " % par    #swap function
							else:
								cypher = cypher + "s%s " % par    #slice function
			except:
				print "[myTube] unable to make cypher string for decrypt"
				return ""

			cypher = cypher.rstrip()
			import datetime
			open(plugin.plugin_path+"/mytube.dic", "a").write("%s:%s:%s\n" % (ver,cypher,datetime.datetime.now().strftime("%d %b %Y")))
			print "[myTube] Decode cypher is %s" %cypher
			return cypher

	def getfunction(self,func, script,par):
		cypher = ""
 		nfunc = func.split("(")[0]
 		nfunc = nfunc.split(".")[1]
 		# Find nfunc 
		try:
			Funct = re.search('%s:function[^{]+{(.*?)}' % nfunc.replace('$','\$'), script).group(1)
			print "[myTube] SubFunction for decrypter is %s" %Funct
		except:
			print "[myTube] unable to find decode subfunction %s" %nfunc
			return ""
		try:
			if "reverse" in Funct:
				cypher = "r "    #reverse function
			elif "a.length" in Funct:
				cypher = "w%s " % par    #swap function
			elif "splice" in Funct:
				cypher = "s%s " % par    #slice 	
			else:
				if len(par.split(",")) == 2:
					par = par.split(",")[1]
					cypher = "w%s " % par    #swap function
				else:
					cypher = "s%s " % par    #slice function
		except:
			print "[myTube] unable to make cypher string for decrypt"
			return ""
		return cypher

		
	###########################################################################################################################


	def getRelatedVideos(self):
		print "[MyTubeFeedEntry] getRelatedVideos()"
		for link in self.entry.link:
			#print "Related link: ", link.rel.endswith
			if link.rel.endswith("video.related"):
				print "Found Related: ", link.href
				return link.href

	def getResponseVideos(self):
		print "[MyTubeFeedEntry] getResponseVideos()"
		for link in self.entry.link:
			#print "Responses link: ", link.rel.endswith
			if link.rel.endswith("video.responses"):
				print "Found Responses: ", link.href
				return link.href
				
	def getUserVideos(self):
		print "[MyTubeFeedEntry] getUserVideos()"
		username = self.getUserId()
		myuri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % username
		print "Found Uservideos: ", myuri
		return myuri

class MyTubePlayerService():
#	Do not change the client_id and developer_key in the login-section!
#	ClientId: ytapi-dream-MyTubePlayer-i0kqrebg-0
#	DeveloperKey: AI39si4AjyvU8GoJGncYzmqMCwelUnqjEMWTFCcUtK-VUzvWygvwPO-sadNwW5tNj9DDCHju3nnJEPvFy4WZZ6hzFYCx8rJ6Mw

	cached_auth_request = {}
	current_auth_token = None
	yt_service = None

	def __init__(self):
		print "[MyTube] MyTubePlayerService - init"
		self.feedentries = []
		self.relatedToVideoId = None
		self.channelId = None
		self.feed = None
		self.order = None
		self.pageToken = None
		self.videoCategoryId = None
		self.q = None
		self.regionCode = None
		self.page = 1
		self.credentials = None
		self.safeSearch = "moderate"
		self.myplaylist = []
				
	def startService(self,auth_token=None):
		global youtube
		self.current_auth_token = auth_token

		print "[MyTube] MyTubePlayerService - startService"

		haskey = True
		if self.current_auth_token is None:
			if not DEVELOPER_KEY:
				haskey = self.readkeys(True)
			if haskey:
				youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
		else:
			if not YOUTUBE_API_CLIENT_ID or not YOUTUBE_API_CLIENT_SECRET:
				haskey = self.readkeys(False)
			if haskey:
				from oauth2client.client import AccessTokenCredentials
				import httplib2
				credentials = AccessTokenCredentials(self.current_auth_token,'mytube-spa/1.0')
				youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
		return haskey

	def readkeys(self, developer):
		global DEVELOPER_KEY
		global YOUTUBE_API_CLIENT_ID
		global YOUTUBE_API_CLIENT_SECRET
		if not fileExists("/etc/keys/mytube.key"):
			if not os_path.isdir('/etc/keys/'):
				mkdir('/etc/keys/')
			open("/etc/keys/mytube.key","w").write("API_KEY=\n")
			open("/etc/keys/mytube.key","a").write("CLIENT_ID=\n")
			open("/etc/keys/mytube.key","a").write("CLIENT_SECRET=\n")
			return False
		else:
			keys=open("/etc/keys/mytube.key","r")
			for line in keys:
				key = line.split("=")
				if len(key) == 2:
					if key[0].strip() == "API_KEY" and len(key[1])>0:
						DEVELOPER_KEY = key[1].strip()
					if key[0].strip() == "CLIENT_ID" and len(key[1])>0:
						YOUTUBE_API_CLIENT_ID = key[1].strip()
					if key[0].strip() == "CLIENT_SECRET" and len(key[1])>0:
						YOUTUBE_API_CLIENT_SECRET = key[1].strip()

		if developer and DEVELOPER_KEY:
			return True
		if not developer and YOUTUBE_API_CLIENT_ID and YOUTUBE_API_CLIENT_SECRET:
			return True
		return False

	def end(self):
		pass

	def stopService(self):
		print "[MyTube] MyTubePlayerService - stopService"
		del self.ytService
		
	def getLoginTokenOnCurl(self, email, pw):

		opts = {
		  'service':'youtube',
		  'accountType': 'HOSTED_OR_GOOGLE',
		  'Email': email,
		  'Passwd': pw,
		  'source': self.yt_service.client_id,
		}
		
		print "[MyTube] MyTubePlayerService - Starting external curl auth request"
		result = os.popen('curl -s -k -X POST "%s" -d "%s"' % (gdata.youtube.service.YOUTUBE_CLIENTLOGIN_AUTHENTICATION_URL , urlencode(opts))).read()
		
		return result

	def supportsSSL(self):
		return 'HTTPSConnection' in dir(httplib)

	def getFormattedTokenRequest(self, email, pw):
		return dict(parse_qsl(self.getLoginTokenOnCurl(email, pw).strip().replace('\n', '&')))
	
	def getAuthedUsername(self):
		# on external curl we can get real username
		if self.cached_auth_request.get('YouTubeUser') is not None:
			return self.cached_auth_request.get('YouTubeUser')

		if self.is_auth() is False:
			return ''

		# current gdata auth class save doesnt save realuser
		return 'Logged In'

	def auth_user(self):
		print "[MyTube] MyTubePlayerService - auth_use - "

		if not YOUTUBE_API_CLIENT_ID or not YOUTUBE_API_CLIENT_SECRET:
			self.readkeys(False)
		if not YOUTUBE_API_CLIENT_ID or not YOUTUBE_API_CLIENT_SECRET:
			return None
                try:                   
			from OAuth import OAuth
			return OAuth(YOUTUBE_API_CLIENT_ID, YOUTUBE_API_CLIENT_SECRET)
		except:
			return None


	def getuserplaylist(self):
#		try:
		self.myplaylist = youtube.channels().list(part="contentDetails",mine='true').execute()["items"]
#		except:
#			pass



	def getmyplaylist(self):
		return self.myplaylist

	def resetAuthState(self):
		print "[MyTube] MyTubePlayerService - resetting auth"
		self.cached_auth_request = {}
		self.current_auth_token = None

		if self.yt_service is None:
			return

		self.yt_service.current_token = None
		self.yt_service.token_store.remove_all_tokens()

	def is_auth(self):
		return self.current_auth_token is not None
#		if self.current_auth_token is not None:
#			return True		
		
#		if self.yt_service.current_token is None:
#			return False
		
#		return self.yt_service.current_token.get_token_string() != 'None'

	def auth_token(self):
		return self.yt_service.current_token.get_token_string()

	def getFeedService(self, feedname):
		if feedname == "top_rated":
			return self.yt_service.GetTopRatedVideoFeed
		elif feedname == "most_viewed":
			return self.yt_service.GetMostViewedVideoFeed
		elif feedname == "recently_featured":
			return self.yt_service.GetRecentlyFeaturedVideoFeed
		elif feedname == "top_favorites":
			return self.yt_service.GetTopFavoritesVideoFeed
		elif feedname == "most_recent":
			return self.yt_service.GetMostRecentVideoFeed
		elif feedname == "most_discussed":
			return self.yt_service.GetMostDiscussedVideoFeed
		elif feedname == "most_linked":
			return self.yt_service.GetMostLinkedVideoFeed
		elif feedname == "most_responded":
			return self.yt_service.GetMostRespondedVideoFeed
		return self.yt_service.GetYouTubeVideoFeed

	def getFeed(self, url, feedname = "", callback = None, errorback = None):
		global youtube
		print "[MyTube] MyTubePlayerService - getFeed:",url, feedname
		self.feedentries = []

		if feedname != _("More video entries."):
			self.feedname = feedname
			self.pageToken = None

		if config.plugins.mytube.general.showadult.value:
			self.safeSearch = "none"			

		self.regionCode = config.plugins.mytube.search.lr.value

		self.stype = ''
		if config.plugins.mytube.general.searchvideos.value:
			self.stype = self.stype + 'video,'
		if config.plugins.mytube.general.searchchannels.value:
			self.stype = self.stype + 'channel,'
		if len(self.stype)>1:
			self.stype = self.stype[:-1]

		if self.feedname == _("User video entries.") or self.feedname == "channel":
			self.stype = 'video'

		if self.feedname == "my_subscriptions":
			if feedname == _("More video entries."):
				self.pageToken = url
				self.page += 1
			else:
				self.page = 1
				self.pageToken = None
			
			request = youtube.subscriptions().list(
				mine=True,
				pageToken=self.pageToken,
				part="id,snippet",
				maxResults="25"
				)
				
		elif self.feedname == "my_favorites" or self.feedname == "my_history" or self.feedname == "my_watch_later" or self.feedname == "my_uploads" or self.feedname == "my_likes":

			if feedname == _("More video entries."):
				self.pageToken = url
				self.page += 1
			else:
				self.page = 1
				self.pageToken = None
				channels_response = youtube.channels().list(
  					mine=True,
  					part="contentDetails",
					).execute()
				for channel in channels_response["items"]:
  					# From the API response, extract the playlist ID that identifies the list
  					# of videos uploaded to the authenticated user's channel.
  					uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
  					#history_list_id = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]
  					#watchlater_list_id = channel["contentDetails"]["relatedPlaylists"]["watchLater"]
  					favorites_list_id = channel["contentDetails"]["relatedPlaylists"]["favorites"]
					likes_id = channel["contentDetails"]["relatedPlaylists"]["likes"]
				
				self.playid = None
				if self.feedname == "my_favorites":
					self.playid = favorites_list_id
				#elif self.feedname == "my_history":
				#	self.playid = history_list_id
				#elif self.feedname == "my_watch_later":
				#	self.playid = watchlater_list_id
				elif self.feedname == "my_uploads":
					self.playid = uploads_list_id
				elif self.feedname == "my_likes":
					self.playid = likes_id

			if self.playid != None:
				request = youtube.playlistItems().list(
					playlistId=self.playid,
					pageToken=self.pageToken,
					part="snippet",
					maxResults="25"
					)

		elif feedname == "top_rated":
			self.relatedToVideoId = None
			self.channelId = None
			self.page = 1
			self.q=None
			self.pageToken=None
			self.videoCategoryId = None
			self.order = "rating"
		elif feedname == "most_viewed":
			self.relatedToVideoId = None
			self.channelId = None
			self.page = 1
			self.q=None
			self.pageToken=None
			self.videoCategoryId = None
			self.order = "viewCount"
		elif feedname == _("More video entries."):
			self.page += 1
			self.pageToken=url
		elif feedname == _("User video entries.") or feedname == "channel":
			self.stype = 'video'
			self.relatedToVideoId = None
			self.channelId = url
			self.page = 1
			self.q=None
			self.pageToken=None
			self.videoCategoryId = None
			self.order = config.plugins.mytube.search.orderBy.value
		elif feedname == _("Related video entries."):
			self.relatedToVideoId = url
			self.channelId = None
			self.page = 1
			self.q=None
			self.pageToken=None
			self.videoCategoryId = None
			self.order = config.plugins.mytube.search.orderBy.value
		elif int(feedname)>0:
			self.relatedToVideoId = None
			self.channelId = None
			self.page = 1
			self.q=None
			self.pageToken=None
			self.videoCategoryId=feedname
			self.stype = 'video'
			self.order = config.plugins.mytube.search.orderBy.value


		if self.feedname != "my_favorites" and self.feedname != "my_history" and self.feedname != "my_watch_later" and self.feedname != "my_uploads" and self.feedname != "my_subscriptions" and self.feedname != "my_likes":
			request = youtube.search().list(
				regionCode = self.regionCode,
				order=self.order,
				videoCategoryId=self.videoCategoryId,
				pageToken=self.pageToken,
				relatedToVideoId=self.relatedToVideoId,
				channelId=self.channelId,
				safeSearch=self.safeSearch,
				q = self.q,
				part="id,snippet",
				maxResults="25",
				type=self.stype
				)
		
		queryThread = YoutubeQueryThread(request, url, self.gotFeed, self.gotFeedError, callback, errorback)
		#queryThread = YoutubeQueryThread(ytservice, url, self.gotFeed, self.gotFeedError, callback, errorback)	
		queryThread.start()
		return queryThread

	def search(self, searchTerms, startIndex = 1, maxResults = 25,
					orderby = "relevance", time = 'all_time', racy = "include",
					author = "", lr = "", categories = "", sortOrder = "ascending", 
					callback = None, errorback = None):
		global youtube
		print "[MyTube] MyTubePlayerService - search()"
		self.stype = ''
		if config.plugins.mytube.general.searchvideos.value:
			self.stype = self.stype + 'video,'
		if config.plugins.mytube.general.searchchannels.value:
			self.stype = self.stype + 'channel,'
		if len(self.stype)>1:
			self.stype = self.stype[:-1]
		self.page = 1
		self.pageToken = None
		self.channelId = None
		self.feedname = "search"
		self.relatedToVideoId = None
		self.channelId = None
		self.feedentries = []
		self.regionCode = config.plugins.mytube.search.lr.value
		#if config.plugins.mytube.search.categories.value != None:
		self.videoCategoryId = config.plugins.mytube.search.categories.value
		self.q = searchTerms
#		self.order = config.plugins.mytube.search.orderBy.value
		self.order = "relevance"  #the search in other orders fails
		if config.plugins.mytube.general.showadult.value:
			self.safeSearch = "none"			

		request = youtube.search().list(
			regionCode = self.regionCode,
			videoCategoryId=self.videoCategoryId,
			safeSearch=self.safeSearch,
			order=self.order,
			q=searchTerms,
			part="id,snippet",
			maxResults="25",
			type=self.stype
			)

		queryThread = YoutubeQueryThread(request, "", self.gotFeed, self.gotFeedError, callback, errorback)
		queryThread.start()
		return queryThread

	def getUserEntry(self, user = "default"):
		channels_response = youtube.channels().list(
			mine=True,
			part="snippet,statistics"
			).execute()
		for channel in channels_response["items"]:
			# From the API response, extract the playlist ID that identifies the list
			# of videos uploaded to the authenticated user's channel.
			username = str(channel["snippet"]["title"])
			img_url = channel["snippet"]["thumbnails"]["default"]["url"]
			view_count = int(channel["statistics"]["viewCount"])
			#coment_count = int(channel["statistics"]["commentCount"])
			subscriber_count = int(channel["statistics"]["subscriberCount"])
			video_count = int(channel["statistics"]["videoCount"])
			coment_count = 0

		return username, str(img_url), view_count, coment_count, subscriber_count, video_count 
	
	def gotFeed(self, feed, callback):
		if feed is not None:
			self.feed = feed
			for entry in self.feed['items']:
				MyFeedEntry = MyTubeFeedEntry(self, entry)
				self.feedentries.append(MyFeedEntry)
		if callback is not None:
			callback(self.feed)
			
	def gotFeedError(self, exception, errorback):
		if errorback is not None:
			errorback(exception)
	
	def SubscribeToUser(self, channel_id):
		try:
  			youtube.subscriptions().insert(
    				part='snippet',
    				body=dict(
      					snippet=dict(
        					resourceId=dict(
          						channelId=channel_id
        						)
      						)
    					)).execute()
			return _("Subscription Succesfully")
		except:
			return _("Subscription error")
	
	def UnSubscribeToUser(self, kid):
		try:
			youtube.subscriptions().delete(
				id=kid).execute()
			
			return _("Remove Subscription Succesfully")
		except:
			return _("Error: No remove Subscription")

	def addToFavorites(self, video_id,kind):
		try:
			channels_response = youtube.channels().list(
				mine=True,
				part="contentDetails",
				).execute()
			for channel in channels_response["items"]:
				favorites_list_id = channel["contentDetails"]["relatedPlaylists"]["favorites"]
			youtube.playlistItems().insert(
				part='snippet',
				body=dict(
					snippet=dict(
						playlistId=favorites_list_id,
						resourceId=dict(
							videoId=video_id,
							kind=kind
							)
						)
					)).execute()	
			return _("Video append to favorites")		
		except:
			return _("Error: No video append")
	
	def deletefromFavorites(self,kid):
		try:
			youtube.playlistItems().delete(
				id=kid).execute()
			
			return _("Video remove from favorites")
		except:
			return _("Error: No remove video from favorites")

	def setlike(self,video_id):
		try:
			youtube.videos().rate(
    				id=video_id,
    				rating="like"
  			).execute()
		except:
			print "[mytube] Error in like action"

	def setdislike(self,video_id):
		try:
			youtube.videos().rate(
    				id=video_id,
    				rating="dislike"
  			).execute()
		except:
			print "[mytube] Error in dislike action"


	def getTitle(self):
		#TODO
		return ""

	def getEntries(self):
		return self.feedentries

	def itemCount(self):
		#TODO
		return ""

	def getTotalResults(self):
		if self.feed["pageInfo"]["totalResults"] is None:
			return 0
				
		return self.feed["pageInfo"]["totalResults"]
	
	def getNextFeedEntriesURL(self):
		try:
			if self.feed["nextPageToken"]:
				return self.feed["nextPageToken"]
			return None
		except:
			return None

	def getCurrentPage(self):
		return self.page

class YoutubeQueryThread(Thread):
	def __init__(self, query, param, gotFeed, gotFeedError, callback, errorback):
		Thread.__init__(self)
		#self.messagePump = ePythonMessagePump()
		self.messages = ThreadQueue()
		self.gotFeed = gotFeed
		self.gotFeedError = gotFeedError
		self.callback = callback
		self.errorback = errorback
		self.query = query
		self.param = param
		self.canceled = False
		#self.messagePump.recv_msg.get().append(self.finished)
	
	def cancel(self):
		self.canceled = True
	
	def run(self):
		search_response = self.query.execute()
		self.gotFeed(search_response, self.callback)

		#try:
		#	if self.param is None:
		#		feed = self.query()
		#	else:
		#		feed = self.query(self.param)
		#	self.messages.push((True, feed, self.callback))
		#	self.messagePump.send(0)
		#except Exception, ex:
		#	self.messages.push((False, ex, self.errorback))
		#	self.messagePump.send(0)
	
	def finished(self, val):		
		if not self.canceled:
			message = self.messages.pop()
			if message[0]:		
				self.gotFeed(message[1], message[2])
			else:
				self.gotFeedError(message[1], message[2])
		
myTubeService = MyTubePlayerService()
