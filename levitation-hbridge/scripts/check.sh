#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
KICAD_CLI="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
mkdir -p reports
"$KICAD_CLI" sch export netlist --format kicadxml -o reports/schematic.net.xml poc_lev.kicad_sch
"$KICAD_CLI" sch erc --exit-code-violations -o reports/erc.rpt poc_lev.kicad_sch
"$KICAD_CLI" pcb drc --exit-code-violations --format json -o reports/final-drc.json poc_lev.kicad_pcb
python3 scripts/verify_design.py
python3 scripts/write_verification.py
