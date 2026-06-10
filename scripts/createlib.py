#!/usr/bin/env python3
import sqlite3
import re
import sys

sys.path.append("kicad-library-utils/common")

import kicad_sym

effect_hidden      = kicad_sym.TextEffect(sizex=0, sizey=0, is_hidden=True)
effect_halign_left = kicad_sym.TextEffect(sizex=1.27, sizey=1.27, h_justify="left")
color_none         = kicad_sym.Color(r=0, g=0, b=0, a=0)

#Set kicad compatibility. Only KiCAD built after this date will work
lib_version = 20200101

def get_group(pattern, text):
    return pattern.search(text).group() if pattern.search(text) else None

def append_parts(lib_object, name_template, reference, footprint, libname, where_clause, symbol_pins, ref_text_posx, ref_text_posy, val_text_posx, val_text_posy, ref_text_effect=effect_halign_left, val_text_effect=effect_halign_left, ref_text_rotation=0, val_text_rotation=0, value_template=None, symbol_rectangles=None, symbol_polylines=None, symbol_arcs=None):
    lib_object.version = lib_version
    cursor = conn.cursor()
    query = """
        WITH replacements(original, changed) AS (
        VALUES 
            (' @ ', '@'),
            ('mA 1 ', 'mA '),
            ('Ohm', 'Ω'),
            ('ohm', 'Ω'),
            ('Ωs', 'Ω'),
            (' Ω', 'Ω'),
            (' kΩ', 'kΩ'),
            (' MΩ', 'MΩ')
        )
        SELECT 
        CAST( 'C' || lcsc AS varchar) AS "lcsc_part", 
        manufacturer, 
        mfr AS "mpn", 
        (
            SELECT COALESCE(MAX(result), Description)
            FROM (
            SELECT REPLACE(desc_col, original, changed) AS result
            FROM replacements
            CROSS JOIN (SELECT Description AS desc_col) AS t
            )
        ) AS description,
        datasheet 
        FROM jlc_components
        WHERE {where_clause}
    """

    cursor.execute(query.format(where_clause=where_clause))
    results = []
    for row in cursor.fetchall():
        (lcsc_part, mfg_name, mfg_part, description, datasheet) = row

        try:
            matches = {}
            for key, pattern in patterns.items():
                match = pattern.search(description)
                matches[key] = match.group() if match else None

            value = eval(value_template)
            name = eval(name_template)

            if value is None:
                print(f"Skipping {lcsc_part}: no parsed value from {description!r}")
                continue

        except:
            print("Can't parse, skipping C" + lcsc_part + " '" + description + "'")
            continue

        symbol = kicad_sym.KicadSymbol.new(name=name,
                                           libname=libname,
                                           reference=reference,
                                           footprint=footprint,
                                           description=re.sub(r'[^-A-Za-z 0-9%()℃~+-,±@Ω/\.]','', description.strip()),
                                           datasheet=datasheet,
        )
        symbol.exclude_from_sim = False
        symbol.in_bom = True
        symbol.on_board = True
        symbol.in_pos_files = True
        symbol.duplicate_pin_numbers_are_jumpers = False
        symbol.hide_pin_numbers = True
        symbol.pin_names_offset = 0

        symbol.properties.append(kicad_sym.Property(name="LCSC", value=lcsc_part, idd=len(symbol.properties), effects=effect_hidden))
        symbol.properties.append(kicad_sym.Property(name="MFG", value=mfg_name, idd=len(symbol.properties), effects=effect_hidden))
        symbol.properties.append(kicad_sym.Property(name="MFGPN", value=mfg_part, idd=len(symbol.properties), effects=effect_hidden))
        symbol.get_property("Reference").posx=ref_text_posx
        symbol.get_property("Reference").posy=ref_text_posy
        symbol.get_property("Reference").rotation=ref_text_rotation
        symbol.get_property("Reference").effects=ref_text_effect
        symbol.get_property("Value").value=value
        symbol.get_property("Value").posx=val_text_posx
        symbol.get_property("Value").posy=val_text_posy
        symbol.get_property("Value").rotation=val_text_rotation
        symbol.get_property("Value").effects=val_text_effect
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
resistor_pins = [ kicad_sym.Pin(name="", number="1", etype="passive", posx=0, posy=3.81, rotation=270, length=1.27),
                kicad_sym.Pin(name="", number="2", etype="passive", posx=0, posy=-3.81, rotation=90, length=1.27),
]
resistor_rectangles = [ kicad_sym.Rectangle(startx=-1.016, starty=-2.54, endx=1.016, endy=2.54, fill_type="none", stroke_width=0.254)
]

capacitor_pins = [ kicad_sym.Pin(name="~", number="1", etype="passive", posx=0, posy=3.81, rotation=270, length=2.794, name_effect=effect_hidden, number_effect=effect_hidden),
                   kicad_sym.Pin(name="~", number="2", etype="passive", posx=0, posy=-3.81, rotation=90, length=2.794, name_effect=effect_hidden, number_effect=effect_hidden),
]
capacitor_polylines = [ kicad_sym.Polyline(points=[kicad_sym.Point(x=-2.032, y=-0.762), kicad_sym.Point(x=2.032, y=-0.762) ], stroke_width=0.508),
                        kicad_sym.Polyline(points=[kicad_sym.Point(x=-2.032, y=+0.762), kicad_sym.Point(x=2.032, y=+0.762) ], stroke_width=0.508),
]

ferrite_bead_pins = [ kicad_sym.Pin(name="~", number="1", etype="passive", posx=0, posy=3.81, rotation=270, length=2.54),
                  kicad_sym.Pin(name="~", number="2", etype="passive", posx=0, posy=-3.81, rotation=90, length=2.54, name_effect=effect_hidden, number_effect=effect_hidden),
]
ferrite_bead_polylines = [
    kicad_sym.Polyline(points=[kicad_sym.Point(x=0, y=1.27), kicad_sym.Point(x=0, y=1.2954) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-2.7686, y=0.4064), kicad_sym.Point(x=-1.7018, y=2.2606), kicad_sym.Point(x=2.7686, y=-0.3048), kicad_sym.Point(x=1.6764, y=-2.1590), kicad_sym.Point(x=-2.7686, y=0.4064) ], stroke_width=0),
]

# inductor_arcs = [ kicad_sym.Arc(startx=0.0, starty=0.0, endx=0.0, endy=0.508, midx=0.254, midy=0.254, stroke_width=0.2032),
# ]
# inductor_pins = [ kicad_sym.Pin(name="~", number="1", etype="passive", posx=0, posy=3.81, rotation=270, length=2.54),
#                   kicad_sym.Pin(name="~", number="2", etype="passive", posx=0, posy=-3.81, rotation=90, length=2.54, name_effect=effect_hidden, number_effect=effect_hidden),
# ]

diode_pins = [
    kicad_sym.Pin(name="K", number="1", etype="passive", posx=-3.81, posy=0, rotation=0, length=2.54, name_effect=effect_hidden, number_effect=effect_hidden),
    kicad_sym.Pin(name="A", number="2", etype="passive", posx=3.81, posy=0, rotation=180, length=2.54, name_effect=effect_hidden, number_effect=effect_hidden),
]
diode_polylines = [
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=0) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.27, y=-1.27), kicad_sym.Point(x=-1.27, y=1.27) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=1.27, y=-1.27), kicad_sym.Point(x=1.27, y=1.27), kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=-1.27) ], stroke_width=0),
]
led_polylines = [
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-3.048, y=-0.762), kicad_sym.Point(x=-4.572, y=-2.286), kicad_sym.Point(x=-3.81, y=-2.286), kicad_sym.Point(x=-4.572, y=-2.286), kicad_sym.Point(x=-4.572, y=-1.524) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.778, y=-0.762), kicad_sym.Point(x=-3.302, y=-2.286), kicad_sym.Point(x=-2.54, y=-2.286), kicad_sym.Point(x=-3.302, y=-2.286), kicad_sym.Point(x=-3.302, y=-1.524) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=0) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.27, y=-1.27), kicad_sym.Point(x=-1.27, y=1.27) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=1.27, y=-1.27), kicad_sym.Point(x=1.27, y=1.27), kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=-1.27) ], stroke_width=0),
]
diode_schottky_polylines = [
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=0) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.905, y=0.635), kicad_sym.Point(x=-1.905, y=1.27), kicad_sym.Point(x=-1.27, y=1.27), kicad_sym.Point(x=-1.27, y=-1.27), kicad_sym.Point(x=-0.635, y=-1.27), kicad_sym.Point(x=-0.635, y=-0.635) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=1.27, y=-1.27), kicad_sym.Point(x=1.27, y=1.27), kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=-1.27) ], stroke_width=0),
]
diode_zener_polylines = [
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=0) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=-1.27, y=-1.27), kicad_sym.Point(x=-1.27, y=1.27), kicad_sym.Point(x=-0.762, y=1.27) ], stroke_width=0),
    kicad_sym.Polyline(points=[kicad_sym.Point(x=1.27, y=-1.27), kicad_sym.Point(x=1.27, y=1.27), kicad_sym.Point(x=-1.27, y=0), kicad_sym.Point(x=1.27, y=-1.27) ], stroke_width=0),
]

#Regular expressions
capacitance_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:pF|nF|uF|F)',re.I)
dielectric_RE = re.compile(r'(?:X[578][RST]|X6S|X7S|X7T|X8R|C0G|NP0|C0H|U2J|T2H|S2H|R2H|P2H|Y5V|Y5U)',re.I)
tolerance_RE = re.compile(r'(?:[±+-]\d+%|-\d+%~[+-]?\d+%)',re.I)
current_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:mA|µA|uA|mA|A|kA)',re.I)
resistance_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:Ω|ohm|mΩ|kΩ|MΩ|GΩ|kohm|Mohm|Z|Z\d+)',re.I)
impedance_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:Ω|ohm|kΩ|MΩ|Z|kΩ|Z\d+)',re.I)
frequency_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:Hz|kHz|MHz|GHz|THz)',re.I)
voltage_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:~|-|to)\s*\d+(?:\.\d+)?\s*V|\d+(?:\.\d+)?\s*k?V',re.I)
wavelength_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:~|-|to)\s*\d+(?:\.\d+)?\s*nm|\d+(?:\.\d+)?\s*nm',re.I)
brightness_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:mcd|cd)',re.I)
power_RE = re.compile(r'\d+(?:\.\d+)?\s*(?:mW|W|kW)',re.I)
colour_RE = re.compile(r'\b(?:red|green|blue|yellow|amber|orange|white|warm\s+white|natural\s+white|neutral\s+white|cool\s+white|rgb|pink|purple|violet|uv|infrared|ir)\b',re.I)

patterns = {
    'voltage': voltage_RE,
    'tolerance': tolerance_RE,
    'capacitance': capacitance_RE,
    'dielectric': dielectric_RE,
    'current': current_RE,
    'resistance': resistance_RE,
    'impedance': impedance_RE,
    'frequency': frequency_RE,
    'wavelength': wavelength_RE,
    'brightness': brightness_RE,
    'power': power_RE,
    'colour': colour_RE,
}

# ===========================================================================================================================
# Basic Resistors
libname = "JLCPCB_Basic_Resistor"
lib = kicad_sym.KicadLibrary("build/"+libname+".kicad_sym")
packages = [
    ('0402', 'Resistor_SMD:R_0402_1005Metric', 'like "%402"'),
    ('0603', 'Resistor_SMD:R_0603_1608Metric', 'like "%603"'),
    ('0805', 'Resistor_SMD:R_0805_2012Metric', 'like "%805"'),
    ('1206', 'Resistor_SMD:R_1206_3216Metric', 'like "%1206"')
]
for packagename, footprintname, packagematch in packages:
    append_parts(lib_object=lib,
                name_template="'_'.join(filter(None, [matches['resistance'], '" + packagename + "', matches['tolerance']]))",
                value_template="matches['resistance']",
                reference='R',
                libname=libname,
                footprint=footprintname,
                symbol_pins=resistor_pins,
                symbol_rectangles=resistor_rectangles,
                ref_text_posx=0.762,
                val_text_posx=0.762,
                ref_text_posy=2.54,
                val_text_posy=-2.54,
                where_clause='(library_type = "base" OR preferred = 1) and "Category" = "Resistors" and "Subcategory" = "Chip Resistor - Surface Mount"  and Package ' + packagematch)

# ===========================================================================================================================
# Basic Capacitors
libname = "JLCPCB_Basic_Capacitor"
lib = kicad_sym.KicadLibrary("build/"+libname+".kicad_sym")
packages = [
    ('0402', 'Capacitor_SMD:C_0402_1005Metric', 'like "%402"'),
    ('0603', 'Capacitor_SMD:C_0603_1608Metric', 'like "%603"'),
    ('0805', 'Capacitor_SMD:C_0805_2012Metric', 'like "%805"'),
    ('1206', 'Capacitor_SMD:C_1206_3216Metric', 'like "%1206"')
]
for packagename, footprintname, packagematch in packages:
    append_parts(lib_object=lib,
                name_template="'_'.join(filter(None, [matches['capacitance'], '" + packagename + "', matches['voltage'], matches['dielectric'], matches['tolerance']]))",
                value_template="matches['capacitance']",
                reference='C',
                libname=libname,
                footprint=footprintname,
                symbol_pins=capacitor_pins,
                symbol_polylines=capacitor_polylines,
                ref_text_posx=0.635,
                val_text_posx=0.635,
                ref_text_posy=2.54,
                val_text_posy=-2.54,
                where_clause='(library_type = "base" OR preferred = 1) and "Category" = "Capacitors" and "Subcategory" = "Multilayer Ceramic Capacitors MLCC - SMD/SMT" and Package ' + packagematch + '')

# ===========================================================================================================================
# Basic ferrite-bead
libname = "JLCPCB_Basic_FerriteBead"
lib = kicad_sym.KicadLibrary("build/"+libname+".kicad_sym")
packages = [
    ('0402', 'Inductor_SMD:L_0402_1005Metric', 'like "%402"'),
    ('0603', 'Inductor_SMD:L_0603_1608Metric', 'like "%603"'),
    ('0805', 'Inductor_SMD:L_0805_2012Metric', 'like "%805"'),
    ('1206', 'Inductor_SMD:L_1206_3216Metric', 'like "%1206"')
]
for packagename, footprintname, packagematch in packages:
    append_parts(lib_object=lib,
                name_template="'_'.join(filter(None, [matches['impedance'] + '@' + matches['frequency'], '" + packagename + "', matches['current'], matches['tolerance']]))",
                value_template="matches['impedance'] + '@' + matches['frequency']",
                reference='FB',
                libname=libname,
                footprint=footprintname,
                symbol_pins=ferrite_bead_pins,
                symbol_polylines=ferrite_bead_polylines,
                ref_text_posx=-3.81,
                ref_text_posy=0.635,
                ref_text_effect='',
                ref_text_rotation=90,
                val_text_posx=3.81,
                val_text_posy=0,
                val_text_effect='',
                val_text_rotation=90,
                where_clause='(library_type = "base" OR preferred = 1) and "Subcategory" LIKE "Ferrite Beads"  and Package ' + packagematch)

# ===========================================================================================================================
# Basic led
libname = "JLCPCB_Basic_LED"
lib = kicad_sym.KicadLibrary("build/"+libname+".kicad_sym")
packages = [
    ('0402', 'LED_SMD:LED_0402_1005Metric', 'like "%402"'),
    ('0603', 'LED_SMD:LED_0603_1608Metric', 'like "%603"'),
    ('0805', 'LED_SMD:LED_0805_2012Metric', 'like "%805"'),
    ('1206', 'LED_SMD:LED_1206_3216Metric', 'like "%1206"')
]
for packagename, footprintname, packagematch in packages:
    append_parts(lib_object=lib,
                name_template="'_'.join(filter(None, [matches['colour'], '" + packagename + "', matches['current'], matches['brightness']]))",
                value_template="matches['colour']",
                reference='D',
                libname=libname,
                footprint=footprintname,
                symbol_pins=diode_pins,
                symbol_polylines=led_polylines,
                ref_text_posx=0,
                ref_text_posy=2.54,
                ref_text_effect='',
                ref_text_rotation=0,
                val_text_posx=0,
                val_text_posy=-2.54,
                val_text_effect='',
                val_text_rotation=0,
                where_clause='(library_type = "base" OR preferred = 1) and category="Optoelectronics" and "Subcategory"="LED Indication - Discrete" and Package ' + packagematch)

# ===========================================================================================================================
# Basic Diodes
packages = [
    ('0402', 'Diode_SMD:D_0402_1005Metric', 'like "%402"'),
    ('0603', 'Diode_SMD:D_0603_1608Metric', 'like "%603"'),
    ('0805', 'Diode_SMD:D_0805_2012Metric', 'like "%805"'),
    ('1206', 'Diode_SMD:D_1206_3216Metric', 'like "%1206"'),
    ('SOD-323', 'Diode_SMD:D_SOD-323', '= "SOD-323"'),
    ('SMA(DO-214AC)', 'Diode_SMD:D_SMA', '= "SMA(DO-214AC)"'),
    ('SOD-123', 'Diode_SMD:D_SOD-123', '= "SOD-123"'),
    ('SMC(DO-214AB)', 'Diode_SMD:D_SMC', '= "SMC(DO-214AB)"'),
    ('SOD-123FL', 'Diode_SMD:D_SOD-123F', '= "SOD-123FL"'),
    ('SMA', 'Diode_SMD:D_SMA', '= "SMA"'),
    ('SOD-523', 'Diode_SMD:D_SOD-523', '= "SOD-523"'),
    ('SMB', 'Diode_SMD:D_SMB', '= "SMB"'),
    ('SMC', 'Diode_SMD:D_SMC', '= "SMC"'),
    ('DO-214AC(SMA)', 'Diode_SMD:D_SMA', '= "DO-214AC(SMA)"'),
    ('DO-214AA(SMB)', 'Diode_SMD:D_SMB', '= "DO-214AA(SMB)"'),
    # ('SOT-323', '', 'SOT-323'),
    # ('SOT-363', '', 'SOT-363'),
    # ('MBS', '', 'MBS'),
    # ('SOT-23', '', 'SOT-23'),
    # ('DBS', '', 'DBS'),
    # ('SMAF', '', 'SMAF'),
    # ('SMBF', '', 'SMBF'),
]
libname = "JLCPCB_Basic_Diode-Zener"
lib = kicad_sym.KicadLibrary("build/"+libname+".kicad_sym")
for packagename, footprintname, packagematch in packages:
    append_parts(lib_object=lib,
                name_template="mfg_part",
                value_template="mfg_part",
                reference='D',
                libname=libname,
                footprint=footprintname,
                symbol_pins=diode_pins,
                symbol_polylines=diode_zener_polylines,
                ref_text_posx=0,
                ref_text_posy=2.54,
                ref_text_effect='',
                ref_text_rotation=0,
                val_text_posx=0,
                val_text_posy=-2.54,
                val_text_effect='',
                val_text_rotation=0,
                where_clause='(library_type = "base" OR preferred = 1) and category="Diodes" and "Subcategory"="Zener Diodes" and Package ' + packagematch)

libname = "JLCPCB_Basic_Diode-General"
lib = kicad_sym.KicadLibrary("build/"+libname+".kicad_sym")
for packagename, footprintname, packagematch in packages:
    append_parts(lib_object=lib,
                name_template="mfg_part",
                value_template="mfg_part",
                reference='D',
                libname=libname,
                footprint=footprintname,
                symbol_pins=diode_pins,
                symbol_polylines=diode_polylines,
                ref_text_posx=0,
                ref_text_posy=2.54,
                ref_text_effect='',
                ref_text_rotation=0,
                val_text_posx=0,
                val_text_posy=-2.54,
                val_text_effect='',
                val_text_rotation=0,
                where_clause='(library_type = "base" OR preferred = 1) and category="Diodes" and "Subcategory"="Diodes - General Purpose" and Package ' + packagematch)

libname = "JLCPCB_Basic_Diode-Schottky"
lib = kicad_sym.KicadLibrary("build/"+libname+".kicad_sym")
for packagename, footprintname, packagematch in packages:
    append_parts(lib_object=lib,
                name_template="mfg_part",
                value_template="mfg_part",
                reference='D',
                libname=libname,
                footprint=footprintname,
                symbol_pins=diode_pins,
                symbol_polylines=diode_schottky_polylines,
                ref_text_posx=0,
                ref_text_posy=2.54,
                ref_text_effect='',
                ref_text_rotation=0,
                val_text_posx=0,
                val_text_posy=-2.54,
                val_text_effect='',
                val_text_rotation=0,
                where_clause='(library_type = "base" OR preferred = 1) and category="Diodes" and "Subcategory"="Schottky Diodes" and Package ' + packagematch)



conn.close()