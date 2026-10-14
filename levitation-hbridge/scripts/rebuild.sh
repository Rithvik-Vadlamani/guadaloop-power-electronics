#!/bin/zsh
# Rebuild generated design from the checked-in source scripts. Overwrites native files.
set -euo pipefail
cd "${0:A:h:h}"
if [[ -n "$(find . -maxdepth 1 -name '*.lck' -print -quit)" ]]; then
  print 'Close KiCad before rebuilding.' >&2
  exit 1
fi
KICAD_PYTHON="${KICAD_PYTHON:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3}"
export PYTHONPATH="${KICAD_SITE_PACKAGES:-/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages}"
if [[ ! -x .venv/bin/python ]]; then
  print 'Create a virtual environment from KiCad Python and install numpy, scipy, shapely first. See README.md.' >&2
  exit 1
fi
mkdir -p reports
python3 scripts/build_schematic.py
"$KICAD_PYTHON" scripts/build_board.py
.venv/bin/python scripts/route_board.py
.venv/bin/python scripts/power_stitch.py
.venv/bin/python scripts/finish_board.py
zsh scripts/check.sh
