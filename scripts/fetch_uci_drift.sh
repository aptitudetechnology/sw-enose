#!/bin/sh
# Fetch the UCI Gas Sensor Array Drift at Different Concentrations dataset (id 270) into
# data/uci_drift/raw/. Licence and required citations: see sw_enose/sensors.py.
set -e
cd "$(dirname "$0")/.."
mkdir -p data/uci_drift
curl -sSL -o data/uci_drift/drift270.zip \
  "https://archive.ics.uci.edu/static/public/270/gas+sensor+array+drift+dataset+at+different+concentrations.zip"
python3 -I -c "import zipfile; zipfile.ZipFile('data/uci_drift/drift270.zip').extractall('data/uci_drift/raw')"
echo "done: data/uci_drift/raw/batch1.dat .. batch10.dat"
