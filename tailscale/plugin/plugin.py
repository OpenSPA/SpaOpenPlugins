# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigOnOff, ConfigText
from boxbranding import getImageDistro
from Plugins.Extensions.Tailscale.__init__ import _

config.tailscale = ConfigSubsection()
config.tailscale.autostart = ConfigOnOff(default=True)
config.tailscale.networkname = ConfigText(default='')
config.tailscale.apikey = ConfigText(default='', fixed_size=False)

def mainTailscale(session, **kwargs):
	from Plugins.Extensions.Tailscale.tsnetwork import TailscaleNetwork
	session.open(TailscaleNetwork)

def menuTailscale(menuid, **kwargs):
	if menuid == 'network':
		return [(_('Tailscale-VPN'), mainTailscale, 'tailscale', None)]
	else:
		return []

def Plugins(**kwargs):
	if getImageDistro() == 'openspa':
		list = []
		list.append(PluginDescriptor(name=_('Tailscale-VPN'), description=_('Global Area Networking'), where=PluginDescriptor.WHERE_PLUGINMENU, fnc=mainTailscale, icon='plugin.png'))
		list.append(PluginDescriptor(name=_('Tailscale-VPN'), description=_('Global Area Networking'), where = PluginDescriptor.WHERE_MENU, fnc=menuTailscale))
		return list