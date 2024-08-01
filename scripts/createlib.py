#!/usr/bin/env python3
import sqlite3
import re
import operator
import sys
import importlib
import datetime

sys.path.append("kicad-library-utils/common")

import kicad_sym

effect_hidden      = kicad_sym.TextEffect(sizex=0, sizey=0, is_hidden=True)
effect_halign_left = kicad_sym.TextEffect(sizex=1.27, sizey=1.27, h_justify="left")
color_none         = kicad_sym.Color(r=0, g=0, b=0, a=0)

# lib_version = datetime.datetime.now().strftime("%Y%m%d")
# Hack
lib_version = 20200101


def append_parts(lib_object, description_value_re, name_expand_template, reference, footprint, where_clause, symbol_pins, text_posx, value_expand_template=None, symbol_rectangles=None, symbol_polylines=None, symbol_arcs=None):
    lib_object.version = lib_version
    cursor = conn.cursor()
    cursor.execute('select CAST(lcsc AS varchar) AS "LCSC Part", manufacturers.name as "Manufacturer", mfr as "MPN", REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(Description," @ ","@"),"mA 1 ","mA "),"Ohm","Ω"),"ohm","Ω") ,"Ωs","Ω")," Ω","Ω") ," kΩ","kΩ")," MΩ","MΩ") AS Description, "Datasheet" from components LEFT OUTER JOIN manufacturers ON manufacturers.id = components.manufacturer_id LEFT OUTER JOIN categories on categories.id = components.category_id WHERE {}'.format(where_clause))
    for row in cursor.fetchall():
        (lcsc_part, mfg_name, mfg_part, description, datasheet) = row
        try:
            m = re.match(description_value_re, description)
            name = m.expand(name_expand_template)
            if value_expand_template:
                value = m.expand(value_expand_template)
            else:
                value = name
        except:
            print("Can't parse, skipping " + lcsc_part + " '" + description + "'")
            continue
        # print(lcsc_part + " " + description)
        description_txt = re.sub("[^-A-Za-z 0-9%(),±@Ω]", "", description).strip()
        symbol = kicad_sym.KicadSymbol.new(name=name,
                                           libname="jlcpcb-basic-resistor",
                                           reference=reference,
                                           footprint=footprint,
                                           description=description_txt,
                                           datasheet=datasheet,
        )
        symbol.properties.append(kicad_sym.Property(name="LCSC", value=lcsc_part, idd=len(symbol.properties), effects=effect_hidden))
        symbol.properties.append(kicad_sym.Property(name="MFG", value=mfg_name, idd=len(symbol.properties), effects=effect_hidden))
        symbol.properties.append(kicad_sym.Property(name="MFGPN", value=mfg_part, idd=len(symbol.properties), effects=effect_hidden))
        symbol.get_property("Reference").posx=text_posx
        symbol.get_property("Reference").posy=0.508
        symbol.get_property("Reference").effects=effect_halign_left
        symbol.get_property("Value").value=value
        symbol.get_property("Value").posx=text_posx
        symbol.get_property("Value").posy=-1.016
        symbol.get_property("Value").effects=effect_halign_left
        for pin in symbol_pins:
            symbol.pins.append(pin)
        if symbol_rectangles:
            for rectangle in symbol_rectangles:
                symbol.rectangles.append(rectangle)
        if symbol_polylines:
            for polyline in symbol_polylines:
                symbol.polylines.append(polyline)
        if symbol_arcs:
            for arc in symbol_arcs:
                symbol.arcs.append(arc)
        lib_object.symbols.append(symbol)
    lib_object.write()
    
conn = sqlite3.connect('build/cache.sqlite3');

# Symbol Definition


resistor_pins = [ kicad_sym.Pin(name="~", number="1", etype="passive", posx=0, posy=2.54, rotation=270, length=0.762, name_effect=effect_hidden, number_effect=effect_hidden),
                kicad_sym.Pin(name="~", number="2", etype="passive", posx=0, posy=-2.54, rotation=90, length=0.762, name_effect=effect_hidden, number_effect=effect_hidden),
]
resistor_rectangles = [ kicad_sym.Rectangle(startx=-0.762, starty=1.778, endx=0.762, endy=-1.778, fill_type="none", stroke_width=0.2032)
]

capacitor_pins = [ kicad_sym.Pin(name="~", number="1", etype="passive", posx=0, posy=2.54, rotation=270, length=2.032, name_effect=effect_hidden, number_effect=effect_hidden),
                   kicad_sym.Pin(name="~", number="2", etype="passive", posx=0, posy=-2.54, rotation=90, length=2.032, name_effect=effect_hidden, number_effect=effect_hidden),
]
capacitor_polylines = [ kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.524, y=-0.508), kicad_sym.Point(x=1.524, y=-0.508) ], stroke_width=0.3048),
                        kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.524, y=+0.508), kicad_sym.Point(x=1.524, y=+0.508) ], stroke_width=0.3048),
]

inductor_pins = [ kicad_sym.Pin(name="~", number="1", etype="passive", posx=0, posy=2.54, rotation=270, length=2.032, name_effect=effect_hidden, number_effect=effect_hidden),
                  kicad_sym.Pin(name="~", number="2", etype="passive", posx=0, posy=-2.54, rotation=90, length=2.032, name_effect=effect_hidden, number_effect=effect_hidden),
]
inductor_arcs = [ kicad_sym.Arc(startx=0.0, starty=0.0, endx=0.0, endy=0.508, midx=0.254, midy=0.254, stroke_width=0.2032),
    #               kicad_sym.Arc(points=[kicad_sym.Point(x=0, y=0), kicad_sym.Point(x=0.508, y=0), kicad_sym.Point(x=0.254, y=0.254) ], stroke_width=0.3048),
    #               kicad_sym.Arc(points=[kicad_sym.Point(x=0.508, y=0), kicad_sym.Point(x=1.016, y=0), kicad_sym.Point(x=0.762, y=0.254) ], stroke_width=0.3048),
    #               kicad_sym.Arc(points=[kicad_sym.Point(x=0, y=0), kicad_sym.Point(x=-0.508, y=0), kicad_sym.Point(x=-0.254, y=0.254) ], stroke_width=0.3048),
    #               kicad_sym.Arc(points=[kicad_sym.Point(x=-0.508, y=0), kicad_sym.Point(x=-1.016, y=0), kicad_sym.Point(x=-0.762, y=0.254) ], stroke_width=0.3048),
]

# ===========================================================================================================================
# All Resistors
lib_resistors_all = kicad_sym.KicadLibrary("build/jlcpcb-basic-resistor.kicad_sym")
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?±)(?P<tolerance>\d+\.?\d*%)(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*)',
             name_expand_template='\\4_0402_\\2',
             reference='R',
             footprint='R_0402_1005Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%402" and description not in ("0402  Chip Resistor - Surface Mount ROHS","0402 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%:%%Ω%" ESCAPE ":" OR description LIKE "%:%%ohm%" ESCAPE ":")')
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*?±)(?P<tolerance>\d+\.?\d*%)(.*)',
             name_expand_template='\\4_0402_\\2',
             reference='R',
             footprint='R_0402_1005Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%402" and description not in ("0402  Chip Resistor - Surface Mount ROHS","0402 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%Ω%:%%" ESCAPE ":" OR description LIKE "%ohm%:%%" ESCAPE ":")')
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?±)(?P<tolerance>\d+\.?\d*%)(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*)',
             name_expand_template='\\4_0603_\\2',
             reference='R',
             footprint='R_0603_1608Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%603" and description not in ("0603  Chip Resistor - Surface Mount ROHS","0603 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%:%%Ω%" ESCAPE ":" OR description LIKE "%:%%ohm%" ESCAPE ":")')
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*?±)(?P<tolerance>\d+\.?\d*%)(.*)',
             name_expand_template='\\4_0603_\\2',
             reference='R',
             footprint='R_0603_1608Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%603" and description not in ("0603  Chip Resistor - Surface Mount ROHS","0603 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%Ω%:%%" ESCAPE ":" OR description LIKE "%ohm%:%%" ESCAPE ":")')
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?±)(?P<tolerance>\d+\.?\d*%)(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*)',
             name_expand_template='\\4_0805_\\2',
             reference='R',
             footprint='R_0805_2012Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%805" and description not in ("0805  Chip Resistor - Surface Mount ROHS","0805 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%:%%Ω%" ESCAPE ":" OR description LIKE "%:%%ohm%" ESCAPE ":")')
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*?±)(?P<tolerance>\d+\.?\d*%)(.*)',
             name_expand_template='\\4_0805_\\2',
             reference='R',
             footprint='R_0805_2012Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%805" and description not in ("0805  Chip Resistor - Surface Mount ROHS","0805 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%Ω%:%%" ESCAPE ":" OR description LIKE "%ohm%:%%" ESCAPE ":")')
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?±)(?P<tolerance>\d+\.?\d*%)(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*)',
             name_expand_template='\\4_01206_\\2',
             reference='R',
             footprint='R_1206_3216Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%1206" and description not in ("01206  Chip Resistor - Surface Mount ROHS","01206 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%:%%Ω%" ESCAPE ":" OR description LIKE "%:%%ohm%" ESCAPE ":")')
append_parts(lib_object=lib_resistors_all,
             description_value_re=r'(.*?)(?P<resistance>\d+\.?\d*[mkM]?[Ω])(.*?±)(?P<tolerance>\d+\.?\d*%)(.*)',
             name_expand_template='\\4_01206_\\2',
             reference='R',
             footprint='R_1206_3216Metric',
             symbol_pins=resistor_pins,
             symbol_rectangles=resistor_rectangles,
             text_posx=0.762,
             where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%1206" and description not in ("01206  Chip Resistor - Surface Mount ROHS","01206 Chip Resistor - Surface Mount RoHS","") and (description LIKE "%Ω%:%%" ESCAPE ":" OR description LIKE "%ohm%:%%" ESCAPE ":")')

# ===========================================================================================================================
# All Capacitors
lib_capacitors_all_basic = kicad_sym.KicadLibrary("build/jlcpcb-basic-capacitor.kicad_sym")
append_parts(lib_object=lib_capacitors_all_basic,
             description_value_re=r'(?P<voltage>\d+(\.\d+)?V)\s+(?P<capacitance>\d+(\.\d+)?[pnµuF]+)\s+(?P<dielectric>[A-Z0-9]+)\s+±(?P<tolerance>\d+%)\s+(?P<package_size>\d+)(.*)',
             name_expand_template='\\3_0402_\\1_\\6',
             reference='C',
             footprint='C_0402_1005Metric',
             symbol_pins=capacitor_pins,
             symbol_polylines=capacitor_polylines,
             text_posx=1.71,
             where_clause='basic = 1 and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "%402"')
append_parts(lib_object=lib_capacitors_all_basic,
             description_value_re=r'(?P<voltage>\d+(\.\d+)?V)\s+(?P<capacitance>\d+(\.\d+)?[pnµuF]+)\s+(?P<dielectric>[A-Z0-9]+)\s+(?P<tolerance>±\d+%)\s+(?P<package_size>\d+)(.*)',
             name_expand_template='\\2_0402_\\1_\\4',
             reference='C',
             footprint='C_0603_1608Metric',
             symbol_pins=capacitor_pins,
             symbol_polylines=capacitor_polylines,
             text_posx=1.71,
             where_clause= 'basic = 1 and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "%603"')
append_parts(lib_object=lib_capacitors_all_basic,
             description_value_re=r'(?P<voltage>\d+(\.\d+)?V)\s+(?P<capacitance>\d+(\.\d+)?[pnµuF]+)\s+(?P<dielectric>[A-Z0-9]+)\s+(?P<tolerance>±\d+%)\s+(?P<package_size>\d+)(.*)',
             name_expand_template='\\2_0402_\\1_\\4',
             reference='C',
             footprint='C_0805_2012Metric',
             symbol_pins=capacitor_pins,
             symbol_polylines=capacitor_polylines,
             text_posx=1.71,
             where_clause='basic = 1 and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "%805"')
append_parts(lib_object=lib_capacitors_all_basic,
             description_value_re=r'(?P<voltage>\d+(\.\d+)?V)\s+(?P<capacitance>\d+(\.\d+)?[pnµuF]+)\s+(?P<dielectric>[A-Z0-9]+)\s+(?P<tolerance>±\d+%)\s+(?P<package_size>\d+)(.*)',
             name_expand_template='\\2_0402_\\1_\\4',
             reference='C',
             footprint='C_1206_3216Metric',
             symbol_pins=capacitor_pins,
             symbol_polylines=capacitor_polylines,
             text_posx=1.71,
             where_clause='basic = 1 and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "1206"')
             
# ===========================================================================================================================
# Basic Inductors
lib_inductors_all = kicad_sym.KicadLibrary("build/jlcpcb-basic-FerriteBead.kicad_sym")
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_0402',
             reference='L',
             footprint='L_0402_1005Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 1 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%402" AND Description not in ("0402  Ferrite Beads ROHS","100mΩ 0402  Ferrite Beads ROHS","30mΩ 0402  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_0603',
             reference='L',
             footprint='L_0603_1608Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 1 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%603" AND Description not in ("0603  Ferrite Beads ROHS","100mΩ 0603  Ferrite Beads ROHS","30mΩ 0603  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_0805',
             reference='L',
             footprint='L_0805_2012Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 1 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%805" AND Description not in ("0805  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_01206',
             reference='L',
             footprint='L_1206_3216Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 1 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%1206" AND Description not in ("1206  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')

# ===========================================================================================================================
# Extended Inductors
lib_inductors_all = kicad_sym.KicadLibrary("build/jlcpcb-extended-FerriteBead.kicad_sym")
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_0402',
             reference='L',
             footprint='L_0402_1005Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 0 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%402" AND Description not in ("0402  Ferrite Beads ROHS","100mΩ 0402  Ferrite Beads ROHS","30mΩ 0402  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_0603',
             reference='L',
             footprint='L_0603_1608Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 0 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%603" AND Description not in ("0603  Ferrite Beads ROHS","100mΩ 0603  Ferrite Beads ROHS","30mΩ 0603  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_0805',
             reference='L',
             footprint='L_0805_2012Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 0 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%805" AND Description not in ("0805  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')
append_parts(lib_object=lib_inductors_all,
             description_value_re=r'(?P<current>\d+mA)?\s*(?P<resistance>\d+\.?\d*[mkM]?Ω)?\s*(?P<tolerance>±\d+%)?\s*(?P<impedance>\d+\.?\d*[kmM]?Ω)@(?P<frequency>\d+[kM]Hz)(.*)',
             name_expand_template='\\4@\\5_01206',
             reference='L',
             footprint='L_1206_3216Metric',
             symbol_pins=inductor_pins,
             symbol_arcs=inductor_arcs,
             text_posx=1.71,
             where_clause='basic = 0 and "Subcategory" LIKE "Ferrite Beads"  and "Package" like "%1206" AND Description not in ("1206  Ferrite Beads ROHS") and description not like "%Hz%Ω%"')



# # ===========================================================================================================================
# # 0402 resistors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-resistor-0402.kicad_sym"),
#              description_value_re="¡À([0-9%]+).*¡æ\s*(.*)¦¸.*",
#              name_expand_template='\\2',
#              reference='R',
#              footprint='R_0402_1005Metric',
#              symbol_pins=resistor_pins,
#              symbol_rectangles=resistor_rectangles,
#              text_posx=0.762,
#              where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%402"')

# # ===========================================================================================================================
# # 0603 resistors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-resistor-0603.kicad_sym"),
#              description_value_re="¡À([0-9%]+).*¡æ\s*(.*)¦¸.*",
#              name_expand_template='\\2',
#              reference='R',
#              footprint='R_0603_1608Metric',
#              symbol_pins=resistor_pins,
#              symbol_rectangles=resistor_rectangles,
#              text_posx=0.762,
#              where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%603"')

# # ===========================================================================================================================
# # 0805 resistors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-resistor-0805.kicad_sym"),
#              description_value_re="¡À([0-9%]+).*¡æ\s*(.*)¦¸.*",
#              name_expand_template='\\2',
#              reference='R',
#              footprint='R_0805_2012Metric',
#              symbol_pins=resistor_pins,
#              symbol_rectangles=resistor_rectangles,
#              text_posx=0.762,
#              where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "%805"')

# # ===========================================================================================================================
# # 1206 resistors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-resistor-1206.kicad_sym"),
#              description_value_re="¡À([0-9%]+).*¡æ\s*(.*)¦¸.*",
#              name_expand_template='\\2',
#              reference='R',
#              footprint='R_1206_3216Metric',
#              symbol_pins=resistor_pins,
#              symbol_rectangles=resistor_rectangles,
#              text_posx=0.762,
#              where_clause='basic = 1 and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount" and "Package" like "1206"')

# # ===========================================================================================================================
# # 0402 Capacitors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-capacitor-0402.kicad_sym"),
#              description_value_re="(.+)\s(.+)\s(.+)¡À.*",
#              name_expand_template='\\2,\\1,\\3',
#              reference='C',
#              footprint='C_0402_1005Metric',
#              symbol_pins=capacitor_pins,
#              symbol_polylines=capacitor_polylines,
#              text_posx=1.71,
#              where_clause='basic = 1 and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "%402"')
# # ===========================================================================================================================
# # 0603 Capacitors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-capacitor-0603.kicad_sym"),
#              description_value_re="(.+)\s(.+)\s(.+)¡À.*",
#              name_expand_template='\\2,\\1,\\3',
#              reference='C',
#              footprint='C_0603_1608Metric',
#              symbol_pins=capacitor_pins,
#              symbol_polylines=capacitor_polylines,
#              text_posx=1.71,
#              where_clause= '"Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "%603"')
# # ===========================================================================================================================
# # 0805 Capacitors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-capacitor-0805.kicad_sym"),
#              description_value_re="(.+)\s(.+)\s(.+)¡À.*",
#              name_expand_template='\\2,\\1,\\3',
#              reference='C',
#              footprint='C_0805_2012Metric',
#              symbol_pins=capacitor_pins,
#              symbol_polylines=capacitor_polylines,
#              text_posx=1.71,
#              where_clause='basic = 1 and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "%805"')
# # ===========================================================================================================================
# # 1206 Capacitors
# append_parts(lib_object=kicad_sym.KicadLibrary("build/jlcpcb-basic-capacitor-1206.kicad_sym"),
#              description_value_re="(.+)\s(.+)\s(.+)¡À.*",
#              name_expand_template='\\2,\\1,\\3',
#              reference='C',
#              footprint='C_1206_3216Metric',
#              symbol_pins=capacitor_pins,
#              symbol_polylines=capacitor_polylines,
#              text_posx=1.71,
#              where_clause='basic = 1 and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and "Package" like "1206"')

conn.close()