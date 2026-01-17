"""Enthält ein Dictionary mit IDs als Schlüssel und Dictionaries als Werte, in denen der Hochschulname der Schlüssel und der Kurzname der Wert ist.

Im Dashboard wird der Kurzname ausgelesen, wenn der Hochschulname einen Schwellwert an Zeichen überschreibt.

Quelle:
Stiftung zur Förderung der Hochschulrektorenkonferenz. (n.d.). Alle Hochschulen als TXT-Datei.
Hochschulkompass.de. https://hs-kompass.de/kompass/xml/download/hs_liste.txt
"""

hs_dict_kurz = {
    0: {"": ""},
    1: {"AKAD Hochschule Stuttgart - staatlich anerkannt": "Stuttgart AKAD"},
    2: {"APOLLON Hochschule der Gesundheitswirtschaft": "Bremen FernFH"},
    3: {"Akademie der Bildenden Künste München": "München AkdBK"},
    4: {"Akademie der Bildenden Künste Nürnberg": "Nürnberg AkdBK"},
    5: {"Akademie der Polizei Hamburg": "Hamburg AkPol (Verw)"},
    6: {"Akkon-Hochschule": "Berlin Akkon"},
    7: {"Alanus Hochschule für Kunst und Gesellschaft": "Alfter HfKuG"},
    8: {"Albert-Ludwigs-Universität Freiburg im Breisgau": "Freiburg U"},
    9: {"Alice Salomon Hochschule Berlin": "Berlin ASH"},
    10: {
        "Allensbach Hochschule Konstanz,  staatlich anerkannte Hochschule der European Education Group GmbH": "Konstanz AllensbachH"
    },
    11: {
        "Archivschule Marburg - Hochschule für Archivwissenschaft": "Marburg HArchiv (Verw)"
    },
    12: {"Augustana-Hochschule Neuendettelsau": "Neuendettelsau KiH"},
    13: {
        "BSP Business and Law School - Hochschule für Management und Recht": "Berlin BSP"
    },
    14: {"Bard College Berlin, A Liberal Arts University": "Berlin BC"},
    15: {"Barenboim-Said Akademie": "Berlin BSA"},
    16: {"Bauhaus-Universität Weimar": "Weimar U"},
    17: {"Bergische Universität Wuppertal": "Wuppertal U"},
    18: {"Berlin International University of Applied Sciences": "Berlin BIU"},
    19: {"Berliner Hochschule für Technik": "Berlin BHT"},
    20: {"Berufliche Hochschule Hamburg (BHH)": "Hamburg BHH"},
    21: {"Brand University of Applied Sciences": "Hamburg FHBrand"},
    22: {
        "Brandenburgische Technische Universität Cottbus-Senftenberg": "Cottbus-Senftenberg TU"
    },
    23: {"Bucerius Law School, Hochschule für Rechtswissenschaft": "Hamburg BLS"},
    24: {"Burg Giebichenstein Kunsthochschule Halle": "Halle KuH"},
    25: {
        "CBS International Business School - University of Applied Sciences": "Köln CBS"
    },
    26: {"CODE University of Applied Sciences": "Berlin CODE"},
    27: {"CVJM-Hochschule": "Kassel CVJM"},
    28: {"Carl von Ossietzky Universität Oldenburg": "Oldenburg U"},
    29: {"Charlotte Fresenius Hochschule": "Wiesbaden CFH"},
    30: {"Christian-Albrechts-Universität zu Kiel": "Kiel U"},
    31: {"Constructor University": "Bremen CU"},
    32: {"DHGS Deutsche Hochschule für Gesundheit und Sport": "Berlin DHGS"},
    33: {"DIPLOMA Hochschule - Private Fachhochschule Nordhessen": "Nordhessen FH"},
    34: {"DIU - Dresden International University GmbH": "Dresden DIU"},
    35: {"Deutsche Hochschule der Polizei": "Münster DHPol (Verw)"},
    36: {
        "Deutsche Hochschule für Angewandte Wissenschaften - German University of Applied Sciences": "Potsdam DtH"
    },
    37: {
        "Deutsche Hochschule für Prävention und Gesundheitsmanagement GmbH": "Saarbrücken DHfPG"
    },
    38: {"Deutsche Sporthochschule Köln": "Köln DSHS"},
    39: {"Deutsche Universität für Verwaltungswissenschaften Speyer": "Speyer DUV"},
    40: {"Digital Business University of Applied Sciences": "Berlin DBU"},
    41: {"Duale Hochschule Baden-Württemberg": "Baden-Württemberg DH"},
    42: {"Duale Hochschule Gera-Eisenach": "Gera-Eisenach DH"},
    43: {"Duale Hochschule Sachsen": "Sachsen DH"},
    44: {
        "Duale Hochschule Schleswig-Holstein - staatlich anerkannte Hochschule für angewandte Wissenschaften in Trägerschaft der Wirtschaftsakademie Schleswig-Holstein": "Schleswig-Holstein DHSH"
    },
    45: {"EBS Universität für Wirtschaft und Recht": "Wiesbaden EBS"},
    46: {"EBZ Business School - University of Applied Sciences": "Bochum EBZ"},
    47: {
        "EHIP - Europäische Hochschule für Innovation und Perspektive": "Backnang EHIP"
    },
    48: {"ESCP Europe Wirtschaftshochschule Berlin e.V.": "Berlin ESCP"},
    49: {"ESMT European School of Management and Technology": "Berlin ESMT"},
    50: {"Eberhard Karls Universität Tübingen": "Tübingen U"},
    51: {"Ernst-Abbe-Hochschule Jena": "Jena H"},
    52: {"Europa-Universität Flensburg": "Flensburg U"},
    53: {"Europa-Universität Viadrina Frankfurt (Oder)": "Frankfurt (Oder) U"},
    54: {
        "Europäische Fachhochschule Rhein/Erft, european university of applied sciences": "Köln EUFH"
    },
    55: {"Europäische Fernhochschule Hamburg": "Hamburg EFH"},
    56: {"Evangelische Hochschule Berlin": "Berlin EvH"},
    57: {
        "Evangelische Hochschule Darmstadt (staatlich anerkannt) - Kirchliche Körperschaft des öffentlichen Rechts": "Darmstadt EvH"
    },
    58: {"Evangelische Hochschule Dresden": "Dresden EvH"},
    59: {
        "Evangelische Hochschule Freiburg, staatlich anerkannte Hochschule der Evangelischen Landeskirche in Baden": "Freiburg EvHS"
    },
    60: {
        "Evangelische Hochschule Ludwigsburg - staatlich anerkannte Hochschule für Angewandte Wissenschaften der Evangelischen Landeskirche Württemberg": "Ludwigsburg EvH"
    },
    61: {
        "Evangelische Hochschule Rheinland-Westfalen-Lippe": "Bochum Rheinland-Westfalen-Lippe EvH"
    },
    62: {"Evangelische Hochschule Tabor": "Marburg EHTabor"},
    63: {"Evangelische Hochschule für Kirchenmusik": "Halle HfKiM"},
    64: {"Evangelische Hochschule für Soziale Arbeit & Diakonie": "Hamburg EvH"},
    65: {
        "Evangelische Hochschule für angewandte Wissenschaften - Evangelische Fachhochschule Nürnberg": "Nürnberg EvH"
    },
    66: {"FH Münster - University of Applied Sciences": "Münster FH"},
    67: {
        "FOM Hochschule für Oekonomie & Management - University of Applied Sciences": "Essen FOM"
    },
    68: {"Fachhochschule Aachen": "Aachen FH"},
    69: {"Fachhochschule Dortmund": "Dortmund FH"},
    70: {"Fachhochschule Dresden": "Dresden PFH"},
    71: {"Fachhochschule Erfurt": "Erfurt FH"},
    72: {"Fachhochschule Kiel": "Kiel FH"},
    73: {"Fachhochschule Polizei Sachsen-Anhalt": "Sachsen-Anhalt FHPol (Verw)"},
    74: {"Fachhochschule Potsdam": "Potsdam FH"},
    75: {"Fachhochschule Südwestfalen": "Südwestfalen FH"},
    76: {"Fachhochschule Wedel": "Wedel FH"},
    77: {
        "Fachhochschule Westküste, Hochschule für Wirtschaft und Technik": "Westküste FH"
    },
    78: {
        "Fachhochschule der Diakonie - Diaconia - University of Applied Sciences": "Bielefeld FHDiakonie"
    },
    79: {"Fachhochschule der Verwaltung des Saarlandes": "Saarland FHVerw (Verw)"},
    80: {"Fachhochschule der Wirtschaft": "Paderborn FHDW"},
    81: {"Fachhochschule des Mittelstands (FHM)": "Bielefeld FHM"},
    82: {"Fachhochschule für Finanzen Brandenburg": "Brandenburg FHFinanz (Verw)"},
    83: {
        "Fachhochschule für Interkulturelle Theologie Hermannsburg": "Hermannsburg FIT"
    },
    84: {
        "Fachhochschule für Rechtspflege Nordrhein-Westfalen": "Nordrhein-Westfalen FHRecht (Verw)"
    },
    85: {"Fachhochschule für Sport und Management Potsdam": "Potsdam FHSport"},
    86: {
        "Fachhochschule für Verwaltung und Dienstleistung in Schleswig-Holstein": "Schleswig-Holstein FHVD (Verw)"
    },
    87: {"Fachhochschule für die Wirtschaft Hannover": "Hannover FHDW"},
    88: {
        "Fachhochschule für öffentliche Verwaltung, Polizei und Rechtspflege des Landes Mecklenburg-Vorpommern": "Mecklenburg-Vorp. FHVerw (Verw)"
    },
    89: {"FernUniversität in Hagen": "Hagen FernU"},
    90: {"Filmuniversität Babelsberg Konrad Wolf": "Potsdam-Babelsberg FilmU"},
    91: {"Fliedner Fachhochschule Düsseldorf": "Düsseldorf FliednerFH"},
    92: {"Folkwang Universität der Künste": "Essen UdK"},
    93: {"Frankfurt School of Finance & Management": "Frankfurt am Main FSFM"},
    94: {"Frankfurt University of Applied Sciences": "Frankfurt am Main FH"},
    95: {
        "Freie Hochschule Stuttgart - Seminar für Waldorfpädagogik. Staatlich anerkannte wissenschaftliche Hochschule.": "Stuttgart U Waldorf"
    },
    96: {"Freie Theologische Hochschule Gießen": "Giessen FThH"},
    97: {"Freie Universität Berlin": "Berlin FU"},
    98: {"Friedrich-Alexander-Universität Erlangen-Nürnberg": "Erlangen-Nürnberg U"},
    99: {"Friedrich-Schiller-Universität Jena": "Jena U"},
    100: {"Georg-August-Universität Göttingen": "Göttingen U"},
    101: {"German International University": "Berlin GIU"},
    102: {"Gisma University of Applied Sciences": "Potsdam GISMA"},
    103: {"Gottfried Wilhelm Leibniz Universität Hannover": "Hannover U"},
    104: {
        "HAWK Hochschule für angewandte Wissenschaft und Kunst Hildesheim/Holzminden/Göttingen": "Hildesh./Holzm./Göttingen H"
    },
    105: {"HHL Leipzig Graduate School of Management": "Leipzig HHL"},
    106: {"HMU Health and Medical University": "Erfurt HMU"},
    107: {"HMU Health and Medical University Potsdam": "Potsdam HMU"},
    108: {"HSBA Hamburg School of Business Administration": "Hamburg HSBA"},
    109: {"HSD Hochschule Döpfer": "Potsdam HSD"},
    110: {"HafenCity Universität Hamburg": "Hamburg HCU"},
    111: {"Hamburger Fern-Hochschule, gemeinnützige GmbH": "Hamburg FernH"},
    112: {"Heinrich-Heine-Universität Düsseldorf": "Düsseldorf U"},
    113: {
        "Helmut-Schmidt-Universität/Universität der Bundeswehr Hamburg": "Hamburg UBw"
    },
    114: {"Hertie School": "Berlin Hertie"},
    115: {
        "Hessische Hochschule für Finanzen und Rechtspflege Rotenburg a.d. Fulda": "Hessen HFinanz/Recht (Verw)"
    },
    116: {
        "Hessische Hochschule für öffentliches Management und Sicherheit": "Hessen HOeffManagement(Verw)"
    },
    117: {"Hochschule Aalen - Technik, Wirtschaft und Gesundheit": "Aalen H"},
    118: {"Hochschule Albstadt-Sigmaringen": "Albstadt-Sigmaringen H"},
    119: {"Hochschule Anhalt - Anhalt University of Applied Sciences": "Anhalt H"},
    120: {
        "Hochschule Biberach - Architektur und Bauwesen, Betriebswirtschaft und Biotechnologie": "Biberach H"
    },
    121: {
        "Hochschule Bielefeld - University of Applied Sciences and Arts (HSBI)": "Bielefeld H"
    },
    122: {"Hochschule Bochum": "Bochum H"},
    123: {
        "Hochschule Bonn-Rhein-Sieg, University of Applied Sciences": "Bonn-Rhein-Sieg H"
    },
    124: {
        "Hochschule Braunschweig/Wolfenbüttel, Ostfalia Hochschule für angewandte Wissenschaften": "Ostfalia H"
    },
    125: {"Hochschule Bremen": "Bremen H"},
    126: {"Hochschule Bremerhaven": "Bremerhaven H"},
    127: {"Hochschule Darmstadt": "Darmstadt H"},
    128: {"Hochschule Düsseldorf": "Düsseldorf H"},
    129: {"Hochschule Emden/Leer": "Emden/Leer H"},
    130: {"Hochschule Esslingen": "Esslingen H"},
    131: {"Hochschule Flensburg": "Flensburg H"},
    132: {"Hochschule Fresenius": "Idstein HFresen"},
    133: {
        "Hochschule Fresenius Heidelberg - staatlich anerkannte Hochschule der Hochschule Fresenius für Internationales Management GmbH": "Heidelberg HFresen"
    },
    134: {"Hochschule Fulda - University of Applied Sciences": "Fulda H"},
    135: {
        "Hochschule Furtwangen - Informatik, Technik, Wirtschaft, Medien, Gesundheit": "Furtwangen H"
    },
    136: {"Hochschule Geisenheim": "Geisenheim H"},
    137: {"Hochschule Hamm-Lippstadt": "Hamm-Lippstadt H"},
    138: {"Hochschule Hannover": "Hannover H"},
    139: {"Hochschule Harz, Hochschule für angewandte Wissenschaften (FH)": "Harz H"},
    140: {"Hochschule Heilbronn, Technik, Wirtschaft, Informatik": "Heilbronn H"},
    141: {
        "Hochschule Kaiserslautern (University of Applied Sciences)": "Kaiserslautern H"
    },
    142: {"Hochschule Karlsruhe - Technik und Wirtschaft": "Karlsruhe H"},
    143: {"Hochschule Koblenz": "Koblenz H"},
    144: {"Hochschule Konstanz Technik, Wirtschaft und Gestaltung": "Konstanz H"},
    145: {
        "Hochschule Landshut - Hochschule für angewandte Wissenschaften": "Landshut H"
    },
    146: {
        "Hochschule Macromedia - staatlich anerkannte Hochschule für angewandte Wissenschaften der Macromedia GmbH mit Sitz in Stuttgart": "Stuttgart MAW"
    },
    147: {"Hochschule Magdeburg-Stendal": "Magdeburg-Stendal H"},
    148: {"Hochschule Mainz": "Mainz H"},
    149: {"Hochschule Merseburg": "Merseburg H"},
    150: {"Hochschule Mittweida, University of Applied Sciences": "Mittweida H"},
    151: {
        "Hochschule Neubrandenburg - University of Applied Sciences": "Neubrandenburg H"
    },
    152: {"Hochschule Niederrhein": "Niederrhein H"},
    153: {"Hochschule Nordhausen": "Nordhausen H"},
    154: {"Hochschule Osnabrück": "Osnabrück H"},
    155: {
        "Hochschule Pforzheim - Gestaltung, Technik, Wirtschaft und Recht": "Pforzheim H"
    },
    156: {"Hochschule Ravensburg-Weingarten": "Ravensburg-Weingarten H"},
    157: {
        "Hochschule Reutlingen, Hochschule für Technik-  Wirtschaft-Informatik-Design": "Reutlingen HTWID"
    },
    158: {"Hochschule Rhein-Waal - University of Applied Sciences": "Rhein-Waal H"},
    159: {"Hochschule RheinMain": "RheinMain H"},
    160: {"Hochschule Ruhr West- University of Applied Sciences": "Ruhr West H"},
    161: {"Hochschule Schmalkalden": "Schmalkalden H"},
    162: {"Hochschule Stralsund": "Stralsund H"},
    163: {"Hochschule Trier - Trier University of Applied Sciences": "Trier H"},
    164: {"Hochschule Weserbergland": "Weserbergland H"},
    165: {
        "Hochschule Wismar - University of Applied Sciences: Technology, Business and Design": "Wismar H"
    },
    166: {"Hochschule Worms, University of Applied Sciences": "Worms H"},
    167: {"Hochschule Zittau/Görlitz": "Zittau/ Görlitz H"},
    168: {
        "Hochschule der Bayerischen Wirtschaft für angewandte Wissenschaften - HDBW": "München HDBW"
    },
    169: {"Hochschule der Bildenden Künste Saar": "Saar HBK"},
    170: {
        "Hochschule der Bundesagentur für Arbeit - Staatlich anerkannte Hochschule für angewandte Wissenschaft in Mannheim und Schwerin (University of Applied Labour Studies of the Federal Employment Agency)": "Mannheim HdBA (Verw)"
    },
    171: {"Hochschule der Deutschen Bundesbank": "Hachenburg HBundesbank (Verw)"},
    172: {"Hochschule der Medien Stuttgart": "Stuttgart HdM"},
    173: {"Hochschule der Polizei Brandenburg": "Brandenburg HPol (Verw)"},
    174: {"Hochschule der Polizei Rheinland-Pfalz": "Rheinland-Pfalz HPol (Verw)"},
    175: {"Hochschule der Wirtschaft für Management": "Mannheim HdWM"},
    176: {"Hochschule der bildenden Künste (HBK) Essen": "Essen HBK"},
    177: {"Hochschule des Bundes für öffentliche Verwaltung": "Brühl HSBund (Verw)"},
    178: {"Hochschule für Angewandte Wissenschaften Hamburg": "Hamburg HAW"},
    179: {"Hochschule für Bildende Künste (Städelschule)": "Frankfurt am Main HfBK"},
    180: {"Hochschule für Bildende Künste Braunschweig": "Braunschweig HBK"},
    181: {"Hochschule für Bildende Künste Dresden": "Dresden HfBK"},
    182: {"Hochschule für Bildende Künste Hamburg": "Hamburg HfBK"},
    183: {"Hochschule für Fernsehen und Film München": "München HFF"},
    184: {"Hochschule für Finanzen NRW": "Nordrhein-Westfalen HFinanz (Verw)"},
    185: {"Hochschule für Finanzen Rheinland-Pfalz": "Rheinland-Pfalz HFinanz (Verw)"},
    186: {"Hochschule für Finanzwirtschaft & Management": "Bonn HFinMan"},
    187: {"Hochschule für Forstwirtschaft Rottenburg": "Rottenburg H"},
    188: {"Hochschule für Gesellschaftsgestaltung": "Koblenz HfG"},
    189: {"Hochschule für Gestaltung Offenbach": "Offenbach HfGest"},
    190: {"Hochschule für Gestaltung Schwäbisch Gmünd": "Schwäbisch Gmünd HGest"},
    191: {
        "Hochschule für Gesundheitsfachberufe Eberswalde": "Eberswalde FH Gesundheit"
    },
    192: {"Hochschule für Grafik und Buchkunst Leipzig": "Leipzig HfGuB"},
    193: {"Hochschule für Jüdische Studien Heidelberg": "Heidelberg HfJS"},
    194: {
        "Hochschule für Katholische Kirchenmusik und Musikpädagogik": "Regensburg HfKiM"
    },
    195: {
        "Hochschule für Kirchenmusik der Diözese Rottenburg-Stuttgart": "Rottenburg HfKiM"
    },
    196: {
        "Hochschule für Kirchenmusik der Evangelisch-Lutherischen Landeskirche Sachsens": "Dresden HfKiM"
    },
    197: {
        "Hochschule für Kirchenmusik der Evangelischen Kirche von Westfalen": "Witten HfKiM"
    },
    198: {
        "Hochschule für Kirchenmusik der Evangelischen Landeskirche in Baden": "Heidelberg HfKiM"
    },
    199: {
        "Hochschule für Kirchenmusik der Evangelischen Landeskirche in Württemberg": "Tübingen HfKiM"
    },
    200: {"Hochschule für Kommunikation und Gestaltung": "Stuttgart HfK+G"},
    201: {"Hochschule für Künste Bremen": "Bremen HfK"},
    202: {"Hochschule für Künste im Sozialen, Ottersberg": "Ottersberg H"},
    203: {"Hochschule für Musik Carl Maria von Weber Dresden": "Dresden HfM"},
    204: {"Hochschule für Musik Detmold": "Detmold HfM"},
    205: {"Hochschule für Musik Franz Liszt Weimar": "Weimar HfM"},
    206: {"Hochschule für Musik Freiburg im Breisgau": "Freiburg HfM"},
    207: {"Hochschule für Musik Hanns Eisler Berlin": "Berlin HfM"},
    208: {"Hochschule für Musik Karlsruhe": "Karlsruhe HfM"},
    209: {"Hochschule für Musik Nürnberg": "Nürnberg HfM"},
    210: {"Hochschule für Musik Saar": "Saarbrücken HfM"},
    211: {"Hochschule für Musik Würzburg": "Würzburg HfM"},
    212: {
        "Hochschule für Musik und Darstellende Kunst Frankfurt am Main": "Frankfurt am Main HfM"
    },
    213: {"Hochschule für Musik und Tanz Köln": "Köln HfMT"},
    214: {
        "Hochschule für Musik und Theater Felix Mendelssohn Bartholdy Leipzig": "Leipzig HMT"
    },
    215: {"Hochschule für Musik und Theater Hamburg": "Hamburg HfM"},
    216: {"Hochschule für Musik und Theater München": "München HMT"},
    217: {"Hochschule für Musik und Theater Rostock": "Rostock HMT"},
    218: {"Hochschule für Musik, Theater und Medien Hannover": "Hannover HfMTM"},
    219: {"Hochschule für Philosophie": "München HPhil"},
    220: {"Hochschule für Polizei Baden-Württemberg": "Baden-Württemberg HfPol (Verw)"},
    221: {
        "Hochschule für Polizei und öffentliche Verwaltung Nordrhein-Westfalen": "Nordrhein-Westfalen HSPV (Verw)"
    },
    222: {
        "Hochschule für Rechtspflege Schwetzingen": "Baden-Württemberg HRecht (Verw)"
    },
    223: {"Hochschule für Schauspielkunst Ernst Busch": "Berlin HfS"},
    224: {
        "Hochschule für Soziale Arbeit und Pädagogik (HSAP) gemeinnützige Betriebsgesellschaft mbH": "Berlin HSAP"
    },
    225: {"Hochschule für Technik Stuttgart": "Stuttgart H"},
    226: {"Hochschule für Technik und Wirtschaft Berlin": "Berlin HTW"},
    227: {
        "Hochschule für Technik und Wirtschaft Dresden - University of Applied Sciences": "Dresden HTW"
    },
    228: {"Hochschule für Technik und Wirtschaft des Saarlandes": "Saarbrücken HTW"},
    229: {"Hochschule für Technik, Wirtschaft und Kultur Leipzig": "Leipzig HTWK"},
    230: {"Hochschule für Technik, Wirtschaft und Medien Offenburg": "Offenburg H"},
    231: {
        "Hochschule für Wirtschaft und Gesellschaft Ludwigshafen ": "Ludwigshafen HWG"
    },
    232: {"Hochschule für Wirtschaft und Recht Berlin": "Berlin HWR"},
    233: {
        "Hochschule für Wirtschaft und Umwelt Nürtingen-Geislingen": "Nürtingen-Geislingen H"
    },
    234: {"Hochschule für angewandte Wissenschaften Ansbach": "Ansbach H"},
    235: {"Hochschule für angewandte Wissenschaften Coburg": "Coburg H"},
    236: {"Hochschule für angewandte Wissenschaften Hof": "Hof H"},
    237: {"Hochschule für angewandte Wissenschaften Kempten": "Kempten H"},
    238: {"Hochschule für angewandte Wissenschaften München": "München HAW"},
    239: {"Hochschule für angewandte Wissenschaften Neu-Ulm": "Neu-Ulm H"},
    240: {
        "Hochschule für angewandte Wissenschaften Weihenstephan-Triesdorf": "Weihenstephan-Triesdorf H"
    },
    241: {"Hochschule für angewandtes Management": "Ismaning HAM"},
    242: {"Hochschule für den öffentlichen Dienst in Bayern": "Bayern HföD (Verw)"},
    243: {
        "Hochschule für evangelische Kirchenmusik der Evangelisch-Lutherischen Kirche in Bayern": "Bayreuth HfKiM"
    },
    244: {"Hochschule für nachhaltige Entwicklung Eberswalde": "Eberswalde H"},
    245: {"Hochschule für Öffentliche Verwaltung Bremen": "Bremen VerwH (Verw)"},
    246: {
        "Hochschule für öffentliche Verwaltung Kehl": "Baden-Württemberg HVerw (Verw)"
    },
    247: {
        "Hochschule für öffentliche Verwaltung Rheinland-Pfalz": "Rheinland-Pfalz HVerw (Verw)"
    },
    248: {
        "Hochschule für öffentliche Verwaltung und Finanzen Ludwigsburg": "Baden-Württemberg HVerw/Finanzen(Verw)"
    },
    249: {
        "Hochschule für öffentliche Verwaltung und Rechtspflege (FH), Fortbildungszentrum des Freistaates Sachsen (HSF)": "Sachsen HVerw (VerwH)"
    },
    250: {"Humboldt-Universität zu Berlin": "Berlin HU"},
    251: {"IB Hochschule für Gesundheit und Soziales": "Berlin IB"},
    252: {"INU - Innovative University of Applied Sciences": "Köln INU"},
    253: {"IST-Hochschule für Management": "Düsseldorf IST"},
    254: {"IU Internationale Hochschule": "Erfurt IU"},
    255: {"International Psychoanalytic University Berlin": "Berlin IPU"},
    256: {"International School of Management": "Dortmund ISM"},
    257: {"Internationale Hochschule Liebenzell (IHL)": "Bad Liebenzell IHL"},
    258: {
        "Internationale Hochschule SDI München - Hochschule für angewandte Wissenschaften": "München IH"
    },
    259: {
        "Jade Hochschule -  Wilhelmshaven/Oldenburg/Elsfleth": "Wilhelmshaven/Oldenburg/Elsfleth H"
    },
    260: {
        "Johann Wolfgang Goethe-Universität, Frankfurt am Main": "Frankfurt am Main U"
    },
    261: {"Johannes Gutenberg-Universität Mainz": "Mainz U"},
    262: {"Julius-Maximilians-Universität Würzburg": "Würzburg U"},
    263: {"Justus-Liebig-Universität Gießen": "Giessen U"},
    264: {
        "Karlshochschule International University - staatlich anerkannte Hochschule der Karlshochschule gemeinnützige GmbH Karlsruhe": "Karlsruhe KIU"
    },
    265: {"Karlsruher Institut für Technologie": "Karlsruhe U KIT"},
    266: {
        "Katholische    Stiftungshochschule für   angewandte Wissenschaften München - Hochschule der Kirchlichen Stiftung des öffentlichen Rechts Katholische Bildungsstätten für Sozialberufe in Bayern": "München KathH"
    },
    267: {
        "Katholische Hochschule Freiburg, staatlich anerkannte Hochschule - Catholic University of Applied Sciences": "Freiburg KathHS"
    },
    268: {
        "Katholische Hochschule Mainz Catholic University of Applied Sciences": "Mainz KathH"
    },
    269: {
        "Katholische Hochschule Nordrhein-Westfalen - Catholic University of Applied Sciences": "Nordrhein-Westfalen KathH"
    },
    270: {
        "Katholische Hochschule für Sozialwesen Berlin (KHSB) - Staatlich anerkannte Fachhochschule für Sozialwesen": "Berlin KHS"
    },
    271: {"Katholische Universität Eichstätt - Ingolstadt": "Eichstätt - Ingolstadt U"},
    272: {"Kirchliche Hochschule Wuppertal": "Wuppertal KiH"},
    273: {"Kolping Hochschule": "Köln KolpingH"},
    274: {
        "Kommunale Hochschule für Verwaltung in Niedersachsen": "Niedersachsen HVerw (Verw)"
    },
    275: {"Kunstakademie Düsseldorf": "Düsseldorf KuAk"},
    276: {"Kunstakademie Münster, Hochschule für Bildende Künste": "Münster KuAk"},
    277: {"Kunsthochschule für Medien Köln": "Köln KuHMedien"},
    278: {"Kölner Hochschule für Katholische Theologie (KHKT)": "Köln KHKT"},
    279: {
        "Kühne Logistics University - Wissenschaftliche Hochschule für Logistik und Unternehmensführung": "Hamburg KLU"
    },
    280: {"Leibniz-Fachhochschule": "Hannover LeibnizFH"},
    281: {"Leuphana Universität Lüneburg": "Lüneburg U"},
    282: {"Ludwig-Maximilians-Universität München": "München U"},
    283: {"Lutherische Theologische Hochschule Oberursel": "Oberursel LuthThH"},
    284: {
        "MSH Medical School Hamburg - University of Applied Sciences and Medical University": "Hamburg MSH"
    },
    285: {"MU Media University of Applied Sciences": "Berlin MU"},
    286: {"Martin-Luther-Universität Halle-Wittenberg": "Halle-Wittenberg U"},
    287: {"Mediadesign Hochschule für Design und Informatik": "Berlin MDH"},
    288: {
        "Medical School Berlin - Hochschule für Gesundheit und Medizin (MSB)": "Berlin MSB"
    },
    289: {"Medizinische Hochschule Brandenburg Theodor Fontane": "Neuruppin MHB"},
    290: {"Medizinische Hochschule Hannover (MHH)": "Hannover MedH"},
    291: {
        "Merz Akademie Hochschule für Gestaltung, Kunst und Medien, Stuttgart - Staatlich anerkannt": "Stuttgart MerzAk"
    },
    292: {
        "Munich Business School - Staatlich anerkannte private Fachhochschule": "München MBS"
    },
    293: {"Musikhochschule Lübeck": "Lübeck HfM"},
    294: {"Muthesius Kunsthochschule": "Kiel KuH"},
    295: {
        "NBS Northern Business School - University of Applied Sciences": "Hamburg NBS"
    },
    296: {"NORDAKADEMIE Hochschule der Wirtschaft": "Elmshorn FH Nordakademie"},
    297: {
        "Norddeutsche Akademie für Finanzen und Steuerrecht": "Hamburg AkFinanz (Verw)"
    },
    298: {
        "Norddeutsche Hochschule für Rechtspflege - Niedersachsen": "Niedersachsen HRecht (Verw)"
    },
    299: {"Ostbayerische Technische Hochschule Amberg-Weiden": "Amberg-Weiden OTH"},
    300: {"Ostbayerische Technische Hochschule Regensburg": "Regensburg OTH"},
    301: {"Otto-Friedrich-Universität Bamberg": "Bamberg U"},
    302: {"Otto-von-Guericke-Universität Magdeburg": "Magdeburg U"},
    303: {"PFH - Private Hochschule Göttingen": "Göttingen PFH"},
    304: {"Palucca Hochschule für Tanz Dresden": "Dresden HfTanz"},
    305: {"Philipps-Universität Marburg": "Marburg U"},
    306: {
        "Philosophisch-Theologische Hochschule Münster - Kirchlich und staatlich anerkannte Hochschule in Trägerschaft der PTH Philosophisch-Theologische Hochschule Münster gemeinnützige GmbH": "Münster PhThH"
    },
    307: {
        "Philosophisch-Theologische Hochschule Sankt Georgen Frankfurt am Main": "Frankfurt am Main PhThH"
    },
    308: {"Polizeiakademie Niedersachsen": "Niedersachsen PolAk (Verw)"},
    309: {
        "Private Hochschule für Wirtschaft und Technik Vechta/Diepholz": "Vechta/Diepholz PHWT"
    },
    310: {"Private Universität Witten/Herdecke gGmbH": "Witten/Herdecke U"},
    311: {
        "Provadis School of International Management and Technology": "Frankfurt am Main FHProvadis"
    },
    312: {"Psychologische Hochschule Berlin (PHB)": "Berlin PHB"},
    313: {"Pädagogische Hochschule Freiburg": "Freiburg PH"},
    314: {"Pädagogische Hochschule Heidelberg": "Heidelberg PH"},
    315: {"Pädagogische Hochschule Karlsruhe": "Karlsruhe PH"},
    316: {"Pädagogische Hochschule Ludwigsburg": "Ludwigsburg PH"},
    317: {"Pädagogische Hochschule Schwäbisch Gmünd": "Schwäbisch Gmünd PH"},
    318: {"Pädagogische Hochschule Weingarten": "Weingarten PH"},
    319: {"Quadriga Hochschule Berlin": "Berlin Quadriga"},
    320: {"Rheinisch-Westfälische Technische Hochschule Aachen": "Aachen TH"},
    321: {"Rheinische Friedrich-Wilhelms-Universität Bonn": "Bonn U"},
    322: {"Rheinische Hochschule Köln": "Köln RheinH"},
    323: {
        "Rheinland-Pfälzische Technische Universität Kaiserslautern-Landau": "Kaiserslautern-Landau RPTU"
    },
    324: {"Robert Schumann Hochschule Düsseldorf": "Düsseldorf HfM"},
    325: {"Ruhr-Universität Bochum": "Bochum U"},
    326: {"Ruprecht-Karls-Universität Heidelberg": "Heidelberg U"},
    327: {"SRH Fernhochschule - The Mobile University": "Riedlingen SRH"},
    328: {"SRH University of Applied Sciences Heidelberg": "Heidelberg SRH"},
    329: {"Staatliche Akademie der Bildenden Künste Karlsruhe": "Karlsruhe AkdBK"},
    330: {"Staatliche Akademie der Bildenden Künste Stuttgart": "Stuttgart AkdBK"},
    331: {"Staatliche Hochschule für Gestaltung Karlsruhe": "Karlsruhe HfGest"},
    332: {"Staatliche Hochschule für Musik Trossingen": "Trossingen HfM"},
    333: {
        "Staatliche Hochschule für Musik und Darstellende Kunst Mannheim": "Mannheim HfM"
    },
    334: {
        "Staatliche Hochschule für Musik und Darstellende Kunst Stuttgart": "Stuttgart HfM"
    },
    335: {"Steinbeis Hochschule": "Magdeburg SH"},
    336: {"Steuerakademie Niedersachsen": "Niedersachsen SteuerAk (Verw)"},
    337: {"Stiftung Tierärztliche Hochschule Hannover": "Hannover TiHo"},
    338: {"Technische Hochschule Aschaffenburg": "Aschaffenburg TH"},
    339: {"Technische Hochschule Augsburg": "Augsburg TH"},
    340: {"Technische Hochschule Bingen": "Bingen TH"},
    341: {"Technische Hochschule Brandenburg": "Brandenburg TH"},
    342: {"Technische Hochschule Deggendorf": "Deggendorf TH"},
    343: {"Technische Hochschule Georg Agricola": "Bochum TH"},
    344: {"Technische Hochschule Ingolstadt": "Ingolstadt TH"},
    345: {"Technische Hochschule Köln": "Köln TH"},
    346: {"Technische Hochschule Lübeck": "Lübeck TH"},
    347: {"Technische Hochschule Mannheim": "Mannheim TH"},
    348: {"Technische Hochschule Mittelhessen - THM": "Mittelhessen THM"},
    349: {"Technische Hochschule Nürnberg Georg Simon Ohm": "Nürnberg TH"},
    350: {"Technische Hochschule Ostwestfalen-Lippe": "Ostwestfalen-Lippe TH"},
    351: {"Technische Hochschule Rosenheim": "Rosenheim TH"},
    352: {"Technische Hochschule Ulm": "Ulm TH"},
    353: {"Technische Hochschule Wildau": "Wildau TH"},
    354: {"Technische Hochschule Würzburg-Schweinfurt": "Würzburg-Schweinfurt TH"},
    355: {"Technische Universität Bergakademie Freiberg": "Freiberg TUBergAk"},
    356: {"Technische Universität Berlin": "Berlin TU"},
    357: {"Technische Universität Braunschweig": "Braunschweig TU"},
    358: {"Technische Universität Chemnitz": "Chemnitz TU"},
    359: {"Technische Universität Clausthal": "Clausthal TU"},
    360: {"Technische Universität Darmstadt": "Darmstadt TU"},
    361: {"Technische Universität Dortmund": "Dortmund TU"},
    362: {"Technische Universität Dresden": "Dresden TU"},
    363: {"Technische Universität Hamburg": "Hamburg TU"},
    364: {"Technische Universität Ilmenau": "Ilmenau TU"},
    365: {"Technische Universität München": "München TUM"},
    366: {"Technische Universität Nürnberg": "Nürnberg TU"},
    367: {"Theologische Fakultät Fulda": "Fulda ThFak"},
    368: {"Theologische Fakultät Paderborn": "Paderborn ThFak"},
    369: {"Theologische Fakultät Trier": "Trier ThFak"},
    370: {"Theologische Hochschule Elstal": "Elstal ThH"},
    371: {"Theologische Hochschule Friedensau": "Friedensau ThH"},
    372: {
        "Theologische Hochschule Reutlingen - staatlich anerkannte Fachhochschule der Evangelisch-methodistischen Kirche": "Reutlingen ThH"
    },
    373: {"Theologisches Hochschule Ewersbach": "Ewersbach ThH"},
    374: {
        "Thüringer Fachhochschule für öffentliche Verwaltung": "Thüringen VerwH (Verw)"
    },
    375: {"Tomorrow University of Applied Sciences": "Frankfurt am Main ToU"},
    376: {"University of Europe for Applied Sciences": "Potsdam UE"},
    377: {"University of Labour": "Frankfurt am Main UoL"},
    378: {"Universität Augsburg": "Augsburg U"},
    379: {"Universität Bayreuth": "Bayreuth U"},
    380: {"Universität Bielefeld": "Bielefeld U"},
    381: {"Universität Bremen": "Bremen U"},
    382: {"Universität Duisburg-Essen": "Duisburg-Essen U"},
    383: {"Universität Erfurt": "Erfurt U"},
    384: {"Universität Greifswald": "Greifswald U"},
    385: {"Universität Hamburg": "Hamburg U"},
    386: {"Universität Hildesheim": "Hildesheim U"},
    387: {"Universität Hohenheim": "Hohenheim U"},
    388: {"Universität Kassel": "Kassel U"},
    389: {"Universität Koblenz": "Koblenz U"},
    390: {"Universität Konstanz": "Konstanz U"},
    391: {"Universität Leipzig": "Leipzig U"},
    392: {"Universität Mannheim": "Mannheim U"},
    393: {"Universität Münster": "Münster U"},
    394: {"Universität Osnabrück": "Osnabrück U"},
    395: {"Universität Paderborn": "Paderborn U"},
    396: {"Universität Passau": "Passau U"},
    397: {"Universität Potsdam": "Potsdam U"},
    398: {"Universität Regensburg": "Regensburg U"},
    399: {"Universität Rostock": "Rostock U"},
    400: {"Universität Siegen": "Siegen U"},
    401: {"Universität Stuttgart": "Stuttgart U"},
    402: {"Universität Trier": "Trier U"},
    403: {"Universität Ulm": "Ulm U"},
    404: {"Universität Vechta": "Vechta U"},
    405: {"Universität der Bundeswehr München": "München UBw"},
    406: {"Universität der Künste Berlin": "Berlin UdK"},
    407: {"Universität des Saarlandes": "Saarbrücken U"},
    408: {"Universität zu Köln": "Köln U"},
    409: {"Universität zu Lübeck": "Lübeck U"},
    410: {"VICTORIA | Internationale Hochschule": "Berlin VICTORIA"},
    411: {
        "Vinzenz Pallotti University - kirchlich und staatlich anerkannte wissenschaftliche Hochschule in freier Trägerschaft": "Vallendar VP-Uni"
    },
    412: {"WHU - Otto Beisheim School of Management": "Vallendar WHU"},
    413: {
        "Westfälische Hochschule Gelsenkirchen, Bocholt, Recklinghausen": "Westfälische H"
    },
    414: {"Westsächsische Hochschule Zwickau": "Zwickau H"},
    415: {"Wilhelm Büchner Hochschule": "Darmstadt WBH"},
    416: {"XU Exponential University of Applied Sciences": "Potsdam XU"},
    417: {
        "Zeppelin Universität - Hochschule zwischen Wirtschaft, Kultur und Politik": "Friedrichshafen ZU"
    },
    418: {"accadis Hochschule Bad Homburg": "Bad Homburg accadisFH"},
    419: {"bbw Hochschule": "Berlin bbw"},
    420: {"hochschule 21": "Buxtehude FH"},
    421: {"media Akademie - Hochschule Stuttgart": "Stuttgart MediaAk"},
    422: {"weißensee kunsthochschule berlin": "Berlin-Weißensee KHB"},
}
