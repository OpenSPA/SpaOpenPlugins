## MyTubeSearch
skinMyTubeSuggestionsListScreenHD= """
 	<screen name="MyTubeSuggestionsListScreen" title="MyTube - Search" position="76,185" zPosition="1" size="987,382" flags="wfNoBorder" backgroundColor="#00ffffff">
 		<eLabel name="fondo" position="1,1" size="984,379" backgroundColor="#00555555" zPosition="-10" />
 		<ePixmap name="scrollimg" position="943,6" size="37,337" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/hdscr225-fs8.png" alphatest="blend" zPosition="8" />
 		<ePixmap name="infos" position="1,342" size="297,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/info_s-fs8HD.png" alphatest="blend" zPosition="3" />
 		<ePixmap name="bizmm2" position="837,342" size="112,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/ok_hs-fs8HD.png" alphatest="blend" zPosition="3" />		
 		<widget source="suggestionslist" render="Listbox" position="6,6" zPosition="7" size="975,337" transparent="0" backgroundColor="#00ffffff" backgroundColorSelected="#00550000" foregroundColorSelected="#00ffffff" foregroundColor="black">
 			<convert type="TemplatedMultiContent">
 				{"template": [
 						MultiContentEntryText(pos = (0, 1), size = (340, 40), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name
 						MultiContentEntryText(pos = (350, 1), size = (180, 40), font=1, flags = RT_HALIGN_RIGHT, text = 1), # index 1 are the rtesults
 					],
 				"fonts": [gFont("RegularHD", 22),gFont("RegularHD", 18)],
 				"itemHeight": 25
 				}
 			</convert>
 		</widget>
 	</screen>"""
skinMyTubeSettingsScreenHD = """
 		<screen name="MyTubeSettingsScreen" flags="wfNoBorder" position="0,0" size="1920,1080" title="MyTubePlayerMainScreen...">
 		<widget source="session.VideoPicture" render="Pig" position="86,152" size="630,400" backgroundColor="transparent" zPosition="0" />
 		<ePixmap name="dch" position="61,130" size="681,445" pixmap="~/img/bordebHD-fs8.png" alphatest="blend" zPosition="3" transparent="1" />    
 		<widget source="session.CurrentService" render="Label" position="94,168" size="600,30" font="RegularHD; 17" transparent="1" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
 			  <convert type="ServiceName">Name</convert>
 			</widget>
 		<eLabel name="tapa" position="79,168" size="628,30" backgroundColor="#aa000000" foregroundColor="#ffffa0" transparent="0" />
 
     <ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="~/img/fondoHD-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
     <ePixmap position="277,702" size="253,118" zPosition="4" pixmap="~/img/youtubelogoHD-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
     <ePixmap name="bizq" position="784,157" size="1066,57" pixmap="~/img/titulovHD-fs8.png" alphatest="blend" />
     <ePixmap name="izq" position="780,133" size="1084,802" pixmap="~/img/bordevHD-fs8.png" alphatest="blend" zPosition="1" />
     <ePixmap position="1665,986" size="213,91" zPosition="4" pixmap="~/img/logospazeHD-fs8.png" alphatest="blend" transparent="1" />
     <widget name="title" position="873,157" size="900,52" zPosition="5" valign="center" halign="left" font="RegularHD;20" transparent="1" foregroundColor="#770000" backgroundColor="#00ffffff" noWrap="1" />
     <widget name="config" zPosition="2" itemHeight="42" position="804,219" size="1024,675" font="RegularHD;20" scrollbarMode="showOnDemand" transparent="1" foregroundColorSelected="#00ffffff" foregroundColor="black" backgroundColor="#00ffffff" backgroundColorSelected="#00550000" />
     <ePixmap position="69,1009" zPosition="4" size="52,37" pixmap="~/img/redHD.png" transparent="1" alphatest="on" />
     <widget name="key_red" position="126,1011" zPosition="5" size="316,37" valign="center" halign="left" font="RegularHD; 16" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
     <ePixmap position="477,1009" zPosition="4" size="52,37" pixmap="~/img/greenHD.png" transparent="1" alphatest="blend" />
     <widget name="key_green" position="534,1011" zPosition="5" size="267,37" valign="center" halign="left" font="RegularHD; 16" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" backgroundColor="black" />
   </screen>"""
 
skinMyTubeTasksScreenHD = """
 		<screen name="MyTubeTasksScreen" flags="wfNoBorder" position="0,0" size="1920,1080" title="MyTubePlayerMainScreen...">
 		<widget source="session.VideoPicture" render="Pig" position="88,153" size="630,400" backgroundColor="transparent" zPosition="0" />
 		<ePixmap name="dch" position="61,130" size="681,445" pixmap="~/img/bordebHD-fs8.png" alphatest="blend" zPosition="3" transparent="1" />    
 		<widget source="session.CurrentService" render="Label" position="94,168" size="600,30" font="RegularHD; 17" transparent="1" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
 			  <convert type="ServiceName">Name</convert>
 			</widget>
 		<eLabel name="tapa" position="79,168" size="628,30" backgroundColor="#aa000000" foregroundColor="#ffffa0" transparent="0" />
 
 		<ePixmap position="center,center" zPosition="-1" size="1920,1080" pixmap="~/img/fondoHD-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
 		<ePixmap position="270,687" size="253,118" zPosition="4" pixmap="~/img/youtubelogoHD-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
 		<ePixmap name="bizq" position="765,159" size="1066,57" pixmap="~/img/titulovHD-fs8.png" alphatest="blend" />
 		<ePixmap name="izq" position="759,133" size="1084,802" pixmap="~/img/bordevHD-fs8.png" alphatest="blend" zPosition="1" />
 		<ePixmap position="1665,991" size="213,91" zPosition="4" pixmap="~/img/logospazeHD-fs8.png" alphatest="blend" transparent="1" />
 		<widget name="title" position="847,158" size="955,52" zPosition="5" valign="center" halign="left" font="RegularHD;20" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
 		<widget source="tasklist" render="Listbox" position="786,225" size="1024,675" zPosition="7" scrollbarMode="showOnDemand" transparent="1" foregroundColor="#00990000" backgroundColor="#00ffffff" foregroundColorSelected="#00550000" backgroundColorSelected="#00ffffff">
 		  <convert type="TemplatedMultiContent">
 						{"template": [
 								MultiContentEntryText(pos = (0, 2), size = (300, 36), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 1 is the name
 								MultiContentEntryText(pos = (315, 2), size = (225, 36), font=1, flags = RT_HALIGN_RIGHT, text = 2), # index 2 is the state
 								MultiContentEntryProgress(pos = (555, 2), size = (150, 36), percent = -3), # index 3 should be progress 
 								MultiContentEntryText(pos = (720, 2), size = (150, 36), font=1, flags = RT_HALIGN_RIGHT, text = 4), # index 4 is the percentage
 							],
 						"fonts": [gFont("RegularHD", 22),gFont("RegularHD", 18)],
 						"itemHeight": 38
 						}
 					</convert>
 		</widget>
 		<ePixmap position="69,1022" zPosition="4" size="52,37" pixmap="~/img/redHD.png" transparent="1" alphatest="on" />
 		<widget name="key_red" position="126,1026" zPosition="5" size="316,30" valign="center" halign="left" font="RegularHD; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" />
   </screen>"""
 
skinMyTubeHistoryScreenHD = """
 		<screen name="MyTubeHistoryScreen" position="76,105" zPosition="1" size="987,528" flags="wfNoBorder" backgroundColor="#00ffffff" title="MyTube - History">
 			<eLabel name="fondo" position="1,1" size="984,525" backgroundColor="#00555555" zPosition="-10" />
 			<ePixmap name="infohis" position="1,492" size="150,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/info_h-fs8HD.png" alphatest="blend" zPosition="3" />
 			<ePixmap name="scrollimg" position="943,6" size="37,487" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/hdscr325-fs8.png" alphatest="blend" zPosition="8" />
 			<ePixmap name="bizmm2" position="837,492" size="112,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/ok_hs-fs8HD.png" alphatest="blend" zPosition="3" />
 			<widget source="historylist" render="Listbox" position="6,6" zPosition="7" size="975,487" scrollbarMode="showAlways" transparent="0" backgroundColor="#00ffffff" backgroundColorSelected="#00550000" foregroundColorSelected="#00ffffff" foregroundColor="black">
 				<convert type="TemplatedMultiContent">
 					{"template": [
 							MultiContentEntryText(pos = (0, 0), size = (340, 40), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name
 						],
 					"fonts": [gFont("RegularHD", 22),gFont("RegularHD", 18)],
 					"itemHeight": 42
 					}
 				</convert>
 			</widget>
 		</screen>"""
 ## plugin
skinMyTubePlayerMainScreenHD = """
 		<screen name="MyTubePlayerMainScreen" flags="wfNoBorder" position="0,0" size="1921,1081" title="MyTubePlayerMainScreen..." backgroundColor="#00ffffff">
 <widget source="session.VideoPicture" render="Pig" position="1213,138" size="630,400" backgroundColor="transparent" zPosition="0" />
 <ePixmap name="dch" position="1196,120" size="681,445" pixmap="~/img/bordebHD-fs8.png" alphatest="blend" zPosition="3" transparent="1" />    
 <widget source="session.CurrentService" render="Label" position="1229,152" size="600,30" font="RegularHD; 17" transparent="1" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
       <convert type="ServiceName">Name</convert>
     </widget>
 <eLabel name="tapa" position="1216,152" size="628,30" backgroundColor="#aa000000" foregroundColor="#ffffa0" transparent="0" />
 
 <ePixmap name="bizmm2" position="1110,114" size="75,37" pixmap="~/img/chmas_bHD-fs8.png" alphatest="blend" zPosition="4" />
 <ePixmap name="bordebuscar" position="54,96" size="1057,67" pixmap="~/img/bordebuscarHD.png" alphatest="blend" zPosition="3" transparent="1" />
 
 <ePixmap position="0,0" zPosition="-1" size="1921,1081" pixmap="~/img/fondoHD-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
     <widget name="config" zPosition="8" position="117,112" size="982,37" itemHeight="42" scrollbarMode="showNever" transparent="1" backgroundColor="#00ffffff" foregroundColor="#00000000" foregroundColorSelected="#000000" backgroundColorSelected="#00ffffff" />
 	<widget source="feedlist" render="Listbox" position="79,262" size="1023,685" zPosition="0" scrollbarMode="showAlways" transparent="0" backgroundPixmap="~/img/fondo75HD-fs8.png" selectionPixmap="~/img/seleccion75HD-fs8.png" foregroundColorSelected="#990000" backgroundColor="#00ffffff" backgroundColorSelected="#00ffffff">
 		  <convert type="TemplatedMultiContent">
 			{"templates":
 				{"default": (114,[
 						MultiContentEntryPixmapAlphaTest(pos = (0, 0), size = (150, 113), png = 4), # index 4 is the thumbnail
 						MultiContentEntryText(pos = (156, 2), size = (900, 55), font=0, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 1,color=0x000000), # index 1 is the Title
 						MultiContentEntryText(pos = (156, 41), size = (450, 43), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 6,color=0x444444), # index 6 is the Channel
 						MultiContentEntryText(pos = (156, 72), size = (450, 35), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 5,color=0x444444), # index 5 is the Published Date
 					]),
 				"state": (114,[
 						MultiContentEntryText(pos = (15, 2), size = (840, 55), font=2, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 0,color=0x000000), # index 0 is the name
 						MultiContentEntryText(pos = (15, 33), size = (840, 69), font=3, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 1,color=0x444444), # index 2 is the description
 					])
 				},
 				"fonts": [gFont("RegularHD", 20),gFont("RegularHD", 16),gFont("RegularHD", 20),gFont("RegularHD", 18)],
 				"itemHeight": 114
 			}
 			</convert>
 		</widget>
 	<ePixmap name="scrollimg" position="1065,262" size="37,675" pixmap="~/img/hdscrmain-fs8.png" alphatest="blend" zPosition="1" />		
     <ePixmap pixmap="~/img/infoHD.png" position="123,30" zPosition="4" size="52,38" alphatest="blend" transparent="1" />
     <ePixmap pixmap="~/img/menuHD.png" position="69,30" zPosition="4" size="52,38" alphatest="blend" transparent="1" />
     <ePixmap position="1615,886" size="253,118" zPosition="4" pixmap="~/img/youtubelogoHD-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
     <ePixmap position="69,1012" zPosition="4" size="52,38" pixmap="~/img/redHD.png" transparent="1" alphatest="blend" />
     <ePixmap position="477,1012" zPosition="4" size="52,38" pixmap="~/img/greenHD.png" transparent="1" alphatest="blend" />
     <ePixmap position="813,1012" zPosition="4" size="52,38" pixmap="~/img/yellowHD.png" transparent="1" alphatest="blend" />
     <widget name="key_red" position="128,1018" zPosition="5" size="316,30" valign="center" halign="left" font="RegularHD; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" backgroundColor="#00000000" />
     <widget name="key_green" position="536,1018" zPosition="5" size="267,30" valign="center" halign="left" font="RegularHD; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" backgroundColor="#00000000" />
     <widget name="key_yellow" position="873,1018" zPosition="5" size="280,30" valign="center" halign="left" font="RegularHD; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" backgroundColor="#00000000" />
     <widget name="ButtonBlue" pixmap="~/img/blueHD.png" position="1176,1022" zPosition="10" size="52,37" transparent="1" alphatest="blend" />
     <widget name="VKeyIcon" pixmap="~/img/vkHD.png" position="1233,1008" zPosition="10" size="48,24" transparent="1" alphatest="blend" />
     <widget name="thumbnail" position="852,627" size="150,112" alphatest="on" /> # fake entry for dynamic thumbnail resizing, currently there is no other way doing this.
     <widget name="HelpWindow" position="1168,645" zPosition="6" size="1,1" transparent="1" alphatest="on" />
     <ePixmap name="izq" position="54,172" size="1080,802" pixmap="~/img/bordevHD-fs8.png" alphatest="blend" zPosition="1" />
     <ePixmap name="bizq" position="60,196" size="1066,57" pixmap="~/img/titulovHD-fs8.png" alphatest="blend" />
     <ePixmap name="bizqlogo" position="141,202" size="163,40" pixmap="~/img/youtubevHD-fs8.png" alphatest="blend" zPosition="3" />
     <ePixmap position="1659,995" size="213,91" zPosition="4" pixmap="~/img/logospazeHD-fs8.png" alphatest="blend" transparent="1" />
     <widget name="feed" position="525,202" size="570,45" zPosition="6" font="RegularHD;18" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" halign="right"/>
     <widget name="user" position="1200,577" size="507,52" zPosition="5" font="RegularHD;22" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
     <widget name="icon" position="1200,630" size="127,127" zPosition="5" transparent="1" backgroundColor="#00ffffff" />
     <widget name="csubscriptors" position="1350,630" size="315,52" foregroundColor="#00000000" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" />
     <widget name="cviews" position="1350,660" size="315,52" foregroundColor="#00000000" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" />
<!--     <widget name="cvideowatch" position="1350,690" size="315,52" foregroundColor="#00000000" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" /> -->
     <widget name="cuser_uploads" position="1350,690" size="315,52" foregroundColor="#00000000" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" />
     <widget name="subscriptors" position="1680,630" size="180,52" foregroundColor="#00000000" halign="right" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" />
     <widget name="views" position="1680,660" size="180,52" foregroundColor="#00000000" halign="right" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" />
<!--     <widget name="videowatch" position="1680,690" size="180,52" foregroundColor="#00000000" halign="right" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" /> -->
     <widget name="user_uploads" position="1680,690" size="180,52" foregroundColor="#00000000" halign="right" zPosition="5" font="RegularHD;15" transparent="1"  noWrap="1" />
     <widget name="result" position="82,945" size="937,30" zPosition="5" font="RegularHD;15" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
 </screen>"""
 
skinMyTubeVideoInfoScreenHD = """
 		<screen name="MyTubeVideoInfoScreen" flags="wfNoBorder" position="0,0" size="1920,1080" title="MyTubePlayerMainScreen..." backgroundColor="#00ffffff">
     <ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="~/img/fondoHD-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
     <widget name="title" position="148,165" size="957,52" zPosition="5" valign="center" halign="left" font="RegularHD;18" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
     <widget name="like" pixmap="~/img/likeHD.png" position="1153,97" zPosition="7" size="150,105" transparent="1" alphatest="on" />
     <widget name="dislike" pixmap="~/img/dislikeHD.png" position="1404,97" zPosition="7" size="150,105" transparent="1" alphatest="on" />
     <widget name="llike" position="1252,117" size="450,37" zPosition="10" font="RegularHD;18" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget name="ldislike" position="1500,117" size="450,37" zPosition="10" font="RegularHD;18" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget name="author" position="106,241" size="450,37" zPosition="10" font="RegularHD;21" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget source="infolist" render="Listbox" position="1221,171" size="570,750" zPosition="6" scrollbarMode="showNever" selectionDisabled="1" transparent="1" foregroundColorSelected="#990000" backgroundColor="#00ffffff" backgroundColorSelected="#00ffffff">
       <convert type="TemplatedMultiContent">
 		{"templates":
 			{"default": (750,[
 					MultiContentEntryPixmapAlphaTest(pos = (150, 0), size = (240, 180), png = 0), # index 0 is the thumbnail
 					MultiContentEntryPixmapAlphaTest(pos = (150, 188), size = (240, 180), png = 1), # index 0 is the thumbnail
 					MultiContentEntryPixmapAlphaTest(pos = (150, 375), size = (240, 180), png = 2), # index 0 is the thumbnail
 					MultiContentEntryPixmapAlphaTest(pos = (150, 555), size = (240, 180), png = 3), # index 0 is the thumbnail
 				]),
 			"state": (750,[
 					MultiContentEntryText(pos = (0, 0), size = (420, 750), font=2, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 0,color=0x555555), # index 0 is the name
 				])
 			},
 			"fonts": [gFont("RegularHD", 19),gFont("RegularHD", 14),gFont("RegularHD", 19)],
 			"itemHeight": 750
 		}
 		</convert>
     </widget>
     <widget name="author" position="106,241" size="600,37" zPosition="10" font="RegularHD;21" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget name="duration" position="567,241" size="519,37" zPosition="10" font="RegularHD;21" transparent="1" halign="right" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget name="published" position="106,279" size="600,37" zPosition="10" font="RegularHD;21" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget name="views" position="567,279" size="519,37" zPosition="10" font="RegularHD;21" transparent="1" halign="right" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget name="tags" position="106,319" size="979,37" zPosition="10" font="RegularHD;18" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
     <widget name="detailtext" position="106,382" size="978,517" zPosition="10" font="RegularHD;18" transparent="1" halign="left" valign="top" foregroundColor="#00000000" backgroundColor="#00ffffff" />
     <ePixmap position="69,1022" zPosition="4" size="52,37" pixmap="~/img/redHD.png" transparent="1" alphatest="on" />
     <widget name="key_red" position="126,1026" zPosition="5" size="316,30" valign="center" halign="left" font="RegularHD; 16" transparent="1" backgroundColor="#00000000" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" />
     <widget name="thumbnail" position="1381,186" size="240,180" alphatest="on" zPosition="11" /> # fake entry for dynamic thumbnail resizing, currently there is no other way doing this.
 	 <ePixmap position="1621,66" size="253,118" zPosition="4" pixmap="~/img/youtubelogoHD-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
	 <ePixmap name="bizq" position="54,166" size="1066,57" pixmap="~/img/titulovHD-fs8.png" alphatest="blend" />
	 <ePixmap name="izq" position="54,133" size="1084,802" pixmap="~/img/bordevHD-fs8.png" alphatest="blend" zPosition="1" />
	 <ePixmap position="1666,998" size="213,91" zPosition="4" pixmap="~/img/logospazeHD-fs8.png" alphatest="blend" transparent="1" /><eLabel name="linea1" position="1111,171" size="808,1" backgroundColor="#00cccccc" />
	 <eLabel name="linea2" position="1111,921" size="808,1" backgroundColor="#00cccccc" />
	</screen>"""
 
skinMyTubeVideoHelpScreenHD = """
 		<screen name="MyTubeVideoHelpScreen" flags="wfBorder" position="center,center" size="1080,864" title="MyTube - Help">
 			
 			<widget name="title" position="90,75" size="900,75" zPosition="5" valign="center" halign="left" font="RegularHD;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
 			<widget name="detailtext" position="90,180" size="915,555" zPosition="10" font="RegularHD;21" transparent="1" halign="left" valign="top" />
 			<ePixmap position="150,750" size="150,60" zPosition="0" pixmap="~/img/hdplugin.png" alphatest="on" transparent="1" />
 			<ePixmap position="330,750" zPosition="4" size="210,60" pixmap="usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" transparent="1" alphatest="on" />
 			<widget name="key_red" position="330,750" zPosition="5" size="210,60" valign="center" halign="center" font="RegularHD;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
 		</screen>"""
 
skinMyTubePlayerHD = """<screen name="MyTubePlayer" flags="wfNoBorder" position="0,870" size="1921,231" title="MyTube - Player" backgroundColor="#ff000000">
 	<eLabel name="lineafondo" position="0,31" size="1921,1" backgroundColor="#00444444" zPosition="11" />
     <ePixmap position="1749,46" size="105,40" zPosition="4" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/youtubevHD-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
     <widget source="session.CurrentService" zPosition="5" render="Label" position="160,42" size="1408,36" font="RegularHD;20" backgroundColor="#00ffffff" foregroundColor="#00990000" transparent="1">
       <convert type="ServiceName">Name</convert>
     </widget>
     <widget source="session.CurrentService" render="Label" position="877,92" size="135,30" font="RegularHD; 16" halign="center" backgroundColor="#00ffffff" foregroundColor="#00333333" shadowColor="#cecece" shadowOffset="-1,-1" transparent="1">
       <convert type="ServicePosition">Length</convert>
     </widget>
     <widget source="session.CurrentService" render="Label" position="420,112" size="150,30" font="RegularHD;18" halign="right" valign="center" backgroundColor="#00ffffff" foregroundColor="#00333333" shadowColor="#cecece" shadowOffset="-1,-1" transparent="1">
       <convert type="ServicePosition">Position</convert>
     </widget>
     <widget source="session.CurrentService" render="PositionGauge" position="576,120" size="765,18" zPosition="2" pointer="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/position_pointer.png:810,4" transparent="1" foregroundColor="#00000000">
       <convert type="ServicePosition">Gauge</convert>
     </widget>
     <widget source="session.CurrentService" render="Label" position="1348,112" size="150,30" font="RegularHD;18" halign="left" valign="center" backgroundColor="#00ffffff" foregroundColor="#00333333" shadowColor="#cecece" shadowOffset="-1,-1" transparent="1">
       <convert type="ServicePosition">Remaining</convert>
     </widget>
     <eLabel name="new eLabel" position="576,124" size="765,8" zPosition="1" backgroundColor="#00cccccc" />
     <ePixmap name="new ePixmap" position="66,22" size="96,96" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/hdnmcfs8.png" alphatest="blend" zPosition="10" />
     <eLabel name="fondoblanco" position="0,31" size="1920,196" backgroundColor="#10ffffff" zPosition="-10" />
   </screen>"""
   
 # ~/img/ ~/img/
