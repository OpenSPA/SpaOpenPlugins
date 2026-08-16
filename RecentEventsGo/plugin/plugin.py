# -*- coding: utf-8 -*-
# Plugin developed by VillaK for OpenSpa.
# Show Recently Started Events from InfoBar.

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.config import config, ConfigSubsection, ConfigText, ConfigInteger, getConfigListEntry, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from enigma import eServiceCenter, eServiceReference, eEPGCache, eListboxPythonMultiContent, gFont, \
    RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, BT_SCALE, BT_KEEP_ASPECT_RATIO
from Plugins.Plugin import PluginDescriptor
from Tools.LoadPixmap import LoadPixmap
from Components.Renderer.Picon import getPiconName
from Components.SelectionList import SelectionList, SelectionEntryComponent
import time


# ─── Traducciones ────────────────────────────────────────────────────────────────────
import gettext
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
try:
    lang = gettext.translation(
        "RecentEventsGo",
        resolveFilename(SCOPE_PLUGINS, "Extensions/RecentEventsGo/locale"),
        fallback=True
    )
    _ = lang.gettext
except:
    _ = lambda x: x


# ─── Skin ────────────────────────────────────────────────────────────────────
from skin import loadSkin
from os import path
loadSkin(path.join(path.dirname(__file__), "skin/skin.xml"))


# ─── Configuración persistente ───────────────────────────────────────────────
# SUSTITUYE el bloque config.plugins.recentstarts que ya tienes
config.plugins.recentstarts = ConfigSubsection()
config.plugins.recentstarts.bouquet_refs      = ConfigText(default="")
config.plugins.recentstarts.bouquet_name      = ConfigText(default=_("(none)"))
config.plugins.recentstarts.minutes_threshold = ConfigInteger(default=5, limits=(1, 20))
config.plugins.recentstarts.hotkey            = ConfigSelection(
    default="text",
    choices=[
        ("text",     _("Teletext")),
        ("green",    _("Green")),
        ("yellow",   _("Yellow")),
        ("blue",     _("Blue")),
        ("red",      _("Red")),
        ("info",     _("Info")),
        ("epg",      _("EPG")),
        ("audio",    _("Audio")),
        ("subtitle", _("Subtitle")),
        ("f1",       _("F1")),
        ("f2",       _("F2")),
        ("f3",       _("F3")),
        ("f4",       _("F4")),
    ]
)


# ─── Pantalla de selección de bouquets ───────────────────────────────────────
class BouquetSelectScreen(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("Select Bouquets"))
        self["list"]       = SelectionList([], enableWrapAround=True)
        self["key_red"]    = Label(_("Cancel"))
        self["key_green"]  = Label(_("Save"))
        self["key_yellow"] = Label(_("Mark/Unmark"))
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok":     self.toggle,
                "yellow": self.toggle,
                "green":  self.save,
                "red":    self.close,
                "cancel": self.close,
            }, -1
        )
        self.bouquets = []
        self.selected = set()
        self.onLayoutFinish.append(self.loadBouquets)

    def loadBouquets(self):
        self.bouquets = []
        self.selected = set()
        serviceHandler = eServiceCenter.getInstance()
        bouquets_ref = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet')
        bouquetList = serviceHandler.list(bouquets_ref)
        if bouquetList is None:
            return
        while True:
            service = bouquetList.getNext()
            if not service or service.valid() == 0:
                break
            info = serviceHandler.info(service)
            name = info and info.getName(service) or service.toString()
            self.bouquets.append((name, service.toString().strip()))

        saved = [r.strip() for r in config.plugins.recentstarts.bouquet_refs.value.split("|") if r.strip()]
        items = []
        for i, (name, ref) in enumerate(self.bouquets):
            checked = ref in saved
            if checked:
                self.selected.add(i)
            items.append(SelectionEntryComponent(name, ref, i, checked))
        self["list"].setList(items)

    def toggle(self):
        idx = self["list"].getCurrentIndex()
        self["list"].toggleSelection()
        if idx in self.selected:
            self.selected.discard(idx)
        else:
            self.selected.add(idx)

    def save(self):
        refs  = [self.bouquets[i][1] for i in sorted(self.selected)]
        names = [self.bouquets[i][0] for i in sorted(self.selected)]
        config.plugins.recentstarts.bouquet_refs.value = "|".join(refs)
        config.plugins.recentstarts.bouquet_name.value = ", ".join(names) if names else _("(none)")
        config.plugins.recentstarts.bouquet_refs.save()
        config.plugins.recentstarts.bouquet_name.save()
        self.close(True)


# ─── Pantalla de configuración ────────────────────────────────────────────────
class RecentStartsConfig(ConfigListScreen, Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("RecentEventsGo - Configuration"))
        self["bouquet_label"] = Label(_("Bouquets: ") + config.plugins.recentstarts.bouquet_name.value)
        self["key_red"]    = Label(_("Cancel"))
        self["key_green"]  = Label(_("Save"))
        self["key_yellow"] = Label(_("Choose Bouquets"))

        cfglist = [
            getConfigListEntry(_("Minutes from start (threshold):"),
                               config.plugins.recentstarts.minutes_threshold),
            getConfigListEntry(_("Hotkey in InfoBar:"),
                               config.plugins.recentstarts.hotkey),
        ]
        ConfigListScreen.__init__(self, cfglist, session=session)

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "green":  self.save,
                "red":    self.cancel,
                "yellow": self.chooseBouquet,
                "cancel": self.cancel,
            }, -1
        )

    def chooseBouquet(self):
        self.session.openWithCallback(self._bouquetChosen, BouquetSelectScreen)

    def _bouquetChosen(self, result=None):
        bouquet_name = config.plugins.recentstarts.bouquet_name.value
        if bouquet_name in ("(none)", "(ninguno)", ""):
            bouquet_name = _("(none)")
        self["bouquet_label"].setText(_("Bouquets: ") + bouquet_name)

    def save(self):
        for entry in self["config"].list:
            entry[1].save()
        writeKeymap()
        try:
            from keymapparser import readKeymap, removeKeymap
            keymap_path = path.join(path.dirname(__file__), "keymap.xml")
            removeKeymap(keymap_path)
            readKeymap(keymap_path)
        except Exception as e:
            print("[RecentEventsGo] readKeymap error:", e)
        self.close(True)
        
    def cancel(self):
        for entry in self["config"].list:
            entry[1].cancel()
        self.close(False)

# ─── Lista multicontent con picons ───────────────────────────────────────────
class RecentStartsList(MenuList):
    def __init__(self, lst, enableWrapAround=True):
        MenuList.__init__(self, lst, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", 28))
        self.l.setFont(1, gFont("Regular", 24))
        self.l.setFont(2, gFont("Regular", 30))
        self.l.setItemHeight(75)


# ─── Columna header ────────────────────────────────────────────────────────────
class ColHeaderList(MenuList):
    def __init__(self):
        MenuList.__init__(self, [], False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", 22))
        self.l.setItemHeight(38)
        BG = 0x000000
        row = [
            "header",
            MultiContentEntryText(pos=(0,0), size=(1700,38), font=0,
                flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER, text="", backcolor=BG),
            MultiContentEntryText(pos=(10,0), size=(310,38), font=0,
                flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
                text=_("CHANNEL"), color=0x00FFFF, backcolor=BG),
            MultiContentEntryText(pos=(450,0), size=(520,38), font=0,
                flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
                text=_("PROGRAM"), color=0x00FFFF, backcolor=BG),
            MultiContentEntryText(pos=(1125,0), size=(280,38), font=0,
                flags=RT_HALIGN_RIGHT|RT_VALIGN_CENTER,
                text=_("START"), color=0x00FFFF, backcolor=BG),
            MultiContentEntryText(pos=(1290,0), size=(400,38), font=0,
                flags=RT_HALIGN_RIGHT|RT_VALIGN_CENTER,
                text=_("DURATION"), color=0x00FFFF, backcolor=BG),
        ]
        self.l.setList([row])


# ─── Builders de filas ────────────────────────────────────────────────────────
def _entryHeader(bouquet_name, count=0):
    ACC = 0xFFEF97
    MID = 0xAA9F60
    res = [bouquet_name]
    res.append(MultiContentEntryText(
        pos=(0,0), size=(1300,75), font=2,
        flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
        text=u"\u2590  " + bouquet_name.upper(), color=ACC
    ))
    if count > 0:
        res.append(MultiContentEntryText(
            pos=(1300,0), size=(395,75), font=1,
            flags=RT_HALIGN_RIGHT|RT_VALIGN_CENTER,
            text=_("%d channel(s)") % count, color=MID
        ))
    return res

def _entryChannel(ch_name, ev_name, started_str, dur_str, sref, elapsed_secs=0, duration_secs=0):
    res = [ch_name]
    try:
        pngname = getPiconName(sref.toString())
        if not pngname:
            pngname = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
        png = LoadPixmap(pngname)
        if png:
            res.append(MultiContentEntryPixmapAlphaBlend(
                pos=(2,5), size=(110,67),
                png=png, flags=BT_SCALE|BT_KEEP_ASPECT_RATIO
            ))
    except Exception:
        pass
    res.append(MultiContentEntryText(
        pos=(115,17), size=(320,38), font=2,
        flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
        text=ch_name, color=0x00BFFF
    ))
    res.append(MultiContentEntryText(
        pos=(450,19), size=(880,38), font=0,
        flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
        text=ev_name, color=0xCCCCCC
    ))
    res.append(MultiContentEntryText(
        pos=(1340,19), size=(200,38), font=1,
        flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
        text=started_str, color=0xFFEF97
    ))
    bar_x, bar_y, bar_w = 1340, 56, 350
    ratio     = min(elapsed_secs / float(duration_secs), 1.0) if duration_secs > 0 else 0
    fill_w    = int(bar_w * ratio)
    remaining = max((duration_secs - elapsed_secs) // 60, 0)
    res.append(MultiContentEntryText(
        pos=(bar_x, bar_y), size=(bar_w, 10), font=1,
        flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
        text="", backcolor=0x333333, backcolor_sel=0x333333
    ))
    if fill_w > 0:
        res.append(MultiContentEntryText(
            pos=(bar_x, bar_y), size=(fill_w, 10), font=1,
            flags=RT_HALIGN_LEFT|RT_VALIGN_CENTER,
            text="", backcolor=0x00BFFF, backcolor_sel=0x00BFFF
        ))
    res.append(MultiContentEntryText(
        pos=(bar_x, 20), size=(bar_w, 36), font=1,
        flags=RT_HALIGN_RIGHT|RT_VALIGN_CENTER,
        text=u"+%d min" % remaining,
        color=0x666666, color_sel=0xFFFFFF
    ))
    return res


# ─── Pantalla de resultados ───────────────────────────────────────────────────
class RecentStartsScreen(Screen):

    def __init__(self, session, grouped_entries):
        Screen.__init__(self, session)
        self.setTitle(_("Recently Started Broadcasts"))
        self["header"] = Label(
            _("Last %d min  —  %s") % (
                config.plugins.recentstarts.minutes_threshold.value,
                config.plugins.recentstarts.bouquet_name.value,
            )
        )
        self["col_header"] = ColHeaderList()
        self["list"]       = RecentStartsList([])
        self["status"]     = Label("")
        self["actions"] = ActionMap(
        ["OkCancelActions", "DirectionActions", "InfobarActions", "InfobarEPGActions"],
            {
                "cancel":          self.close,
                "ok":              self.zapToSelected,
                "up":              self._navUp,
                "down":            self._navDown,
                "left":            self._navPageUp,
                "right":           self._navPageDown,
                "InfoPressed": self._showEventInfo,
            }, -1
        )
        self._srefs   = []
        self._grouped = grouped_entries
        self.onLayoutFinish.append(self._populate)

    def _populate(self):
        items = []
        self._srefs = []
        total = 0
        for bouquet_name, entries in self._grouped:
            items.append(_entryHeader(bouquet_name, count=len(entries)))
            self._srefs.append(None)
            for ch_name, ev_name, started_str, duration_str, sref, elapsed_secs, duration_secs in entries:
                items.append(_entryChannel(ch_name, ev_name, started_str, duration_str,
                                           sref, elapsed_secs, duration_secs))
                self._srefs.append(sref)
                total += 1
        if not items:
            self["status"].setText(_("No recent broadcasts"))
            return
        self["list"].setList(items)
        self["status"].setText(
            _("Total %d channel(s)  ·  OK = tune  ·  INFO = EPG") % total
        )
        for i, sref in enumerate(self._srefs):
            if sref is not None:
                self["list"].moveToIndex(i)
                break

    def zapToSelected(self):
        idx = self["list"].getSelectionIndex()
        if idx < 0 or idx >= len(self._srefs):
            return
        sref = self._srefs[idx]
        if sref is None:
            return
        self.close(sref.toString())  # <-- string, no objeto

    def _navDown(self):
        self["list"].down()
        idx = self["list"].getSelectionIndex()
        if idx < len(self._srefs) and self._srefs[idx] is None:
            self["list"].down()

    def _navUp(self):
        self["list"].up()
        idx = self["list"].getSelectionIndex()
        if idx < len(self._srefs) and self._srefs[idx] is None:
            self["list"].up()

    def _navPageDown(self):
        self["list"].pageDown()
        idx = self["list"].getSelectionIndex()
        if idx < len(self._srefs) and self._srefs[idx] is None:
            self["list"].down()

    def _navPageUp(self):
        self["list"].pageUp()
        idx = self["list"].getSelectionIndex()
        if idx < len(self._srefs) and self._srefs[idx] is None:
            self["list"].down()

    def _showEventInfo(self):
        from Screens.EventView import EventViewEPGSelect
        from ServiceReference import ServiceReference
        idx = self["list"].getSelectionIndex()
        if idx < 0 or idx >= len(self._srefs):
            return
        sref = self._srefs[idx]
        if sref is None:
            return
        epgcache = eEPGCache.getInstance()
        event = epgcache.lookupEventTime(sref, int(time.time()))
        if event is None:
            return
        self.session.open(EventViewEPGSelect, event, ServiceReference(sref))

# ─── Lógica EPG ───────────────────────────────────────────────────────────────
def getServicesInBouquet(bouquet_ref_str):
    services = []
    if not bouquet_ref_str:
        return services
    serviceHandler = eServiceCenter.getInstance()
    ref = eServiceReference(bouquet_ref_str)
    serviceList = serviceHandler.list(ref)
    if serviceList is None:
        return services
    while True:
        sref = serviceList.getNext()
        if not sref or sref.valid() == 0:
            break
        if sref.flags & eServiceReference.isDirectory:
            continue
        services.append(sref)
    return services


def getRecentlyStarted(bouquet_refs_str, threshold_minutes=10):
    now            = int(time.time())
    threshold_secs = threshold_minutes * 60
    epgcache       = eEPGCache.getInstance()
    serviceHandler = eServiceCenter.getInstance()
    grouped        = []

    for bouquet_ref_str in bouquet_refs_str.split("|"):
        bouquet_ref_str = bouquet_ref_str.strip()
        if not bouquet_ref_str:
            continue
        bref  = eServiceReference(bouquet_ref_str)
        binfo = serviceHandler.info(bref)
        bouquet_name = binfo.getName(bref) if binfo else bouquet_ref_str

        seen    = set()
        entries = []

        for sref in getServicesInBouquet(bouquet_ref_str):
            event = epgcache.lookupEventTime(sref, now)
            if event is None:
                continue
            begin   = event.getBeginTime()
            elapsed = now - begin
            if not (0 <= elapsed <= threshold_secs):
                continue
            info    = serviceHandler.info(sref)
            ch_name = info.getName(sref) if info else sref.toString()
            if ch_name in seen:
                continue
            seen.add(ch_name)

            ev_name       = event.getEventName() or _("(no title)")
            mins_ago      = elapsed // 60
            started_str   = _("%d min ago") % mins_ago if mins_ago > 0 else _("now")
            duration_secs = event.getDuration()
            duration_min  = duration_secs // 60

            entries.append((ch_name, ev_name, started_str,
                            "%d min" % duration_min, sref, elapsed, duration_secs))

        if entries:
            entries.sort(key=lambda x: x[5])
            entries = [(ch, ev, st, dur, sref, el, ds)
                       for ch, ev, st, dur, sref, el, ds in entries]
            grouped.append((bouquet_name, entries))

    return grouped


# ─── Funcion de zapeo reutilizable ────────────────────────────────────────────────────
def doZap(session, sref_str=None):
    if not sref_str:
        return
    try:
        sref = eServiceReference(sref_str)
        from Screens.InfoBar import InfoBar
        ib = InfoBar.instance
        sl = ib.servicelist

        # setCurrentSelection + zap() SIEMPRE -> guarda en historial
        sl.setCurrentSelection(sref)
        sl.zap()

        # Para IPTV (tipo != 1) zap() solo no arranca el stream -> forzamos playService ademas
        if sref.type != 1:
            ib.session.nav.playService(sref)

        print("[RecentEventsGo] zap OK:", sref_str)
    except Exception as e:
        print("[RecentEventsGo] doZap error:", e)


# ─── Extensión del InfoBar ────────────────────────────────────────────────────
class InfoBarRecentStartsExtension:
    def __init__(self):
        self["RecentEventsGoActions"] = HelpableActionMap(
            self,
            "InfobarRecentStartsActions",
            {"showRecentStarts": (self.showRecentStarts, _("Recently started broadcasts"))},
            prio=-1
        )

    def showRecentStarts(self):
        refs = config.plugins.recentstarts.bouquet_refs.value
        if not refs:
            self.session.open(
                MessageBox,
                _("Please configure bouquets first in Menu > Plugins > RecentEventsGo."),
                MessageBox.TYPE_INFO,
                timeout=5
            )
            return
        threshold = config.plugins.recentstarts.minutes_threshold.value
        grouped   = getRecentlyStarted(refs, threshold)
        self.session.openWithCallback(self._doZap, RecentStartsScreen, grouped)

    def _doZap(self, sref_str=None):
        doZap(self.session, sref_str)

def writeKeymap():
    key = config.plugins.recentstarts.hotkey.value
    keymap_path = path.join(path.dirname(__file__), "keymap.xml")
    content = """<?xml version="1.0" encoding="UTF-8"?>
    <keymap>
        <map context="InfobarActions">
            <key id="KEY_%s" mapto="showRecentStarts" flags="m" />
        </map>
        <map context="InfobarRecentStartsActions">
            <key id="KEY_%s" mapto="showRecentStarts" flags="m" />
        </map>
    </keymap>""" % (key.upper(), key.upper())
    try:
        with open(keymap_path, "w") as f:
            f.write(content)
    except Exception as e:
        print("[RecentEventsGo] writeKeymap error:", e)


# ─── Autostart ───────────────────────────────────────────────────────────────
def autostart(reason, **kwargs):
    if reason == 0:
        try:
            from keymapparser import readKeymap, removeKeymap
            keymap_path = path.join(path.dirname(__file__), "keymap.xml")
            writeKeymap()
            removeKeymap(keymap_path)
            readKeymap(keymap_path)
        except Exception as e:
            print("[RecentEventsGo] keymap error:", e)
        try:
            from Screens.InfoBar import InfoBar
            if not hasattr(InfoBar, "_recenteventsgo_patched"):
                InfoBar.__bases__ = (InfoBarRecentStartsExtension,) + InfoBar.__bases__
                original_init = InfoBar.__init__
                def patched_init(self_ib, *args, **kw):
                    original_init(self_ib, *args, **kw)
                    InfoBarRecentStartsExtension.__init__(self_ib)
                InfoBar.__init__ = patched_init
                InfoBar._recenteventsgo_patched = True
        except Exception as e:
            print("[RecentEventsGo] autostart error:", e)


# ─── Registro ────────────────────────────────────────────────────────────────
def Plugins(**kwargs):
    icon = path.join(path.dirname(__file__), "icon.png")
    return [
        PluginDescriptor(
            name=_("RecentEventsGo"),
            description=_("Recently started broadcasts from configured bouquets"),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon=icon,
            fnc=lambda session, **kwargs: session.open(RecentStartsConfig)
        ),
        PluginDescriptor(
            name=_("RecentEventsGo"),
            description=_("Recently started broadcasts"),
            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
            icon=icon,
            fnc=lambda session, **kwargs: session.openWithCallback(
                lambda sref_str=None: doZap(session, sref_str),
                RecentStartsScreen,
                getRecentlyStarted(config.plugins.recentstarts.bouquet_refs.value,
                                    config.plugins.recentstarts.minutes_threshold.value)
            )
        ),
        PluginDescriptor(
            name=_("RecentEventsGo - Configuration"),
            description=_("Configure RecentEventsGo"),
            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
            icon=icon,
            fnc=lambda session, **kwargs: session.open(RecentStartsConfig)
        ),
        PluginDescriptor(
            name="RecentEventsGo Autostart",
            where=PluginDescriptor.WHERE_AUTOSTART,
            fnc=autostart
        ),
    ]
