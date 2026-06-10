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