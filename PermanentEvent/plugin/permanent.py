# -*- coding: utf-8 -*-
# Credits for PermanetClock.
# PermanentEvent code by Villak OpenSPA Team 2021

from Components.ActionMap import ActionMap
from Components.config import config, ConfigInteger, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigSelectionNumber, getConfigListEntry, configfile, ConfigText, ConfigDirectory, ConfigPassword, ConfigNothing
from Components.ConfigList import ConfigListScreen
from Components.Language import language
from Components.MenuList import MenuList
from Components.Input import Input
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.ServiceList import refreshServiceList
from Components.Sources.Boolean import Boolean
from Components.SystemInfo import SystemInfo
from Components.Pixmap import Pixmap
from Components.SelectionList import SelectionList, SelectionEntryComponent
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import LocationBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from boxbranding import getBoxType, getMachineBrand, getMachineName, getImageDistro
from enigma import ePoint, getDesktop, addFont, eTimer, eLabel, eSize, ePoint, eServiceCenter, eServiceReference, iServiceInformation, eEPGCache, getBestPlayableServiceReference
from GlobalActions import globalActionMap
from keymapparser import readKeymap, removeKeymap
from PIL import Image
import gettext
import xml.etree.cElementTree
import os, re, datetime
import socket
import threading
import six

setup_path = resolveFilename(SCOPE_PLUGINS, "Extensions/PermanentEvent/")
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

_session = None
epgcache = eEPGCache.getInstance()

def setupdom(plugin=None):
	setupfile = open( setup_path + 'setup.xml', 'r')
	setupfiledom = xml.etree.cElementTree.parse(setupfile)
	setupfile.close()
	return setupfiledom

def getConfigMenuItem(configElement):
	for item in setupdom().getroot().findall('./setup/item/.'):
		if item.text == configElement:
			return _(item.attrib["text"]), eval(configElement)
	return "", None

class SetupError(Exception):
	def __init__(self, message):
		self.msg = message

	def __str__(self):
		return self.msg

class SetupSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["SetupTitle"] = StaticText(_(parent.setup_title))
		self["SetupEntry"] = StaticText("")
		self["SetupValue"] = StaticText("")
		if hasattr(self.parent,"onChangedEntry"):
			self.onShow.append(self.addWatcher)
			self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		if hasattr(self.parent,"onChangedEntry"):
			self.parent.onChangedEntry.append(self.selectionChanged)
			self.parent["config"].onSelectionChanged.append(self.selectionChanged)
			self.selectionChanged()

	def removeWatcher(self):
		if hasattr(self.parent,"onChangedEntry"):
			self.parent.onChangedEntry.remove(self.selectionChanged)
			self.parent["config"].onSelectionChanged.remove(self.selectionChanged)

	def selectionChanged(self):
		self["SetupEntry"].text = self.parent.getCurrentEntry()
		self["SetupValue"].text = self.parent.getCurrentValue()
		if hasattr(self.parent,"getCurrentDescription") and "description" in self.parent:
			self.parent["description"].text = self.parent.getCurrentDescription()
			if 'footnote' in self.parent:
				if self.parent.getCurrentEntry().endswith('*'):
					self.parent['footnote'].text = (_("* Restart Required."))
				else:
					self.parent['footnote'].text = (_(" "))

##########################################################SETTINGS###########################################################
config.plugins.PermanentEvent = ConfigSubsection()
config.plugins.PermanentEvent.enabled = ConfigYesNo(default=False)
config.plugins.PermanentEvent.position_x = ConfigInteger(default=100)
config.plugins.PermanentEvent.position_y = ConfigInteger(default=35)
config.plugins.PermanentEvent.show_hide = ConfigYesNo(default=False)
config.plugins.PermanentEvent_primetimehour = ConfigSelectionNumber (default = 22, stepwidth = 1, min = 00, max = 23, wraparound = True)
config.plugins.PermanentEvent_primetimemins = ConfigSelectionNumber(default = 00, stepwidth = 1, min = 00, max = 59, wraparound = True)
config.plugins.PermanentEvent.mode_event = ConfigSelection([('0', _('Current program with clock')),
 ('1', _('Next program with clock')),
 ('2', _('Current program with image')),
 ('3', _('Next program with image')),
 ('4', _('Primetime')),
 ('5', _('Primetime with image')),
 ('6', _('Current program')),
 ('7', _('Next program')),
 ('8', _('Primetime with image and hour'))], default='6')
config.plugins.PermanentEvent.loc = ConfigDirectory(default='/tmp/')
config.plugins.PermanentEvent.timerMod = ConfigYesNo(default = False)
config.plugins.PermanentEvent.timer = ConfigSelectionNumber(1, 168, 1, default=1)
config.plugins.PermanentEvent.searchbouquet =  ConfigSelection([('0', _('(Ok) to select bouquet'))], default='0')
imglist = []
for i in range(1, 250):
	if i == 20:
		imglist.append(_("now-next"))
	elif i == 50:
		imglist.append(_("primetime"))
	else:
		imglist.append(("%d" % i))
config.plugins.PermanentEvent.searchNUMBER = ConfigSelection(default = _("now-next"), choices = imglist)
config.plugins.PermanentEvent.downalerts = ConfigYesNo(default = True)
config.plugins.PermanentEvent.downfromchan = ConfigYesNo(default = False)
config.plugins.PermanentEvent.apis = ConfigYesNo(default = False)
config.plugins.PermanentEvent.tmdbAPI = ConfigText(default="", visible_width=100, fixed_size=False)
config.plugins.PermanentEvent.tvdbAPI = ConfigText(default="", visible_width=100, fixed_size=False)
config.plugins.PermanentEvent.fanartAPI = ConfigText(default="", visible_width=100, fixed_size=False)
config.plugins.PermanentEvent.searchLang = ConfigText(default="es", visible_width=100, fixed_size=False)
config.plugins.PermanentEvent.tmdb = ConfigYesNo(default = True)
config.plugins.PermanentEvent.tvdb = ConfigYesNo(default = False)
config.plugins.PermanentEvent.fanart = ConfigYesNo(default = False)
config.plugins.PermanentEvent.extra = ConfigYesNo(default = False)
config.plugins.PermanentEvent.extra2 = ConfigYesNo(default = False)
config.plugins.PermanentEvent.backdrop = ConfigYesNo(default = True)
config.plugins.PermanentEvent.cnfg = ConfigYesNo(default = False)
config.plugins.PermanentEvent.days = ConfigSelectionNumber (default = 30, stepwidth = 1, min = 00, max = 30, wraparound = True)
config.plugins.PermanentEvent.TMDBbackdropsize = ConfigSelection(default="w300", choices = [
	("w300", "300x170"), 
	("w780", "780x440"), 
	("w1280", "1280x720"),
	("original", "ORIGINAL")])

config.plugins.PermanentEvent.TVDBbackdropsize = ConfigSelection(default="thumbnail", choices = [
	("thumbnail", "640x360"), 
	("fileName", "original(1920x1080)")])

config.plugins.PermanentEvent.FANART_Backdrop_Resize = ConfigSelection(default="1", choices = [
	("2", "original/2"), 
	("1", "original")])

SKINCC = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/current_clock.xml"
SKINC = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/current.xml"
SKINN = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/next.xml"
SKINNC = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/next_clock.xml"
SKINCI = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/current_image.xml"
SKINNI = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/next_image.xml"
SKINP = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/primetime.xml"
SKINPI = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/primetime_image.xml"
SKINPIC = "/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/widgets/primetime_compact.xml"

##########################################################EVENTS###########################################################
class PermanentEventNewScreen(Screen):

		def __init__(self, session):
				if config.plugins.PermanentEvent.mode_event.value == '0':
						with open(SKINCC, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '1':
						with open(SKINNC, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '2':
						with open(SKINCI, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '3':
						with open(SKINNI, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '4':
						with open(SKINP, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '5':
						with open(SKINPI, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '6':
						with open(SKINC, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '7':
						with open(SKINN, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '8':
						with open(SKINPIC, 'r') as f:
							self.skin = f.read()

				Screen.__init__(self, session)
				self.onShow.append(self.movePosition)

		def movePosition(self):
				if self.instance:
						self.instance.move(ePoint(config.plugins.PermanentEvent.position_x.value, config.plugins.PermanentEvent.position_y.value))

class PermanentEvent():

		def __init__(self):
				self.dialog = None
				self.eventShown = False
				self.eventkey = False
				return

		def gotSession(self, session):
				self.dialog = session.instantiateDialog(PermanentEventNewScreen)
				self.showHide()
				self.unload_key(True)
				self.start_key()

		def start_key(self):
				if config.plugins.PermanentEvent.show_hide.value and not self.eventkey:
						if 'showEvent' not in globalActionMap.actions:
								readKeymap('/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/keymap.xml')
								globalActionMap.actions['showEvent'] = self.ShowHideKey
						self.eventkey = True

		def unload_key(self, force = False):
				if not config.plugins.PermanentEvent.show_hide.value and self.eventkey or force:
						removeKeymap('/usr/lib/enigma2/python/Plugins/Extensions/PermanentEvent/keymap.xml')
						if 'showEvent' in globalActionMap.actions:
								del globalActionMap.actions['showEvent']
						self.eventkey = False

		def ShowHideKey(self):
				if config.plugins.PermanentEvent.enabled.value:
						if self.eventShown:
								self.eventShown = False
								self.dialog.show()
						else:
								self.eventShown = True
								self.dialog.hide()
				return 0

		def changeVisibility(self):
				if config.plugins.PermanentEvent.enabled.value:
						config.plugins.PermanentEvent.enabled.value = False
				else:
						config.plugins.PermanentEvent.enabled.value = True
				config.plugins.PermanentEvent.enabled.save()
				self.showHide()

		def Widgetype(self):
				config.plugins.PermanentEvent.mode_event.save()
				self.dialog = None
				return

		def changeKey(self):
				if config.plugins.PermanentEvent.show_hide.value:
						config.plugins.PermanentEvent.show_hide.value = False
				else:
						config.plugins.PermanentEvent.show_hide.value = True
				config.plugins.PermanentEvent.show_hide.save()

		def showHide(self):
				if config.plugins.PermanentEvent.enabled.value:
						self.dialog.show()
				else:
						self.dialog.hide()

pEvent = PermanentEvent()

class PermanentEventPositioner(Screen):

		def __init__(self, session):
				if config.plugins.PermanentEvent.mode_event.value == '0':
						with open(SKINCC, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '1':
						with open(SKINNC, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '2':
						with open(SKINCI, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '3':
						with open(SKINNI, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '4':
						with open(SKINP, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '5':
						with open(SKINPI, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '6':
						with open(SKINC, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '7':
						with open(SKINN, 'r') as f:
							self.skin = f.read()
				elif config.plugins.PermanentEvent.mode_event.value == '8':
						with open(SKINPIC, 'r') as f:
							self.skin = f.read()

				Screen.__init__(self, session)
				self['actions'] = ActionMap(['WizardActions'], {'left': self.left,
				 'up': self.up,
				 'right': self.right,
				 'down': self.down,
				 'ok': self.ok,
				 'back': self.exit}, -1)
				self.desktopWidth = getDesktop(0).size().width()
				self.desktopHeight = getDesktop(0).size().height()
				self.slider = 1
				self.onLayoutFinish.append(self.__layoutFinished)

		def __layoutFinished(self):
				self.movePosition()

		def movePosition(self):
				self.instance.move(ePoint(config.plugins.PermanentEvent.position_x.value, config.plugins.PermanentEvent.position_y.value))

		def left(self):
				value = config.plugins.PermanentEvent.position_x.value
				value -= self.slider
				if value < 0:
						value = 0
				config.plugins.PermanentEvent.position_x.value = value
				self.movePosition()

		def up(self):
				value = config.plugins.PermanentEvent.position_y.value
				value -= self.slider
				if value < 0:
						value = 0
				config.plugins.PermanentEvent.position_y.value = value
				self.movePosition()

		def right(self):
				value = config.plugins.PermanentEvent.position_x.value
				value += self.slider
				if value > self.desktopWidth:
						value = self.desktopWidth
				config.plugins.PermanentEvent.position_x.value = value
				self.movePosition()

		def down(self):
				value = config.plugins.PermanentEvent.position_y.value
				value += self.slider
				if value > self.desktopHeight:
						value = self.desktopHeight
				config.plugins.PermanentEvent.position_y.value = value
				self.movePosition()

		def ok(self):
				menu = [(_('Save position widget'), 'save'), (_('Set slider'), 'slider')]
				def extraAction(choice):
						if choice is not None:
								if choice[1] == 'slider':
										self.session.openWithCallback(self.setSliderStep, InputBox, title= _('Set slider step (1 - 20):'), text=str(self.slider), type=Input.NUMBER)
								elif choice[1] == 'save':
										self.Save()
						return
				help_txt = _('The value of the slider is used to move the widget faster or slower. Slider value of (1 - 20).')
				self.session.openWithCallback(extraAction, ChoiceBox, title=_('Save position or set slider valor...')+ "\n" + help_txt , list = menu)

		def setSliderStep(self, step):
				if step and 0 < int(step) < 21:
						self.slider = int(step)

		def Save(self):
				config.plugins.PermanentEvent.position_x.save()
				config.plugins.PermanentEvent.position_y.save()
				self.close()

		def exit(self):
				config.plugins.PermanentEvent.position_x.cancel()
				config.plugins.PermanentEvent.position_y.cancel()
				self.close()

genhelp_txt = _('Activate Permanent Event, choose the widget you like the most, if you choose primetime widget, choose the time of maximum audience, and finally, place the widget where you like the most!')
class PermanentEventMenu(Screen):
		def __init__(self, session):
				self.session = session
				Screen.__init__(self, session)
				self['list'] = MenuList([])
				self["text"] = ScrollLabel("")
				self["text"].setText(genhelp_txt)
				self.setTitle(_('Permanent Event Setup'))
				self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.okClicked,
				 'cancel': self.close}, -1)
				self.onLayoutFinish.append(self.showMenu)

		def showMenu(self):
				list = []
				if config.plugins.PermanentEvent.enabled.value:
						list.append(_(' Deactivate permanent event'))
						list.append(_(' Select widget type'))
						list.append(_(' Primetime hour'))
						list.append(_(' Config Images for Events'))
						list.append(_(' Change permanent event position'))
				else:
						list.append(_(' Activate permanent event'))
				if config.plugins.PermanentEvent.enabled.value:
						if config.plugins.PermanentEvent.show_hide.value:
								list.append(_(" Disable key 'long EXIT' show/hide"))
						else:
								list.append(_(" Enable key 'long EXIT' show/hide"))
				self['list'].setList(list)

		def newConfig(self, typewidget = False):
				pEvent.dialog.hide()
				pEvent.Widgetype()
				if pEvent.dialog is None:
						pEvent.gotSession(self.session)
				return

		def okClicked(self):
				sel = self['list'].getCurrent()
				if pEvent.dialog is None:
						pEvent.gotSession(self.session)
				if sel == _(' Deactivate permanent event') or sel == _(' Activate permanent event'):
						pEvent.changeVisibility()
						self.showMenu()
				if sel == _(' Change permanent event position'):
						pEvent.dialog.hide()
						self.session.openWithCallback(self.positionerCallback, PermanentEventPositioner)
				if sel == _(' Select widget type'):
						if pEvent.dialog is not None:
#								pEvent.dialog.hide()
								self.typewidget()
								self.showMenu()
#								if pEvent.dialog is None:
#										pEvent.gotSession(self.session)
				if sel == _(" Disable key 'long EXIT' show/hide"):
						if pEvent.dialog is not None:
								pEvent.changeKey()
								self.showMenu()
								pEvent.unload_key()
				if sel == _(" Enable key 'long EXIT' show/hide"):
						if pEvent.dialog is not None:
								pEvent.changeKey()
								self.showMenu()
								pEvent.start_key()
				if sel == _(' Primetime hour'):
						self.session.openWithCallback(self.setupFinished, Primetimehour)
				if sel == _(' Config Images for Events'):
						self.session.openWithCallback(self.setupFinished, downImages, "downImages")
					
				return

		def setupFinished(self,index=None, entry = None):
				pass

		def typewidget(self):
				help_txt = _('In order to use the image widgets, you must activate "backdrops" in the PermanentEvents plugin.')
				list = [(_('Current program'), self.skinsC),
				 (_('Current program with clock'), self.skinsCC),
				 (_('Current program with image'), self.skinsCI),
				 (_('Next program'), self.skinsN),
				 (_('Next program with clock'), self.skinsNC),
				 (_('Next program with image'), self.skinsNI),
				 (_('Primetime'), self.skinsP),
				 (_('Primetime with image'), self.skinsPI),
				 (_('Primetime with image and hour'), self.skinsPIC)]
				self.session.openWithCallback(self.menuCallback, ChoiceBox, title=_('Choose widget type...')+ "\n" + help_txt , list = list)

		def menuCallback(self, ret = None):
				ret and ret[1]()

		def positionerCallback(self, callback = None):
				pEvent.showHide()

		def skinsCC(self):
				config.plugins.PermanentEvent.mode_event.value = '0'
				self.newConfig(typewidget=True)

		def skinsNC(self):
				config.plugins.PermanentEvent.mode_event.value = '1'
				self.newConfig(typewidget=True)

		def skinsCI(self):
				config.plugins.PermanentEvent.mode_event.value = '2'
				self.newConfig(typewidget=True)
#				self.changew()

		def skinsNI(self):
				config.plugins.PermanentEvent.mode_event.value = '3'
				self.newConfig(typewidget=True)
#				self.changew()

		def skinsP(self):
				config.plugins.PermanentEvent.mode_event.value = '4'
				self.newConfig(typewidget=True)

		def skinsPI(self):
				config.plugins.PermanentEvent.mode_event.value = '5'
				self.newConfig(typewidget=True)
#				self.changew()

		def skinsC(self):
				config.plugins.PermanentEvent.mode_event.value = '6'
				self.newConfig(typewidget=True)

		def skinsN(self):
				config.plugins.PermanentEvent.mode_event.value = '7'
				self.newConfig(typewidget=True)

		def skinsPIC(self):
				config.plugins.PermanentEvent.mode_event.value = '8'
				self.newConfig(typewidget=True)
#				self.changew()

		def changew(self):
				self.session.openWithCallback(self.restart, MessageBox, _("Do you want to restart now, to change widget?"), MessageBox.TYPE_YESNO, timeout = 10)

		def restart(self, answer):
				if answer is True:
					self.newConfig(typewidget=True)
					self.session.open(TryQuitMainloop, 3)
				else:
					self.close()

#####################################################################HOUR PRIME#########################################

help_txthour = _("Pick the time for primetime...(+20 minutes tolerance)")
class Primetimehour(Screen, ConfigListScreen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("Primetime hour"))
		self.list = []
		self.list.append(getConfigListEntry(_("Primetime hour"), config.plugins.PermanentEvent_primetimehour))
		self.list.append(getConfigListEntry(_("Primetime minute"), config.plugins.PermanentEvent_primetimemins))
		ConfigListScreen.__init__(self, self.list, session=session)
		self["text"] = ScrollLabel("")
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["text"].setText(help_txthour)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			"ok": self.save,
			#"yellow": self.getdata,
		}, -2)

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)

	def save(self, mode = True):
		if mode:
			pEvent.dialog.hide()
			self.session.open(MessageBox,_('PrimeTime hour added!'), MessageBox.TYPE_INFO, timeout=5)
			pEvent.gotSession(self.session)
		for i in self["config"].list:
			i[1].save()
			configfile.save()
			self.close()

##########################################################DOWNLOAD IMAGES#######################################################################
class downImages(ConfigListScreen, Screen):
	ALLOW_SUSPEND = True

	def removeNotifier(self):
		self.onNotifiers.remove(self.levelChanged)

	def levelChanged(self, configElement):
		list = []
		self.refill(list)
		self["config"].setList(list)

	def refill(self, listItems):
		xmldata = setupdom(self.plugin).getroot()
		for x in xmldata.findall("setup"):
			if x.get("key") != self.setup:
				continue
			self.addItems(listItems, x)
			self.setup_title = six.ensure_str(x.get("title", ""))
			self.seperation = int(x.get('separation', '0'))

	def __init__(self, session, setup, plugin=None):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = ["setup_" + setup, "downImages" ]

		self['footnote'] = Label()
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)
		self["status"] = StaticText()
		self.onChangedEntry = [ ]
		self.item = None
		self.setup = setup
		self.plugin = plugin
		list = []
		self.onNotifiers = [ ]
		self.refill(list)
		ConfigListScreen.__init__(self, list, session = session, on_change = self.changedEntry)
		self.createSetup()

		self['key_red'] = Label(_('Close'))
		self['key_green'] = Label(_('Delete IMG'))
		self['key_yellow'] = Label(_('Optimize IMG'))
		self['key_blue'] = Label(_('Broken IMG Remove'))
		self["description"] = Label("")
		self.setTitle(_("PermanentEvent..."))
		self['storage'] = Label()
		self['info'] = Label()
		self['gain'] = Label()
		self['finalsize'] = Label()
		self['int_statu'] = Label()
		self.intCheck()
		self["actions"] = ActionMap(["SetupActions", "OkCancelActions", "ColorActions"],
		{
			"red": self.exit,
			"green": self.erase,
			"yellow": self.compressImg,
			"blue": self.brokenImageRemove,
			"cancel": self.exit,
			"ok": self.keyOK,
			"info": self.strg,
		},-1)

		self["VirtualKB"] = ActionMap(["VirtualKeyboardActions"],
		{
			"showVirtualKeyboard": self.KeyText,
		}, -2)
		self["VirtualKB"].setEnabled(False)

		if not self.handleInputHelpers in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.handleInputHelpers)
		self.changedEntry()
		self.onLayoutFinish.append(self.layoutFinished)
		self.onClose.append(self.HideHelp)

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
			filepath = pathLoc+ "backdrop/"
			folder_size=sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
			backdrops_sz = "%0.1f" % (folder_size/(1024*1024.0))
			backdrop_nmbr = len(os.listdir(filepath))
			self['storage'].setText(_("Storage folder...") + "\n{}".format (filepath))
			self['info'].setText(_("Total Backdrops : ") + "{}".format(backdrop_nmbr))
			self['gain'].setText(_("Size : ") + "{} MB.".format(backdrops_sz))
			self['finalsize'].setText(_(" ").format())
		except:
			pass

	def keyOK(self):
		if self['config'].getCurrent()[1] is config.plugins.PermanentEvent.loc:
			self.session.openWithCallback(self.pathSelected, LocationBox, text=_('Default Folder'), currDir=config.plugins.PermanentEvent.loc.getValue(), minFree=100)
		if self['config'].getCurrent()[1] is config.plugins.PermanentEvent.searchbouquet:
			self.session.open(selBouquets)
			for x in self["config"].list:
				if len(x) > 1:
					x[1].save()
			configfile.save()

	def pathSelected(self, res):
		if res is not None:
			config.plugins.PermanentEvent.loc.value = res
			pathLoc = config.plugins.PermanentEvent.loc.value + "PermanentEvent/"
			if not os.path.isdir(pathLoc):
				os.makedirs(pathLoc + "backdrop")
			self.session.openWithCallback(self.restart, MessageBox, _("Do you want to restart now, to change location? \nIf you use Timer, you will have to choose bouquet list again on restart."), MessageBox.TYPE_YESNO, timeout = 20)

	def restart(self, answer):
		if answer is True:
			for x in self["config"].list:
				if len(x) > 1:
					x[1].save()
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.exit()

	def compressImg(self):
		import sys
		filepath = pathLoc + "backdrop"
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
			self['storage'].setText(_("Storage folder...") + "\n{}/".format (filepath))
			self['info'].setText(_("Total Images Optimized : ") + "{}".format(len(lstdr)))
			self['gain'].setText(_("Gain : ") + "{}MB. ↪️ {}MB.".format (finalsize,old_size))
			self['finalsize'].setText(_("Final Size : ") + "{}MB".format (new_size))

	def brokenImageRemove(self):
		b = os.listdir(pathLoc)
		rmvd = 0
		filepath = pathLoc + "backdrop"
		folder_size = sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
		old_size = "%0.1f" % (folder_size/(1024*1024.0))
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
		folder_size = sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
		new_size = "%0.1f" % (folder_size/(1024*1024.0))
		finalsize = (float(old_size) - float(new_size))
		self['storage'].setText(_("Storage folder...") + "\n{}/".format (filepath))
		self['info'].setText(_("Removed Broken Images : ") + "{}".format(str(rmvd)))
		self['gain'].setText(_("Gain : ") + "{}MB. ↪️ {}MB.".format (finalsize,old_size))
		self['finalsize'].setText(_("Final Size : ") + "{}MB".format (new_size))

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()
		configfile.save()
		self.close()

	def erase(self):
		self.session.openWithCallback(self.eraseyes, MessageBox, _("Are you sure you want to delete the images?"), MessageBox.TYPE_YESNO, timeout = 15)

	def eraseyes(self, answer):
		if answer is True:
			try:
				import sys
				path = [pathLoc+ "backdrop"]
				filepath = pathLoc + "backdrop/"
				formato = '%d-%m-%y'
				hoy = datetime.datetime.now()
				daysn = config.plugins.PermanentEvent.days.value
				dia = hoy - datetime.timedelta(days=daysn)
	#			print hoy
	#			print dia
				rmvd = 0
				folder_size = sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
				old_size = "%0.1f" % (folder_size/(1024*1024.0))
				for folder in path :
					print(folder)
					llista = os.listdir(folder)
					for file in llista:
	#					print file
						archivo = folder + os.sep + file
						estado = os.stat(archivo)
						modificado = datetime.datetime.fromtimestamp(estado.st_mtime)
	#					print modificado
						if modificado < dia :
							os.remove(archivo)
							rmvd += 1
				folder_size = sum([sum([os.path.getsize(os.path.join(filepath, fname)) for fname in files]) for filepath, folders, files in os.walk(filepath)])
				new_size = "%0.1f" % (folder_size/(1024*1024.0))
				finalsize = (float(old_size) - float(new_size))
				self['storage'].setText(_("Storage folder...") + "\n{}".format (filepath))
				self['info'].setText(_("Total Removed Images : ") + "{}".format(str(rmvd)))
				self['gain'].setText(_("Gain : ") + "{}MB. ↪️ {}MB.".format (finalsize,old_size))
				self['finalsize'].setText(_("Final Size : ") + "{}MB".format (new_size)) 
			except:
				pass
		else:
			pass

##############################################################SETUP CONFIG################################################################
	def refreshServiceList(configElement = None):
		from Screens.InfoBar import InfoBar
		InfoBarInstance = InfoBar.instance
		if InfoBarInstance is not None:
			servicelist = InfoBarInstance.servicelist
			if servicelist:
				servicelist.setMode()

	def createSetup(self):
		list = []
		self.refill(list)
		self["config"].setList(list)
#		if config.usage.sort_settings.value:
#			self["config"].list.sort()
#		self.moveToItem(self.item)

	def getIndexFromItem(self, item):
		if item is not None:
			for x in range(len(self["config"].list)):
				if self["config"].list[x][0] == item[0]:
					return x
		return None

	def moveToItem(self, item):
		newIdx = self.getIndexFromItem(item)
		if newIdx is None:
			newIdx = 0
		self["config"].setCurrentIndex(newIdx)

	def handleInputHelpers(self):
		self["status"].setText(self["config"].getCurrent()[2])
		if self["config"].getCurrent() is not None:
			try:
				if isinstance(self["config"].getCurrent()[1], ConfigText) or isinstance(self["config"].getCurrent()[1], ConfigPassword):
					if "VKeyIcon" in self:
						self["VirtualKB"].setEnabled(True)
						self["VKeyIcon"].boolean = True
					if "HelpWindow" in self:
						if self["config"].getCurrent()[1].help_window.instance is not None:
							helpwindowpos = self["HelpWindow"].getPosition()
							from enigma import ePoint
							self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0],helpwindowpos[1]))
				else:
					if "VKeyIcon" in self:
						self["VirtualKB"].setEnabled(False)
						self["VKeyIcon"].boolean = False
			except:
				if "VKeyIcon" in self:
					self["VirtualKB"].setEnabled(False)
					self["VKeyIcon"].boolean = False
		else:
			if "VKeyIcon" in self:
				self["VirtualKB"].setEnabled(False)
				self["VKeyIcon"].boolean = False

	def HideHelp(self):
		self.help_window_was_shown = False
		try:
			if isinstance(self["config"].getCurrent()[1], ConfigText) or isinstance(self["config"].getCurrent()[1], ConfigPassword):
				if self["config"].getCurrent()[1].help_window.instance is not None:
					self["config"].getCurrent()[1].help_window.hide()
					self.help_window_was_shown = True
		except:
			pass

	def KeyText(self):
		if isinstance(self["config"].getCurrent()[1], ConfigText) or isinstance(self["config"].getCurrent()[1], ConfigPassword):
			if self["config"].getCurrent()[1].help_window.instance is not None:
				self["config"].getCurrent()[1].help_window.hide()
		from Screens.VirtualKeyBoard import VirtualKeyBoard
		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title = self["config"].getCurrent()[0], text = self["config"].getCurrent()[1].value)

	def VirtualKeyBoardCallback(self, callback = None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())

	def layoutFinished(self):
		self.setTitle(_(self.setup_title))

	# for summary:
	def changedEntry(self):
		self.item = self["config"].getCurrent()
		try:
			#FIXME This code prevents an LCD refresh for this ConfigElement(s)
			if not isinstance(self["config"].getCurrent()[1], ConfigText):
				self.createSetup()
		except:
			pass

	def addItems(self, listItems, parentNode):
		for x in parentNode:
			if not x.tag:
				continue
			if x.tag == 'item':
				item_level = int(x.get("level", 0))
				item_tunerlevel = int(x.get("tunerlevel", 0))
				item_rectunerlevel = int(x.get("rectunerlevel", 0))
				item_tuxtxtlevel = int(x.get("tt_level", 0))

				if not self.onNotifiers:
					self.onNotifiers.append(self.levelChanged)
					self.onClose.append(self.removeNotifier)

				if item_level > config.usage.setup_level.index:
					continue
				if (item_tuxtxtlevel == 1) and (config.usage.tuxtxt_font_and_res.value != "expert_mode"):
					continue
				if item_tunerlevel == 1 and not config.usage.frontend_priority.value in ("expert_mode", "experimental_mode"):
					continue
				if item_tunerlevel == 2 and not config.usage.frontend_priority.value == "experimental_mode":
					continue
				if item_rectunerlevel == 1 and not config.usage.recording_frontend_priority.value in ("expert_mode", "experimental_mode"):
					continue
				if item_rectunerlevel == 2 and not config.usage.recording_frontend_priority.value == "experimental_mode":
					continue

				requires = x.get("requires")
				if requires:
					meets = True
					for requires in requires.split(';'):
						negate = requires.startswith('!')
						if negate:
							requires = requires[1:]
						if requires.startswith('config.'):
							try:
								item = eval(requires)
								SystemInfo[requires] = True if item.value and item.value not in ("0", "False", "false", "off") else False
							except AttributeError:
								print('[Setup] unknown "requires" config element:', requires)

						if requires:
							if not SystemInfo.get(requires, False):
								if not negate:
									meets = False
									break
							else:
								if negate:
									meets = False
									break
					if not meets:
						continue

			
				item_text = _(six.ensure_str(x.get("text", "??")))
				item_description = _(six.ensure_str(x.get("description", " ")))
				item_text = item_text.replace("%s %s", "%s %s" % (getMachineBrand(), getMachineName()))
				item_description = item_description.replace("%s %s", "%s %s" % (getMachineBrand(), getMachineName()))
				b = eval(x.text or "")
				if b == "":
					continue
				#add to configlist
				item = b
				# the first b is the item itself, ignored by the configList.
				# the second one is converted to string.
				if not isinstance(item, ConfigNothing):
					listItems.append((item_text, item, item_description))

##############################################################BOUQUET CONF################################################################

help_txt = _("Choose favorites list to download...")
class selBouquets(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.bouquets = bqtList()
		# self.epgcache = eEPGCache.getInstance()
		self.skinName = ["selectBouquets"]
		self.setTitle(_("Bouquet Selection..."))
		self.sources = [SelectionEntryComponent(s[0], s[1], 0, (s[0] in ["sources"])) for s in self.bouquets]
		self["list"] = SelectionList(self.sources)
		self["text"] = ScrollLabel("")
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
		self['int_statu'] = Label()
		self["text"].setText(help_txt)
		self.intCheck()
		self['info'] = Label()

	def bouquetEpgs(self):
		if os.path.exists(pathLoc+"bqts"):
			os.remove(pathLoc+"bqts")
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
			self.close()

	def withTimerDownload(self):
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

	def intCheck(self):
		try:
			socket.setdefaulttimeout(2)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
			self['int_statu'].setText("●")
			# return True
		except:
			return False

	def download(self):
		from . import download
		threading.Thread(target=self.down).start()

	def brokenImageRemove(self):
		b = os.listdir(pathLoc)
		rmvd = 0
		try:
			for i in b:
				bb = "{}PermanentEvent/backdrop/".format(pathLoc, i)
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

#####################################################PATHLOC###############################################################
class pathLocation():
	def __init__(self):
		self.location()

	def location(self):
		pathLoc = ""
		if not os.path.isdir(config.plugins.PermanentEvent.loc.value):
			pathLoc = "/tmp/PermanentEvent/"
			try:
				if not os.path.isdir(pathLoc):
					os.makedirs(pathLoc + "backdrop")
			except:
				pass
		else:
			pathLoc = config.plugins.PermanentEvent.loc.value + "PermanentEvent/"
			try:
				if not os.path.isdir(pathLoc):
					os.makedirs(pathLoc + "backdrop")
			except:
				pass
		return pathLoc
pathLoc = pathLocation().location()

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

def sessionstart(reason, **kwargs):
		global _session
		if reason == 0 and _session is None:
				_session = kwargs['session']
				if _session:
						pEvent.gotSession(_session)
		return
