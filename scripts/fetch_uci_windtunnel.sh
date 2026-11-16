#!/bin/sh
# Fetch the UCI wind-tunnel gas sensor dataset (id 251, 8.4 GB zip; 107 GB if extracted, so it
# is NOT extracted -- sw_enose/windtunnel.py reads recordings straight from the zip).
set -e
cd "$(dirname "$0")/.."
mkdir -p data/uci_windtunnel
curl -sSL -o data/uci_windtunnel/windtunnel251.zip \
  "https://archive.ics.uci.edu/static/public/251/gas+sensor+arrays+in+open+sampling+settings.zip"
python3 -I -c "import zipfile; bad = zipfile.ZipFile('data/uci_windtunnel/windtunnel251.zip').testzip(); print('CRC OK' if bad is None else 'BAD: ' + bad)"
