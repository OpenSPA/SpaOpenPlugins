## MyTubeSearch
skinMyTubeSuggestionsListScreen= """
	<screen name="MyTubeSuggestionsListScreen" title="MyTube - Search" position="76,105" zPosition="1" size="658,255" flags="wfNoBorder" backgroundColor="#00ffffff">
		<eLabel name="fondo" position="1,1" size="656,253" backgroundColor="#00555555" zPosition="-10" />
		<ePixmap name="scrollimg" position="629,4" size="25,225" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/scr225-fs8.png" alphatest="blend" zPosition="8" />
		<ePixmap name="infos" position="1,228" size="198,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/info_s-fs8.png" alphatest="blend" zPosition="3" />
		<ePixmap name="bizmm2" position="558,228" size="75,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/ok_hs-fs8.png" alphatest="blend" zPosition="3" />		
		<widget source="suggestionslist" render="Listbox" position="4,4" zPosition="7" size="650,225" transparent="0" backgroundColor="#00ffffff" backgroundColorSelected="#00550000" foregroundColorSelected="#00ffffff" foregroundColor="black">
			<convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryText(pos = (0, 1), size = (340, 24), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name
						MultiContentEntryText(pos = (350, 1), size = (180, 24), font=1, flags = RT_HALIGN_RIGHT, text = 1), # index 1 are the rtesults
					],
				"fonts": [gFont("Regular", 22),gFont("Regular", 18)],
				"itemHeight": 25
				}
			</convert>
		</widget>
	</screen>"""
skinMyTubeSettingsScreen = """
		<screen name="MyTubeSettingsScreen" flags="wfNoBorder" position="0,0" size="1280,720" title="MyTubePlayerMainScreen...">
		<widget source="session.VideoPicture" render="Pig" position="59,102" size="420,267" backgroundColor="transparent" zPosition="0" />
		<ePixmap name="dch" position="41,87" size="454,297" pixmap="~/img/bordeb-fs8.png" alphatest="blend" zPosition="3" transparent="1" />    
		<widget source="session.CurrentService" render="Label" position="60,112" size="400,20" font="Regular; 17" transparent="1" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
			  <convert type="ServiceName">Name</convert>
			</widget>
		<eLabel name="tapa" position="53,112" size="419,20" backgroundColor="#aa000000" foregroundColor="#ffffa0" transparent="0" />

    <ePixmap position="0,0" zPosition="-1" size="1280,720" pixmap="~/img/fondo-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
    <ePixmap position="185,468" size="169,79" zPosition="4" pixmap="~/img/youtubelogo-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
    <ePixmap name="bizq" position="523,105" size="711,38" pixmap="~/img/titulov-fs8.png" alphatest="blend" />
    <ePixmap name="izq" position="520,89" size="723,535" pixmap="~/img/bordev-fs8.png" alphatest="blend" zPosition="1" />
    <ePixmap position="1110,651" size="142,61" zPosition="4" pixmap="~/img/logospaze-fs8.png" alphatest="blend" transparent="1" />
    <widget name="title" position="582,105" size="600,35" zPosition="5" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="#770000" backgroundColor="#00ffffff" noWrap="1" />
    <widget name="config" zPosition="2" position="536,146" size="683,450" scrollbarMode="showOnDemand" transparent="1" foregroundColorSelected="#00ffffff" foregroundColor="black" backgroundColor="#00ffffff" backgroundColorSelected="#00550000" />
    <ePixmap position="46,666" zPosition="4" size="35,25" pixmap="~/img/red.png" transparent="1" alphatest="on" />
    <widget name="key_red" position="80,666" zPosition="5" size="211,25" valign="center" halign="left" font="Regular; 16" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
    <ePixmap position="318,666" zPosition="4" size="35,25" pixmap="~/img/green.png" transparent="1" alphatest="blend" />
    <widget name="key_green" position="352,666" zPosition="5" size="178,25" valign="center" halign="left" font="Regular; 16" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" backgroundColor="black" />
  </screen>"""

skinMyTubeTasksScreen = """
		<screen name="MyTubeTasksScreen" flags="wfNoBorder" position="0,0" size="1280,720" title="MyTubePlayerMainScreen...">
		<widget source="session.VideoPicture" render="Pig" position="59,102" size="420,267" backgroundColor="transparent" zPosition="0" />
		<ePixmap name="dch" position="41,87" size="454,297" pixmap="~/img/bordeb-fs8.png" alphatest="blend" zPosition="3" transparent="1" />    
		<widget source="session.CurrentService" render="Label" position="60,112" size="400,20" font="Regular; 17" transparent="1" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
			  <convert type="ServiceName">Name</convert>
			</widget>
		<eLabel name="tapa" position="53,112" size="419,20" backgroundColor="#aa000000" foregroundColor="#ffffa0" transparent="0" />

		<ePixmap position="center,center" zPosition="-1" size="1280,720" pixmap="~/img/fondo-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
		<ePixmap position="180,458" size="169,79" zPosition="4" pixmap="~/img/youtubelogo-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
		<ePixmap name="bizq" position="510,106" size="711,38" pixmap="~/img/titulov-fs8.png" alphatest="blend" />
		<ePixmap name="izq" position="506,89" size="723,535" pixmap="~/img/bordev-fs8.png" alphatest="blend" zPosition="1" />
		<ePixmap position="1110,651" size="142,61" zPosition="4" pixmap="~/img/logospaze-fs8.png" alphatest="blend" transparent="1" />
		<widget name="title" position="565,108" size="637,35" zPosition="5" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
		<widget source="tasklist" render="Listbox" position="524,150" size="683,450" zPosition="7" scrollbarMode="showOnDemand" transparent="1" foregroundColor="#00990000" backgroundColor="#00ffffff" foregroundColorSelected="#00550000" backgroundColorSelected="#00ffffff">
		  <convert type="TemplatedMultiContent">
						{"template": [
								MultiContentEntryText(pos = (0, 1), size = (200, 24), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 1 is the name
								MultiContentEntryText(pos = (210, 1), size = (150, 24), font=1, flags = RT_HALIGN_RIGHT, text = 2), # index 2 is the state
								MultiContentEntryProgress(pos = (370, 1), size = (100, 24), percent = -3), # index 3 should be progress 
								MultiContentEntryText(pos = (480, 1), size = (100, 24), font=1, flags = RT_HALIGN_RIGHT, text = 4), # index 4 is the percentage
							],
						"fonts": [gFont("Regular", 22),gFont("Regular", 18)],
						"itemHeight": 25
						}
					</convert>
		</widget>
		<ePixmap position="46,668" zPosition="4" size="35,25" pixmap="~/img/red.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="80,671" zPosition="5" size="211,20" valign="center" halign="left" font="Regular; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" />
  </screen>"""

skinMyTubeHistoryScreen = """
		<screen name="MyTubeHistoryScreen" position="76,105" zPosition="1" size="658,352" flags="wfNoBorder" backgroundColor="#00ffffff" title="MyTube - History">
			<eLabel name="fondo" position="1,1" size="656,350" backgroundColor="#00555555" zPosition="-10" />
			<ePixmap name="infohis" position="1,328" size="100,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/info_h-fs8.png" alphatest="blend" zPosition="3" />
			<ePixmap name="scrollimg" position="629,4" size="25,325" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/scr325-fs8.png" alphatest="blend" zPosition="8" />
			<ePixmap name="bizmm2" position="558,328" size="75,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/ok_hs-fs8.png" alphatest="blend" zPosition="3" />
			<widget source="historylist" render="Listbox" position="4,4" zPosition="7" size="650,325" scrollbarMode="showAlways" transparent="0" backgroundColor="#00ffffff" backgroundColorSelected="#00550000" foregroundColorSelected="#00ffffff" foregroundColor="black">
				<convert type="TemplatedMultiContent">
					{"template": [
							MultiContentEntryText(pos = (0, 1), size = (340, 26), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name
						],
					"fonts": [gFont("Regular", 20),gFont("Regular", 18)],
					"itemHeight": 30
					}
				</convert>
			</widget>
		</screen>"""
## plugin
skinMyTubePlayerMainScreen = """
		<screen name="MyTubePlayerMainScreen" flags="wfNoBorder" position="0,0" size="1281,721" title="MyTubePlayerMainScreen..." backgroundColor="#00ffffff">
<widget source="session.VideoPicture" render="Pig" position="809,87" size="420,267" backgroundColor="transparent" zPosition="0" />
<ePixmap name="dch" position="791,72" size="454,297" pixmap="~/img/bordeb-fs8.png" alphatest="blend" zPosition="3" transparent="1" />    
<widget source="session.CurrentService" render="Label" position="815,97" size="400,20" font="Regular; 17" transparent="1" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
      <convert type="ServiceName">Name</convert>
    </widget>
<eLabel name="tapa" position="808,97" size="419,20" backgroundColor="#aa000000" foregroundColor="#ffffa0" transparent="0" />

<ePixmap name="bizmm2" position="740,76" size="50,25" pixmap="~/img/chmas_b-fs8.png" alphatest="blend" zPosition="4" />
<ePixmap name="bordebuscar" position="36,64" size="705,45" pixmap="~/img/bordebuscar.png" alphatest="blend" zPosition="3" transparent="1" />

<ePixmap position="0,0" zPosition="-1" size="1281,721" pixmap="~/img/fondo-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
    <widget name="config" zPosition="8" position="78,75" size="655,25" scrollbarMode="showNever" transparent="1" backgroundColor="#00ffffff" foregroundColor="#00000000" foregroundColorSelected="#000000" backgroundColorSelected="#00ffffff" />
	<widget source="feedlist" render="Listbox" position="53,175" size="682,450" zPosition="0" scrollbarMode="showAlways" transparent="0" backgroundPixmap="~/img/fondo75-fs8.png" selectionPixmap="~/img/seleccion75-fs8.png" foregroundColorSelected="#990000" backgroundColor="#00ffffff" backgroundColorSelected="#00ffffff">
		  <convert type="TemplatedMultiContent">
			{"templates":
				{"default": (75,[
						MultiContentEntryPixmapAlphaTest(pos = (0, 0), size = (100, 75), png = 4), # index 4 is the thumbnail
						MultiContentEntryText(pos = (104, 0), size = (600, 32), font=0, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 1,color=0x000000), # index 1 is the Title
						MultiContentEntryText(pos = (104, 25), size = (300, 26), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 6,color=0x444444), # index 6 is the Channel
						MultiContentEntryText(pos = (104, 44), size = (300, 26), font=1, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 5,color=0x444444), # index 5 is the Published Date
						MultiContentEntryPixmapAlphaTest(pos = (560, 24), size = (50, 35), png = 7), # index 7 is the channel icon
					]),
				"state": (75,[
						MultiContentEntryText(pos = (10, 1), size = (560, 32), font=2, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 0,color=0x000000), # index 0 is the name
						MultiContentEntryText(pos = (10, 22), size = (560, 46), font=3, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 1,color=0x444444), # index 2 is the description
					])
				},
				"fonts": [gFont("Regular", 19),gFont("Regular", 16),gFont("Regular", 20),gFont("Regular", 18)],
				"itemHeight": 75
			}
			</convert>
		</widget>
	<ePixmap name="scrollimg" position="710,175" size="25,450" pixmap="~/img/scrmain-fs8.png" alphatest="blend" zPosition="1" />		
    <ePixmap pixmap="~/img/info.png" position="82,24" zPosition="4" size="35,25" alphatest="blend" transparent="1" />
    <ePixmap pixmap="~/img/menu.png" position="46,24" zPosition="4" size="35,25" alphatest="blend" transparent="1" />
    <ePixmap position="1077,581" size="169,79" zPosition="4" pixmap="~/img/youtubelogo-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
    <ePixmap position="46,668" zPosition="4" size="35,25" pixmap="~/img/red.png" transparent="1" alphatest="blend" />
    <ePixmap position="318,668" zPosition="4" size="35,25" pixmap="~/img/green.png" transparent="1" alphatest="blend" />
    <ePixmap position="542,668" zPosition="4" size="35,25" pixmap="~/img/yellow.png" transparent="1" alphatest="blend" />
    <widget name="key_red" position="80,671" zPosition="5" size="211,20" valign="center" halign="left" font="Regular; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" backgroundColor="#00000000" />
    <widget name="key_green" position="352,671" zPosition="5" size="178,20" valign="center" halign="left" font="Regular; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" backgroundColor="#00000000" />
    <widget name="key_yellow" position="577,671" zPosition="5" size="187,20" valign="center" halign="left" font="Regular; 16" transparent="1" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" backgroundColor="#00000000" />
    <widget name="ButtonBlue" pixmap="~/img/blue.png" position="784,668" zPosition="10" size="35,25" transparent="1" alphatest="blend" />
    <widget name="VKeyIcon" pixmap="~/img/vk.png" position="822,672" zPosition="10" size="32,16" transparent="1" alphatest="blend" />
    <widget name="thumbnail" position="568,418" size="100,75" alphatest="on" /> # fake entry for dynamic thumbnail resizing, currently there is no other way doing this.
	<widget name="HelpWindow" position="779,430" zPosition="6" size="1,1" transparent="1" alphatest="on" />
	<ePixmap name="izq" position="36,115" size="720,535" pixmap="~/img/bordev-fs8.png" alphatest="blend" zPosition="1" /><ePixmap name="bizq" position="40,131" size="711,38" pixmap="~/img/titulov-fs8.png" alphatest="blend" /><ePixmap name="bizqlogo" position="94,135" size="109,27" pixmap="~/img/youtubev-fs8.png" alphatest="blend" zPosition="3" /><ePixmap position="1106,650" size="142,61" zPosition="4" pixmap="~/img/logospaze-fs8.png" alphatest="blend" transparent="1" />
    <widget name="feed" position="350,135" size="380,30" zPosition="6" font="Regular;18" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" halign="right"/>
    <widget name="user" position="800,385" size="338,35" zPosition="5" font="Regular;22" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
    <widget name="icon" position="800,420" size="85,85" zPosition="5" transparent="1" backgroundColor="#00ffffff" />
    <widget name="csubscriptors" position="900,420" size="210,35" foregroundColor="#00000000" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" />
    <widget name="cviews" position="900,440" size="210,35" foregroundColor="#00000000" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" />
<!--    <widget name="cvideowatch" position="900,460" size="210,35" foregroundColor="#00000000" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" /> -->
    <widget name="cuser_uploads" position="900,460" size="210,35" foregroundColor="#00000000" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" />
    <widget name="subscriptors" position="1120,420" size="120,35" foregroundColor="#00000000" halign="right" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" />
    <widget name="views" position="1120,440" size="120,35" foregroundColor="#00000000" halign="right" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" />
<!--    <widget name="videowatch" position="1120,460" size="120,35" foregroundColor="#00000000" halign="right" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" /> -->
    <widget name="user_uploads" position="1120,460" size="120,35" foregroundColor="#00000000" halign="right" zPosition="5" font="Regular;15" transparent="1"  noWrap="1" />
    <widget name="result" position="55,630" size="625,20" zPosition="5" font="Regular;15" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
</screen>"""

skinMyTubeVideoInfoScreen = """
		<screen name="MyTubeVideoInfoScreen" flags="wfNoBorder" position="0,0" size="1280,720" title="MyTubePlayerMainScreen..." backgroundColor="#00ffffff">
    <ePixmap position="0,0" zPosition="-1" size="1280,720" pixmap="~/img/fondo-fs8.png" alphatest="on" transparent="1" backgroundColor="#00ffffff" />
    <widget name="title" position="99,113" size="638,35" zPosition="5" valign="center" halign="left" font="Regular;18" transparent="1" foregroundColor="#00770000" backgroundColor="#00ffffff" noWrap="1" />
    <widget name="like" pixmap="~/img/like.png" position="769,65" zPosition="7" size="100,70" transparent="1" alphatest="on" />
    <widget name="dislike" pixmap="~/img/dislike.png" position="936,65" zPosition="7" size="100,70" transparent="1" alphatest="on" />
    <widget name="llike" position="835,78" size="300,25" zPosition="10" font="Regular;18" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget name="ldislike" position="1000,78" size="300,25" zPosition="10" font="Regular;18" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget name="author" position="71,161" size="300,25" zPosition="10" font="Regular;21" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget source="infolist" render="Listbox" position="814,114" size="380,500" zPosition="6" scrollbarMode="showNever" selectionDisabled="1" transparent="1" foregroundColorSelected="#990000" backgroundColor="#00ffffff" backgroundColorSelected="#00ffffff">
      <convert type="TemplatedMultiContent">
		{"templates":
			{"default": (500,[
					MultiContentEntryPixmapAlphaTest(pos = (100, 0), size = (160, 120), png = 0), # index 0 is the thumbnail
					MultiContentEntryPixmapAlphaTest(pos = (100, 125), size = (160, 120), png = 1), # index 0 is the thumbnail
					MultiContentEntryPixmapAlphaTest(pos = (100, 250), size = (160, 120), png = 2), # index 0 is the thumbnail
					MultiContentEntryPixmapAlphaTest(pos = (100, 370), size = (160, 120), png = 3), # index 0 is the thumbnail
				]),
			"state": (500,[
					MultiContentEntryText(pos = (0, 0), size = (280, 500), font=2, flags = RT_HALIGN_LEFT | RT_VALIGN_TOP| RT_WRAP, text = 0,color=0x555555), # index 0 is the name
				])
			},
			"fonts": [gFont("Regular", 19),gFont("Regular", 14),gFont("Regular", 19)],
			"itemHeight": 500
		}
		</convert>
    </widget>
    <widget name="author" position="71,161" size="400,25" zPosition="10" font="Regular;21" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget name="duration" position="378,161" size="346,25" zPosition="10" font="Regular;21" transparent="1" halign="right" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget name="published" position="71,186" size="400,25" zPosition="10" font="Regular;21" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget name="views" position="378,186" size="346,25" zPosition="10" font="Regular;21" transparent="1" halign="right" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget name="tags" position="71,213" size="653,25" zPosition="10" font="Regular;18" transparent="1" halign="left" valign="top" foregroundColor="#00777777" backgroundColor="#00ffffff" />
    <widget name="detailtext" position="71,255" size="652,345" zPosition="10" font="Regular;18" transparent="1" halign="left" valign="top" foregroundColor="#00000000" backgroundColor="#00ffffff" />
    <ePixmap position="46,668" zPosition="4" size="35,25" pixmap="~/img/red.png" transparent="1" alphatest="on" />
    <widget name="key_red" position="80,668" zPosition="5" size="211,20" valign="center" halign="left" font="Regular; 16" transparent="1" backgroundColor="#00000000" foregroundColor="#00ffffff" shadowColor="#00000000" shadowOffset="-1,-1" />
    <widget name="thumbnail" position="921,124" size="160,120" alphatest="on" zPosition="11" /> # fake entry for dynamic thumbnail resizing, currently there is no other way doing this.
	<ePixmap position="1081,44" size="169,79" zPosition="4" pixmap="~/img/youtubelogo-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" /><ePixmap name="bizq" position="36,111" size="711,38" pixmap="~/img/titulov-fs8.png" alphatest="blend" /><ePixmap name="izq" position="36,89" size="723,535" pixmap="~/img/bordev-fs8.png" alphatest="blend" zPosition="1" /><ePixmap position="1111,652" size="142,61" zPosition="4" pixmap="~/img/logospaze-fs8.png" alphatest="blend" transparent="1" /><eLabel name="linea1" position="741,114" size="539,1" backgroundColor="#00cccccc" /><eLabel name="linea2" position="741,614" size="539,1" backgroundColor="#00cccccc" /><ePixmap pixmap="~/img/info.png" position="67,105" zPosition="14" size="35,25" alphatest="blend" transparent="1" />
	</screen>"""

skinMyTubeVideoHelpScreen = """
		<screen name="MyTubeVideoHelpScreen" flags="wfBorder" position="center,center" size="720,576" title="MyTube - Help">
			
			<widget name="title" position="60,50" size="600,50" zPosition="5" valign="center" halign="left" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
			<widget name="detailtext" position="60,120" size="610,370" zPosition="10" font="Regular;21" transparent="1" halign="left" valign="top" />
			<ePixmap position="100,500" size="100,40" zPosition="0" pixmap="~/img/plugin.png" alphatest="on" transparent="1" />
			<ePixmap position="220,500" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="220,500" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
		</screen>"""

skinMyTubePlayer = """<screen name="MyTubePlayer" flags="wfNoBorder" position="0,580" size="1281,154" title="MyTube - Player" backgroundColor="#ff000000">
	<eLabel name="lineafondo" position="0,21" size="1281,1" backgroundColor="#00444444" zPosition="11" />
    <ePixmap position="1166,31" size="70,27" zPosition="4" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/youtubev-fs8.png" alphatest="blend" transparent="1" name="youtubelogo" />
    <widget source="session.CurrentService" zPosition="5" render="Label" position="107,28" size="939,30" font="Regular;20" backgroundColor="#00ffffff" foregroundColor="#00990000" transparent="1">
      <convert type="ServiceName">Name</convert>
    </widget>
    <widget source="session.CurrentService" render="Label" position="585,55" size="90,20" font="Regular; 16" halign="center" backgroundColor="#00ffffff" foregroundColor="#00333333" shadowColor="#cecece" shadowOffset="-1,-1" transparent="1">
      <convert type="ServicePosition">Length</convert>
    </widget>
    <widget source="session.CurrentService" render="Label" position="280,68" size="100,20" font="Regular;18" halign="right" valign="center" backgroundColor="#00ffffff" foregroundColor="#00333333" shadowColor="#cecece" shadowOffset="-1,-1" transparent="1">
      <convert type="ServicePosition">Position</convert>
    </widget>
    <widget source="session.CurrentService" render="PositionGauge" position="384,74" size="510,10" zPosition="2" pointer="skin_default/position_pointer.png:540,0" transparent="1" foregroundColor="#00000000">
      <convert type="ServicePosition">Gauge</convert>
    </widget>
    <widget source="session.CurrentService" render="Label" position="899,68" size="100,20" font="Regular;18" halign="left" valign="center" backgroundColor="#00ffffff" foregroundColor="#00333333" shadowColor="#cecece" shadowOffset="-1,-1" transparent="1">
      <convert type="ServicePosition">Remaining</convert>
    </widget>
    <eLabel name="new eLabel" position="384,76" size="510,5" zPosition="1" backgroundColor="#00cccccc" />
    <ePixmap name="new ePixmap" position="44,15" size="64,64" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyTube/img/nmcfs8.png" alphatest="blend" zPosition="10" />
    <eLabel name="fondoblanco" position="0,21" size="1280,131" backgroundColor="#10ffffff" zPosition="-10" />
  </screen>"""
  
# ~/img/ ~/img/
