# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#  ChannelFinder  v1.5
#  Plugin para Enigma2 / OpenSPA
# ───────────────────────────────────────────────────────────────────
#  Autor  :  VillaK
#  Para   :  OpenSPA
# ───────────────────────────────────────────────────────────────────
#  Búsqueda de canales por nombre entre bouquets seleccionados.
#  Búsqueda de eventos en la guía EPG con soporte de timers de zapeo
#  automático: programa a qué canal saltar a la hora exacta del
#  evento, sin grabación, usando el motor nativo de Enigma2.
# ───────────────────────────────────────────────────────────────────
#  Instalación:
#    /usr/lib/enigma2/python/Plugins/Extensions/ChannelFinder/
# ═══════════════════════════════════════════════════════════════════

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ProgressBar import ProgressBar
from Components.Language import language
from enigma import eServiceReference, eServiceCenter, eEPGCache, eTimer
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import path
import re
import os
import json
import time
import datetime
import gettext

PLUGIN_NAME     = "ChannelFinder"
PLUGIN_DESC     = "Search channels and EPG events"
PLUGIN_VERSION  = "1.5"
PLUGIN_PATH     = resolveFilename(SCOPE_PLUGINS, "Extensions/ChannelFinder/")
CONFIG_FILE     = "/etc/enigma2/channelfinder_bouquets.json"
ZAP_TIMERS_FILE = "/etc/enigma2/channelfinder_zaptimers.json"


# ──────────────────────────────────────────────
#  Internacionalización
# ──────────────────────────────────────────────

def localeInit():
    global _, n_
    try:
        lang = gettext.translation(
            'ChannelFinder',
            os.path.join(PLUGIN_PATH, 'locale'),
            languages=[language.getLanguage()],
            fallback=True
        )
        _ = lang.gettext
        n_ = lang.ngettext  # <-- Añadimos esto
    except Exception as e:
        print("[ChannelFinder] locale error:", e)
        _ = lambda x: x
        # Un fallback simple por si falla la carga del idioma
        n_ = lambda s, p, n: s if n == 1 else p

localeInit()
language.addCallback(localeInit)


# ──────────────────────────────────────────────
#  Persistencia – Bouquets
# ──────────────────────────────────────────────

def loadSavedBouquetNames():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return set(json.load(f).get("bouquets", []))
    except Exception as e:
        print("[ChannelFinder] Error loading config:", e)
    return set()


def saveBouquetNames(names):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"bouquets": list(names)}, f)
    except Exception as e:
        print("[ChannelFinder] Error saving config:", e)


# ──────────────────────────────────────────────
#  Persistencia – Zap Timers propios
# ──────────────────────────────────────────────

def loadZapTimers():
    try:
        if os.path.exists(ZAP_TIMERS_FILE):
            with open(ZAP_TIMERS_FILE, "r") as f:
                return json.load(f).get("timers", [])
    except Exception as e:
        print("[ChannelFinder] Error loading zaptimers:", e)
    return []


def saveZapTimers(timers):
    try:
        with open(ZAP_TIMERS_FILE, "w") as f:
            json.dump({"timers": timers}, f, indent=2)
    except Exception as e:
        print("[ChannelFinder] Error saving zaptimers:", e)


def addZapTimer(title, chRefStr, chName, chBouquet, evStart, evDur):
    """Add timer. Returns True if added, False if already exists."""
    now    = int(time.time())
    timers = [t for t in loadZapTimers() if t["evStart"] + t["evDur"] > now]
    for t in timers:
        if t["chRefStr"] == chRefStr and t["evStart"] == evStart:
            saveZapTimers(timers)
            return False
    timers.append({
        "title":     title,
        "chRefStr":  chRefStr,
        "chName":    chName,
        "chBouquet": chBouquet,
        "evStart":   evStart,
        "evDur":     evDur,
        "added":     now,
    })
    saveZapTimers(timers)
    return True


def removeZapTimer(chRefStr, evStart):
    timers = [t for t in loadZapTimers()
              if not (t["chRefStr"] == chRefStr and t["evStart"] == evStart)]
    saveZapTimers(timers)


def hasZapTimer(chRefStr, evStart):
    return any(t["chRefStr"] == chRefStr and t["evStart"] == evStart
               for t in loadZapTimers())


# ──────────────────────────────────────────────
#  Daemon de zap – dispara a la hora exacta
# ──────────────────────────────────────────────

class ZapTimerDaemon:
    """
    Singleton. Created on autostart with the Enigma2 session.
    Calculates time until next timer and schedules an eTimer
    for that exact time, just like the native RecordTimer.
    No polling: sleeps until it fires.
    """
    _instance = None

    @classmethod
    def start(cls, session):
        if cls._instance is None:
            cls._instance = ZapTimerDaemon(session)
            print("[ChannelFinder] ZapTimerDaemon started")

    @classmethod
    def reschedule(cls):
        """Call after adding or removing a timer."""
        if cls._instance:
            cls._instance._schedule()

    def __init__(self, session):
        self._session = session
        self._eTimer  = eTimer()
        self._eTimer.callback.append(self._onFire)
        self._schedule()

    def _schedule(self):
        """Schedule eTimer for the next pending timer."""
        self._eTimer.stop()
        now    = int(time.time())
        timers = [t for t in loadZapTimers() if t["evStart"] > now]
        if not timers:
            return
        nxt   = min(timers, key=lambda t: t["evStart"])
        delta = max(0, nxt["evStart"] - now)
        self._eTimer.start(delta * 1000, True)   # single-shot, milliseconds
        print("[ChannelFinder] Next zap in %ds -> %s" % (delta, nxt["title"]))

    def _onFire(self):
        now    = int(time.time())
        timers = loadZapTimers()
        fired  = []

        for t in timers:
            # ±90s window to cover clock drift or standby
            if abs(t["evStart"] - now) <= 90 and t["evStart"] + t["evDur"] > now:
                try:
                    self._session.nav.playService(eServiceReference(t["chRefStr"]))
                    fired.append((t["chRefStr"], t["evStart"]))
                    print("[ChannelFinder] Zap executed: %s" % t["title"])
                except Exception as e:
                    print("[ChannelFinder] Error zapping:", e)

        if fired:
            timers = [t for t in timers
                      if (t["chRefStr"], t["evStart"]) not in fired]
            saveZapTimers(timers)

        self._schedule()


# ──────────────────────────────────────────────
#  Bouquets / servicios
# ──────────────────────────────────────────────

def getAllBouquets():
    bouquets = []
    try:
        serviceHandler = eServiceCenter.getInstance()
        rootRef = eServiceReference(
            '1:7:1:0:0:0:0:0:0:0:(type == 1) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        )
        sl = serviceHandler.list(rootRef)
        if sl:
            while True:
                ref = sl.getNext()
                if not ref.valid():
                    break
                info = serviceHandler.info(ref)
                if info:
                    name = info.getName(ref).strip()
                    if name:
                        bouquets.append((name, ref.toString()))
    except Exception as e:
        print("[ChannelFinder] Error reading bouquets:", e)
    return bouquets


def getServicesFromBouquet(bouquetRefStr):
    services = []
    try:
        serviceHandler = eServiceCenter.getInstance()
        ref = eServiceReference(bouquetRefStr)
        sl  = serviceHandler.list(ref)
        if sl:
            while True:
                sRef = sl.getNext()
                if not sRef.valid():
                    break
                if sRef.flags & eServiceReference.isMarker:
                    continue
                info = serviceHandler.info(sRef)
                if info:
                    name = info.getName(sRef).strip()
                    if name:
                        services.append((name, sRef.toString()))
    except Exception as e:
        print("[ChannelFinder] \u2716 Error reading services:", e)
    return services


def normRef(refStr):
    try:
        parts = refStr.strip().split(":")
        return ":".join(parts[2:6]).lower()
    except Exception:
        return refStr.lower()


# ──────────────────────────────────────────────
#  Búsqueda canales
# ──────────────────────────────────────────────

def searchChannels(query, selectedBouquetRefs):
    results = []
    pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
    for (bouquetName, bouquetRef) in selectedBouquetRefs:
        for (chName, chRef) in getServicesFromBouquet(bouquetRef):
            if pattern.search(chName):
                results.append((chName, bouquetName, chRef))
    return results


# ──────────────────────────────────────────────
#  Búsqueda EPG
# ──────────────────────────────────────────────

def formatEventTime(evStart):
    now  = datetime.date.today()
    evDt = datetime.date.fromtimestamp(evStart)
    loc  = time.localtime(evStart)
    hhmm = "%02d:%02d" % (loc.tm_hour, loc.tm_min)
    if evDt == now:
        return _("Today %s") % hhmm
    if evDt == now + datetime.timedelta(days=1):
        return _("Tomorrow %s") % hhmm
    return "%02d/%02d %s" % (loc.tm_mday, loc.tm_mon, hhmm)


def searchEPG(query, selectedBouquetRefs):
    epgCache = eEPGCache.getInstance()
    now      = int(time.time())

    refMap = {}
    for (bouquetName, bouquetRef) in selectedBouquetRefs:
        for (chName, chRefStr) in getServicesFromBouquet(bouquetRef):
            key = normRef(chRefStr)
            refMap.setdefault(key, []).append((chName, bouquetName, chRefStr))

    if not refMap:
        return []

    try:
        rawEvents = epgCache.search((
            'RIBDTW', 2000,
            eEPGCache.PARTIAL_TITLE_SEARCH,
            query,
            eEPGCache.NO_CASE_CHECK
        )) or []
    except Exception as e:
        print("[ChannelFinder] Error epgCache.search:", e)
        rawEvents = []

    results = []
    seen    = set()

    for ev in rawEvents:
        try:
            evRefStr = ev[0]
            evStart  = ev[2]
            evDur    = ev[3]
            evTitle  = ev[4]
            if not evTitle or not evStart:
                continue
            if evStart + evDur < now:
                continue
            key = normRef(evRefStr)
            if key not in refMap:
                continue
            dateStr = formatEventTime(evStart)
            for (chName, bouquetName, origRef) in refMap[key]:
                seenKey = (key, evStart, bouquetName)
                if seenKey in seen:
                    continue
                seen.add(seenKey)
                results.append((evTitle, chName, bouquetName, dateStr, evStart, evDur, origRef))
        except Exception:
            continue

    results.sort(key=lambda x: x[4])
    return results


def getCurrentEvent(chRefStr):
    try:
        epgCache = eEPGCache.getInstance()
        events = epgCache.lookupEvent(['IBDTN', (chRefStr, 0, -1)])
        if events:
            ev = events[0]
            return (ev[3], ev[1], ev[2])
    except Exception:
        pass
    return None


# ──────────────────────────────────────────────
#  Pantalla: lista de timers propios
# ──────────────────────────────────────────────

class ZapTimerListScreen(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self["key_red"]   = Label(_("Delete"))
        self["key_green"] = Label(_("Close"))
        self["info"]      = Label("")
        self["list"]      = MenuList([], enableWrapAround=True)

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok":     self._delete,
                "red":    self._delete,
                "cancel": self._close,
                "green":  self._close,
            }, -1)

        self.onShown.append(self._onShown)

    def _onShown(self):
        self.setTitle(_("ChannelFinder – My zap timers"))
        self._buildList()

    def _buildList(self):
        now    = int(time.time())
        timers = sorted(
            [t for t in loadZapTimers() if t["evStart"] + t["evDur"] > now],
            key=lambda t: t["evStart"]
        )
        self._timers = timers

        if not timers:
            self["info"].setText(_("No timers scheduled"))
            self["list"].setList([u"\u26a0  " + _("(empty list)")])
            return

        self["info"].setText(n_("%d timer scheduled", "%d timers scheduled", len(timers)) % len(timers))
        items = []
        for t in timers:
            startStr = "%02d:%02d" % time.localtime(t["evStart"])[3:5]
            endStr   = "%02d:%02d" % time.localtime(t["evStart"] + t["evDur"])[3:5]
            dateStr  = formatEventTime(t["evStart"])
            items.append(u"\u231b %s  %s\u2013%s  |  %s [%s]  |  %s" % (
                dateStr, startStr, endStr, t["chName"], t["chBouquet"], t["title"]))
        self["list"].setList(items)

    def _delete(self):
        idx = self["list"].getSelectedIndex()
        if not hasattr(self, "_timers") or not (0 <= idx < len(self._timers)):
            return
        t = self._timers[idx]
        startStr = "%02d:%02d" % time.localtime(t["evStart"])[3:5]
        self.session.openWithCallback(
            lambda confirmed: self._confirmDelete(confirmed, t),
            MessageBox,
            u'\ue001 ' + _('Delete timer?\n"%s"  at %s') % (t["title"], startStr),
            MessageBox.TYPE_YESNO,
        )

    def _confirmDelete(self, confirmed, t):
        if not confirmed:
            return
        removeZapTimer(t["chRefStr"], t["evStart"])
        ZapTimerDaemon.reschedule()
        self._buildList()

    def _close(self):
        self.close()


# ──────────────────────────────────────────────
#  Selección de Bouquets
# ──────────────────────────────────────────────

class BouquetSelectionScreen(Screen):

    def __init__(self, session, bouquets, preSelected=None):
        Screen.__init__(self, session)
        self.bouquets = bouquets
        self.selected = {i: (bouquets[i][0] in (preSelected or set()))
                         for i in range(len(bouquets))}

        self["key_red"]   = Label(_("Cancel"))
        self["key_green"] = Label(_("Save"))
        self["key_blue"]  = Label(_("All / None"))
        self["list"]      = MenuList([], enableWrapAround=True)
        self._buildList()

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok":     self._toggle,
                "cancel": self._cancel,
                "red":    self._cancel,
                "green":  self._confirm,
                "blue":   self._toggleAll,
            }, -1)
        self.onShown.append(lambda: self.setTitle(_("ChannelFinder – Bouquets")))

    def _buildList(self):
        self["list"].setList([
            ("✔  " if self.selected.get(i) else "     ") + name
            for i, (name, _) in enumerate(self.bouquets)
        ])

    def _toggle(self):
        idx = self["list"].getSelectedIndex()
        self.selected[idx] = not self.selected.get(idx, False)
        self._buildList()
        self["list"].moveToIndex(idx)

    def _toggleAll(self):
        anySelected = any(self.selected.values())
        for i in range(len(self.bouquets)):
            self.selected[i] = not anySelected
        self._buildList()

    def _cancel(self):
        self.close(None)

    def _confirm(self):
        chosen = [(self.bouquets[i][0], self.bouquets[i][1])
                  for i in range(len(self.bouquets)) if self.selected.get(i)]
        if not chosen:
            self.session.open(MessageBox, _("⚠ Select at least one bouquet."),
                              MessageBox.TYPE_INFO, timeout=3)
            return
        saveBouquetNames(set(n for (n, _) in chosen))
        self.close(chosen)


# ──────────────────────────────────────────────
#  Resultados – Canales
# ──────────────────────────────────────────────

class ChannelResultsScreen(Screen):

    def __init__(self, session, results,  query=""):
        Screen.__init__(self, session)
        self.results = results
        count = len(results)

        self["info"] = Label(_("Search Channel: %s") % query)
        self["key_red"]   = Label(_("Close"))
        self["lab_now"]   = Label("")
        self["now_title"] = Label("")
        self["now_times"] = Label("")
        self["progress"]  = ProgressBar()
        self["list"]      = MenuList([], enableWrapAround=True)

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok":     self._zap,
                "cancel": self._close,
                "red":    self._close,
                "up":     self._up,
                "down":   self._down,
                "left":   self._pageUp,
                "right":  self._pageDown,
            }, -1)

        self._refreshTimer = eTimer()
        self._refreshTimer.callback.append(self._refresh)

        self.onShown.append(self._onShown)
        self.onClose.append(self._onClose)

    def _onShown(self):
        count = len(self.results)
        self.setTitle(n_("ChannelFinder – %d channel", "ChannelFinder – %d channels", count) % count)
        self._buildList()
        self._updateNowInfo()
        self._refreshTimer.start(30000, False)

    def _onClose(self):
        self._refreshTimer.stop()

    def _refresh(self):
        idx = self["list"].getSelectedIndex()
        self._buildList()
        self["list"].moveToIndex(idx)
        self._updateNowInfo()

    def _buildList(self):
        items = []
        for (ch, bq, chRefStr) in self.results:
            ev = getCurrentEvent(chRefStr)
            if ev:
                curTitle, curStart, curDur = ev
                startStr = "%02d:%02d" % time.localtime(curStart)[3:5]
                endStr   = "%02d:%02d" % time.localtime(curStart + curDur)[3:5]
                items.append(u"\ue002  %s  |  %s     \u23f5 %s\u2013%s  %s" % (
                    ch, bq, startStr, endStr, curTitle))
            else:
                items.append(u"\ue002  %s  |  %s     %s" % (ch, bq, _("no EPG")))
        self["list"].setList(items)

    def _up(self):
        self["list"].up()
        self._updateNowInfo()

    def _down(self):
        self["list"].down()
        self._updateNowInfo()

    def _pageUp(self):
        self["list"].pageUp()
        self._updateNowInfo()

    def _pageDown(self):
        self["list"].pageDown()
        self._updateNowInfo()

    def _updateNowInfo(self):
        idx = self["list"].getSelectedIndex()
        if not (0 <= idx < len(self.results)):
            return
        _ch, _bq, chRefStr = self.results[idx]
        now = int(time.time())
        ev  = getCurrentEvent(chRefStr)
        if ev:
            curTitle, curStart, curDur = ev
            curRemMin = max(0, (curStart + curDur - now) // 60)
            curEnd    = "%02d:%02d" % time.localtime(curStart + curDur)[3:5]
            curStart2 = "%02d:%02d" % time.localtime(curStart)[3:5]
            pct       = max(0, min(100, int((now - curStart) * 100 / curDur))) if curDur else 0
            self["lab_now"].setText(u"\u25b6  " + _("Now playing..."))
            self["now_title"].setText(curTitle)
            self["now_times"].setText(_("%s \u2013 %s  (%d min remaining)") % (
                curStart2, curEnd, curRemMin))
            self["progress"].setValue(pct)
        else:
            self["lab_now"].setText(_("No EPG information"))
            self["now_title"].setText("")
            self["now_times"].setText("")
            self["progress"].setValue(0)

    def _zap(self):
        idx = self["list"].getSelectedIndex()
        if 0 <= idx < len(self.results):
            _, _, chRefStr = self.results[idx]
            try:
                self.session.nav.playService(eServiceReference(chRefStr))
                self._close()
            except Exception as e:
                self.session.open(MessageBox,
                                  _("Could not tune to channel:\n%s") % str(e),
                                  MessageBox.TYPE_ERROR, timeout=4)

    def _close(self):
        self.close()


# ──────────────────────────────────────────────
#  Resultados – EPG
# ──────────────────────────────────────────────

class EPGResultsScreen(Screen):
    """
    List icons:
      ▶   on air now       -> OK zaps directly
      ⏱   has zap timer    -> OK offers to cancel
          (no icon)        -> OK offers to add timer

    Bottom panel: current programme + progress bar.
    """

    def __init__(self, session, results, query=""):
        Screen.__init__(self, session)
        self.results = results
        count = len(results)

        self["info"] = Label(_("Search EPG: %s") % query)
        self["key_red"]   = Label(_("Close"))
        self["key_ok"]    = Label(_("Watch / Timer"))
        self["lab_now"]   = Label("")
        self["now_title"] = Label("")
        self["now_times"] = Label("")
        self["progress"]  = ProgressBar()
        self["list"]      = MenuList([], enableWrapAround=True)

        self._buildList()

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok":     self._ok,
                "cancel": self._close,
                "red":    self._close,
                "up":     self._up,
                "down":   self._down,
                "left":   self._pageUp,
                "right":  self._pageDown,
            }, -1)

        self._refreshTimer = eTimer()
        self._refreshTimer.callback.append(self._updateNowInfo)

        self.onShown.append(self._onShown)
        self.onClose.append(self._onClose)

    # ── list ──

    def _buildList(self):
        now   = int(time.time())
        items = []
        for (title, ch, bq, dateStr, evStart, evDur, chRefStr) in self.results:
            if evStart <= now <= evStart + evDur:
                icon = "⏵  "
            elif hasZapTimer(chRefStr, evStart):
                icon = u"\u23f1  "
            else:
                icon = "    "
            items.append("%s%s  |  %s [%s]  |  %s" % (icon, dateStr, ch, bq, title))
        self["list"].setList(items)

    def _rebuildItem(self):
        idx = self["list"].getSelectedIndex()
        self._buildList()
        self["list"].moveToIndex(idx)

    # ── lifecycle ──

    def _onShown(self):
        count = len(self.results)
        self.setTitle(n_("ChannelFinder – %d event in EPG", "ChannelFinder – %d events in EPG", count) % count)
        self._updateNowInfo()
        self._refreshTimer.start(30000, False)

    def _onClose(self):
        self._refreshTimer.stop()

    # ── navigation ──

    def _up(self):
        self["list"].up()
        self._updateNowInfo()

    def _down(self):
        self["list"].down()
        self._updateNowInfo()

    def _pageUp(self):
        self["list"].pageUp()
        self._updateNowInfo()

    def _pageDown(self):
        self["list"].pageDown()
        self._updateNowInfo()

    # ── bottom panel ──

    def _updateNowInfo(self):
        idx = self["list"].getSelectedIndex()
        if not (0 <= idx < len(self.results)):
            return
        title, ch, bq, dateStr, evStart, evDur, chRefStr = self.results[idx]
        now = int(time.time())

        if evStart <= now <= evStart + evDur:
            elapsed  = now - evStart
            pct      = max(0, min(100, int(elapsed * 100 / evDur))) if evDur else 0
            remMin   = max(0, (evDur - elapsed) // 60)
            startStr = "%02d:%02d" % time.localtime(evStart)[3:5]
            endStr   = "%02d:%02d" % time.localtime(evStart + evDur)[3:5]
            self["lab_now"].setText(_("▶  NOW ON %s...") % ch)
            self["now_title"].setText(title)
            self["now_times"].setText(_("%s – %s  (%d min remaining)") % (startStr, endStr, remMin))
            self["progress"].setValue(pct)
        else:
            minUntil = max(0, (evStart - now) // 60)
            startStr = "%02d:%02d" % time.localtime(evStart)[3:5]
            endStr   = "%02d:%02d" % time.localtime(evStart + evDur)[3:5]
            falta    = ("%dh %02dmin" % (minUntil // 60, minUntil % 60)
                        if minUntil >= 60 else "%d min" % minUntil)
            ev = getCurrentEvent(chRefStr)
            if ev:
                curTitle, curStart, curDur = ev
                curRemMin = max(0, (curStart + curDur - now) // 60)
                curEnd    = "%02d:%02d" % time.localtime(curStart + curDur)[3:5]
                pct       = max(0, min(100, int((now - curStart) * 100 / curDur))) if curDur else 0
                self["lab_now"].setText(
                    _("Starts in %s (at %s–%s)\nNow on %s...") % (falta, startStr, endStr, ch))
                self["now_title"].setText(curTitle)
                self["now_times"].setText(_("until %s  (%d min remaining)") % (curEnd, curRemMin))
                self["progress"].setValue(pct)
            else:
                self["lab_now"].setText(
                    _("Starts in %s  (at %s – %s)") % (falta, startStr, endStr))
                self["now_title"].setText(_("No information for current programme"))
                self["now_times"].setText("")
                self["progress"].setValue(0)

    # ── OK action ──

    def _ok(self):
        idx = self["list"].getSelectedIndex()
        if not (0 <= idx < len(self.results)):
            return
        title, ch, bq, dateStr, evStart, evDur, chRefStr = self.results[idx]
        now = int(time.time())

        if evStart <= now <= evStart + evDur:
            try:
                self.session.nav.playService(eServiceReference(chRefStr))
                self._close()
            except Exception as e:
                self.session.open(MessageBox, _("⚠  Could not tune to channel:\n%s") % str(e),
                                  MessageBox.TYPE_ERROR, timeout=4)

        elif hasZapTimer(chRefStr, evStart):
            startStr = "%02d:%02d" % time.localtime(evStart)[3:5]
            self.session.openWithCallback(
                lambda c: self._doRemoveTimer(c, chRefStr, evStart, title),
                MessageBox,
                _("\u23f1  Timer already scheduled:\n\"%s\"  at %s\n\nCancel it?") % (title, startStr),
                MessageBox.TYPE_YESNO,
            )
        else:
            startStr = "%02d:%02d" % time.localtime(evStart)[3:5]
            endStr   = "%02d:%02d" % time.localtime(evStart + evDur)[3:5]
            self.session.openWithCallback(
                lambda c: self._doAddTimer(c, title, chRefStr, ch, bq, evStart, evDur),
                MessageBox,
                _("\"%s\"\nStarts at %s and ends at %s.\n\nAdd zap timer?") % (
                    title, startStr, endStr),
                MessageBox.TYPE_YESNO,
            )

    def _doAddTimer(self, confirmed, title, chRefStr, chName, chBouquet, evStart, evDur):
        if not confirmed:
            return
        startStr = "%02d:%02d" % time.localtime(evStart)[3:5]
        added = addZapTimer(title, chRefStr, chName, chBouquet, evStart, evDur)
        if added:
            ZapTimerDaemon.reschedule()
            msg = _("✔  Timer saved:\n\"%s\"  at %s") % (title, startStr)
        else:
            msg = _("⚠  Timer already exists for:\n\"%s\"  at %s") % (title, startStr)
        self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, timeout=4)
        self._rebuildItem()

    def _doRemoveTimer(self, confirmed, chRefStr, evStart, title):
        if not confirmed:
            return
        removeZapTimer(chRefStr, evStart)
        ZapTimerDaemon.reschedule()
        startStr = "%02d:%02d" % time.localtime(evStart)[3:5]
        self.session.open(
            MessageBox,
            _("\u23f1  Timer cancelled:\n\"%s\"  at %s") % (title, startStr),
            MessageBox.TYPE_INFO, timeout=3)
        self._rebuildItem()

    def _close(self):
        self.close()


# ──────────────────────────────────────────────
#  Pantalla base de búsqueda
# ──────────────────────────────────────────────

class BaseSearchScreen(Screen):

    def __init__(self, session, labelSearch, screenTitle):
        Screen.__init__(self, session)
        self.screenTitle  = screenTitle
        self.searchQuery  = ""
        self.bouquets     = getAllBouquets()
        savedNames        = loadSavedBouquetNames()
        self.selectedBouquets = [(n, r) for (n, r) in self.bouquets
                                 if n in savedNames] if savedNames else []

        self["lab_search"]    = Label(labelSearch)
        self["query_display"] = Label("_")
        self["lab_bouquets"]  = Label(_("Bouquets:"))
        self["bouquet_info"]  = Label("")
        self["key_red"]       = Label(_("Back"))
        self["key_green"]     = Label(_("Search"))
        self["key_yellow"]    = Label(_("Bouquets"))
        self["key_blue"]      = Label(_("Keyboard"))

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok":     self._openKeyboard,
                "cancel": self._exit,
                "red":    self._exit,
                "green":  self._search,
                "yellow": self._selectBouquets,
                "blue":   self._openKeyboard,
            }, -1)

        self._firstShow = True
        self.onShown.append(self._onShown)

    def _onShown(self):
        self.setTitle(self.screenTitle)
        self._updateBouquetInfo()
        if self._firstShow:
            self._firstShow = False
            self._openKeyboard()

    def _openKeyboard(self):
        self.session.openWithCallback(
            self._keyboardClosed,
            spzVirtualKeyboard,
            titulo=_("Enter text to search:"),
        )

    def _keyboardClosed(self, text=None):
        if text is not None:
            self.searchQuery = text
        self["query_display"].setText(self.searchQuery or "_")

    def _selectBouquets(self):
        if not self.bouquets:
            self.session.open(MessageBox, _("⚠  No TV bouquets found."),
                              MessageBox.TYPE_INFO, timeout=4)
            return
        preSelected = set(n for (n, _) in self.selectedBouquets)
        self.session.openWithCallback(
            self._bouquetsChosen, BouquetSelectionScreen,
            self.bouquets, preSelected)

    def _bouquetsChosen(self, chosen):
        if chosen is not None:
            self.selectedBouquets = chosen
        self._updateBouquetInfo()

    def _updateBouquetInfo(self):
        if self.selectedBouquets:
            self["bouquet_info"].setText(
                ", ".join(n for (n, _) in self.selectedBouquets))
        else:
            self["bouquet_info"].setText(_("(⚠  none — press Yellow to choose)"))

    def _search(self):
        query = self.searchQuery.strip()
        if not query:
            self.session.open(MessageBox,
                              _("⚠  First enter the text to search (OK or Blue)."),
                              MessageBox.TYPE_INFO, timeout=3)
            return
        if not self.selectedBouquets:
            self.session.open(MessageBox,
                              _("⚠  Choose at least one bouquet (Yellow button)."),
                              MessageBox.TYPE_INFO, timeout=3)
            return
        self._doSearch(query)

    def _doSearch(self, query):
        pass

    def _exit(self):
        self.close()


class ChannelSearchScreen(BaseSearchScreen):
    def __init__(self, session):
        BaseSearchScreen.__init__(self, session,
            labelSearch=_("Channel to search  (OK = keyboard):"),
            screenTitle=_("ChannelFinder – Search channel"))

    def _doSearch(self, query):
        results = searchChannels(query, self.selectedBouquets)
        if not results:
            self.session.open(MessageBox,
                              _('⚠  Channel "%s" not found.') % query,
                              MessageBox.TYPE_INFO, timeout=4)
        else:
            self.session.open(ChannelResultsScreen, results, query)


class EPGSearchScreen(BaseSearchScreen):
    def __init__(self, session):
        BaseSearchScreen.__init__(self, session,
            labelSearch=_("EPG event to search  (OK = keyboard):"),
            screenTitle=_("ChannelFinder – Search in EPG"))

    def _doSearch(self, query):
        results = searchEPG(query, self.selectedBouquets)
        if not results:
            self.session.open(MessageBox,
                              _('⚠  "%s" not found in EPG.') % query,
                              MessageBox.TYPE_INFO, timeout=4)
        else:
            self.session.open(EPGResultsScreen, results, query)


# ──────────────────────────────────────────────
#  Entrada – ChoiceBox
# ──────────────────────────────────────────────

def main(session, **kwargs):
    session.openWithCallback(
        lambda choice: _menuChoice(session, choice),
        ChoiceBox,
        title=_("ChannelFinder — What do you want to do?"),
        list=[
            (_("  Search channel by name "),    "channel"),
            (_("  Search event in EPG "),       "epg"),
            (_("  My zap timers "),             "timers"),
        ]
    )

def _menuChoice(session, choice):
    if choice is None:
        return
    if choice[1] == "channel":
        session.openWithCallback(
            lambda *args: main(session),
            ChannelSearchScreen)
    elif choice[1] == "epg":
        session.openWithCallback(
            lambda *args: main(session),
            EPGSearchScreen)
    elif choice[1] == "timers":
        session.openWithCallback(
            lambda *args: main(session),
            ZapTimerListScreen)


# ──────────────────────────────────────────────
#  Autostart – skin + keymap + daemon
# ──────────────────────────────────────────────

def autostart(reason, session=None, **kwargs):
    if reason == 0:
        try:
            from skin import loadSkin as skinLoad
            skinLoad(os.path.join(PLUGIN_PATH, "skin", "skin.xml"))
            print("[ChannelFinder] skin.xml loaded OK")
        except Exception as e:
            print("[ChannelFinder] Error loading skin.xml:", e)

        if session is not None:
            ZapTimerDaemon.start(session)
        else:
            print("[ChannelFinder] WARNING: autostart without session, daemon not started")
        from enigma import addFont
        font_path = os.path.join(PLUGIN_PATH, "fonts", "CFIcons.ttf")
        if os.path.exists(font_path):
            addFont(font_path, "CFIcons", 100, 1)
            print("[ChannelFinder] CFIcons.ttf loaded OK")

def Plugins(**kwargs):
    icon = path.join(path.dirname(__file__), "icon.png")
    return [
        PluginDescriptor(
            name=PLUGIN_NAME,
            description=_("Search channels and EPG event and program zaptimers for IPTV channels"),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon=icon,
            fnc=main,
        ),
        PluginDescriptor(
            name=PLUGIN_NAME,
            description=PLUGIN_DESC,
            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
            fnc=main,
        ),
        PluginDescriptor(
            name=PLUGIN_NAME,
            where=PluginDescriptor.WHERE_SESSIONSTART,
            fnc=autostart,
            needsRestart=False,
        ),
    ]