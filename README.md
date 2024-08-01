# kicad-jlcpcb

FutureProofHomes Electronics KiCad Libraries
====================================

This repository contains the FutureProofHomes KiCad Library of commonly used parts. It is a cultivated combination of KiCad parts (mostly symbols) and original FutureProofHomes-designed KiCAD footprints. This is a work in progress so be very cautious when using these symbols or footprints as they may contain errors.

**Note:** The FutureProofHomes KiCad components contain internal part numbers for JLCPCB for ease of manufacture. 

### Theory

KiCad is very good and has a large number of stock and industry common symbols and footprints. We are adding new parts to this library as we need them for new projects.

The FutureProofHomes approach: when a new part needs to be added we decide whether to use a KiCad stock symbol, edit it for use, or create it from scratch. We give preference to the stock KiCad symbol. We try to follow the [KiCad Library Conventions](https://klc.kicad.org/) where possible.

Additionally, JPCPCB/FabHouses needs to assign various unique manufacturing data (ie, internal part numbers) to parts. To alleviate this, there is a large number of components with an identical symbol each with their own production ID information. For example, capacitors:

![List of FutureProofHomes capacitors in KiCad](Capacitor-List.png)

We use the following naming conventions to create our 'bubble gum' parts: 

* [capacity]\_[size]\_[voltage]_[tolerance]
* [resistance]\_[size]\_[wattage optional]_[tolerance optional]
* [inductance]\_[size]\_[max current]
* [led color]\_[size]\_[wavelength optional]

Contents
-------------------

* [/Footprints](https://github.com/FutureProofHomes/KiCad-Libraries/tree/main/Footprints) -- PCB footprints
* [/Symbols](https://github.com/FutureProofHomes/KiCad-Libraries/tree/main/Symbols) -- Schematic symbols

License
-------------------

This library is released under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) license. 
**You are welcome to use this library for commercial purposes.**
For attribution, we ask that when you begin to sell your device using our footprint, you email us with a link to the product being sold. 
We want bragging rights that we helped (in a very small part) to create your 8th world wonder. 
We would like the opportunity to feature your device on our homepage.

Please consider contributing back to this library or others to help the open-source hardware community continue to thrive and grow! 

Scripts based on the work of TomKeddie https://github.com/TomKeddie/prj-kicad-jlcpcb
