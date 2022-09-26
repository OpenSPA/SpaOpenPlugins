from enigma import eServiceReference, eServiceCenter, iServiceInformation
from Components.config import config
from Tools.Transponder import ConvertToHumanReadable
from Tools.Directories import fileExists
from ServiceReference import ServiceReference



service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'


def getBlackBouquets():
	blackl=[]
	if fileExists("/etc/keys/sinric.blackbouquets"):
		blackl=open("/etc/keys/sinric.blackbouquets","r").read().split("\n")
	return blackl


def getBouquetList():
	if config.usage.multibouquet.value:
		bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
	else:
		bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'% (service_types)
	bouquet_root = eServiceReference(bouquet_rootstr)
	bouquets = [ ]
	serviceHandler = eServiceCenter.getInstance()
	if config.usage.multibouquet.value:
		list = serviceHandler.list(bouquet_root)
		if list:
			while True:
				s = list.getNext()
				if not s.valid():
					break
				if s.flags & eServiceReference.isDirectory:
					info = serviceHandler.info(s)
					if info and info.getName(s) != "Last Scanned":
						bouquets.append((info.getName(s), s))
			return bouquets
	else:
		info = serviceHandler.info(bouquet_root)
		if info:
			bouquets.append((info.getName(bouquet_root), bouquet_root))
		return bouquets
	return None


class channels():
	def __init__(self):
		bouquets=self.getBouquets()
		self.services=self.getServices(bouquets)

	def search(self,name):
		name2 = name.lower().replace(" ","").replace("tv","").replace("hd","").replace("movistar","").replace("4k","").replace("uhd","")
		slist = []
		for entry in self.services:
			if name2 == entry[0]:
				slist.append(entry)
				
		if len(slist) == 0:
			names = name.lower().split()
			if len(names)>1:
				name2= names[0]
				for entry in self.services:
					if name2 in entry[0]:
						slist.append(entry)
				
		return slist

	def getNumber(self, number):
		if fileExists("/etc/keys/sinric.chan") and config.plugins.sinric.use_table_ch.value:
			channels = {}
			chann=open("/etc/keys/sinric.chan","r").read().split("\n")
			for can in chann:
				ch = can.split(" ")
				if len(ch)>1:
					ch_num=ch[0]
					s = can.split(":")
					if len(s)==12:
						nomcan = s[-1]
						service = ":".join(s[:-1])
						service = service.split(" ")[1]
					else:
						service=ch[1]
						try:
							refser=eServiceReference(ch[1])
							nomcan=ServiceReference(refser).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
							if len(nomcan)==0 or nomcan is None:
								nomcan=_("*** CHANNEL NOT FOUND ***")
						except:
							nomcan=_("*** CHANNEL NOT FOUND ***")
					channels[ch_num] = (service,nomcan)
			if str(number) in channels:
				channel = channels[str(number)]
				return channel[0], channel[1]
				
		for entry in self.services:
			if number == entry[5]:
				return entry[3].toString(), entry[4]

		return None

	def getBouquets(self):
		tbouquets = getBouquetList()
		bbouquets = getBlackBouquets()
		bouquets = []
		for b in tbouquets:
			if not b[0] in bbouquets:
				bouquets.append(b)
		return bouquets


#	def getBouquetList(self):
#		self.service_types = service_types_tv
#		if config.usage.multibouquet.value:
#			self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
#		else:
#			self.bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(self.service_types)
#		self.bouquet_root = eServiceReference(self.bouquet_rootstr)
#		bouquets = [ ]
#		serviceHandler = eServiceCenter.getInstance()
#		if config.usage.multibouquet.value:
#			list = serviceHandler.list(self.bouquet_root)
#			if list:
#				while True:
#					s = list.getNext()
#					if not s.valid():
#						break
#					if s.flags & eServiceReference.isDirectory:
#						info = serviceHandler.info(s)
#						if info:
#							bouquets.append((info.getName(s), s))
#				return bouquets
#		else:
#			info = serviceHandler.info(self.bouquet_root)
#			if info:
#				bouquets.append((info.getName(self.bouquet_root), self.bouquet_root))
#			return bouquets
#		return None

	def getServices(self, bouquets):
		services = []
		for bouquet in bouquets:
			Servicelist = eServiceCenter.getInstance().list(bouquet[1])
			serviceHandler=eServiceCenter.getInstance()
			if Servicelist is not None and not "Last Scanned" in bouquet[0]:
				while True:
					service = Servicelist.getNext()
					if not service.valid():
						break
					if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker):
						continue
					info = serviceHandler.info(service)
					realname = info.getName(service).replace('\xc2\x86', '').replace('\xc2\x87', '')
					transponder_info = info.getInfoObject(service, iServiceInformation.sTransponderData)
					tp_info = ConvertToHumanReadable(transponder_info)
					try:
						tipo = tp_info["system"]
					except:
						tipo = "IPTV"

					tipo = tipo.replace("2","")

					servicetype = eServiceReference(service).getData(0)
					if servicetype == 25:
						res = "HD"
					elif servicetype == 31:
						res = "UHD"
					else:
						res = "SD"
					name = realname.replace("M+","").replace(" ","").replace("#","").lower().replace("hd","").replace("4k","").replace("uhd","").replace("tv","").replace("m.","")
					num = service.getChannelNum()
					services.append((name,tipo,res,service,realname,num))
		services.sort()
		return services

			

