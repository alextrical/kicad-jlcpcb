**kicad-jlcpcb**
Generate KiCad symbol libraries for commonly used JLCPCB/LCSC parts, including JLCPCB assembly metadata needed for manufacturing.

**Overview**
`kicad-jlcpcb` is a library generation project for KiCad users who build boards with JLCPCB assembly in mind. The repository contains the scripts, helper utilities, and workflow logic required to generate `.kicad_sym` libraries from upstream part data.
The project is designed around a reproducible workflow:

* fetch upstream cached part data
* process and normalize that data
* generate KiCad symbol libraries
* attach JLCPCB-specific part metadata
* publish generated libraries to a separate consumption repository

This repository is intended to be the **source repository** for generation logic. In a production setup, the generated libraries are typically published into a second repository so downstream users can consume a clean output-only library repo.

**Why this exists**
KiCad already ships with a strong set of general-purpose symbols and footprints. This project does not try to replace those official libraries. Instead, it focuses on the gap between schematic capture and JLCPCB assembly, where real manufacturing workflows depend on supplier- and assembler-specific identifiers.
For many commonly used passives and production parts, the electrical symbol is generic but the manufacturable part is not. A single resistor or capacitor value may correspond to many JLCPCB/LCSC orderable variants, each with different package, tolerance, voltage, or internal part number data.
This project generates practical symbols that preserve the ease of use of generic library parts while embedding the metadata required for board assembly.

**Features**

* Generates KiCad symbol libraries from scripted inputs
* Pulls upstream cached JLCPCB/LCSC part data during generation
* Supports repeatable local builds and scheduled CI builds
* Works well with a two-repository setup, one for source code and one for published libraries
* Uses a Git submodule for KiCad library utility dependencies
* Suited to stock-driven or regularly refreshed library generation workflows

**Naming conventions**
Generated symbols use compact, predictable names so common component variants are easy to find.

* Capacitors: `capacity_size_voltage_tolerance
* Resistors: `resistance_size_wattage(optional)_tolerance(optional)
* Inductors: `inductance_size_max current
* LEDs: `led color_size_wavelength optional

**Examples:**

* `100nF_0603_16V_10%`
* `10k_0402_1%`
* `4u7_0805_1A`
* `green_0603_565nm`
  
  Requirements
  Typical local dependencies:
* `bash`
* `python3`
* `wget`
* `p7zip`/`7z`
* `sed`
* `git`

On Debian or Ubuntu systems, a typical install command is:

```
sudo apt-get update
sudo apt-get install -y git python3 wget p7zip-full sed
```

***Clone and setup***
Clone the repository with submodules:

```
git clone --recurse-submodules https://github.com/alextrical/kicad-jlcpcb.git
cd kicad-jlcpcb
```

If the repository has already been cloned without submodules:

```
git config --global --unset-all url.git@gitlab.com:.insteadof
git submodule sync --recursive
git submodule update --init --recursive
```

This project uses the following submodule:

```
[submodule "scripts/kicad-library-utils"]
path = scripts/kicad-library-utils
url = https://gitlab.com/kicad/libraries/kicad-library-utils
```

***Local workflow***
A typical local generation flow is:

1. Initialize the submodule.
2. Fetch the latest cached JLCPCB/LCSC data.
3. Extract the archives into the build directory.
4. Run the Python generation script.
5. Clean the generated symbol output.
6. Copy the `.kicad_sym` files into `out/` or a publication directory.

***Example:***
```
   chmod +x generate.sh
   ./generate.sh
```

A CI-friendly version of `generate.sh` usually writes outputs into `out/` instead of moving them directly into another repository. For example:

```
#!/usr/bin/env bash
set -euo pipefail

mkdir -p build out
wget -N -c https://yaqwsx.github.io/jlcparts/data/cache.zip -P build/

for i in $(seq -w 1 99); do
url="https://yaqwsx.github.io/jlcparts/data/cache.z$i"
wget -N -c "$url" -P build/ || break
done

7z x build/cache.zip -obuild/ -aoa
python3 createlib.py
sed -i 's/\\"//g' build/*.kicad_sym
cp build/*.kicad_sym out/
```

***Consuming the generated libraries***
The generated library repository can be used in several ways:
* clone it locally and point KiCad library tables to it
* include it as a dependency in internal tooling
* package release archives for download
* track updates through Git history and scheduled regeneration
This keeps the generation logic separate from the consumable output, which is cleaner for both maintainers and downstream users.

***Open-source use***
This project is published for public use and contribution. Issues, improvements, bug reports, and pull requests are welcome.
Typical contributions include:
* fixes to generation logic
* support for additional part families
* better metadata normalization
* CI improvements
* documentation updates
For larger changes, opening an issue first is a good way to align on the intended direction.

***Development notes***
A few implementation details are worth keeping in mind:
* Git submodules are not initialized automatically unless cloning with `--recurse-submodules` or running `git submodule update --init --recursive` later.
* actions/checkout` supports recursive submodule checkout in GitHub Actions, which is useful for `scripts/kicad-library-utils`.
* For workflows that push into a second private repository, a PAT with access to the destination repository is typically required.

License
-------
This library is released under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) license.
**You are welcome to use this library for commercial purposes.**
For attribution, we ask that when you begin to sell your device using our footprint, you email us with a link to the product being sold.
We want bragging rights that we helped (in a very small part) to create your 8th world wonder.
We would like the opportunity to feature your device on our homepage.

Please consider contributing back to this library or others to help the open-source hardware community continue to thrive and grow!

Scripts based on the work of TomKeddie https://github.com/TomKeddie/prj-kicad-jlcpcb
