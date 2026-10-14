# poc_lev — levitation-coil H-bridge

KiCad 10 project for one nominal 60 V, bidirectional coil-driver channel. Built from the supplied brief, with the user's approved Bourns Kelvin pickup and revised component bands. No purchases or paid external services were used.

**Engineering review package. Hardware has not been built or powered.** The 30 A target, transient envelope and <5 nH commutation-loop target are not qualified. See the open release items in [DESIGN_NOTES.md](DESIGN_NOTES.md), especially the unknown charged-pack voltage, unmeasured coil, INA240 transient limit, heatsinks and requested human driver-pinout signoff.

The follow-up [hardware qualification review](HARDWARE_QUALIFICATION.md) includes conditional transient, ripple and thermal calculations. The user confirmed that no assembled board exists; physical qualification is blocked until hardware is available.

The approved [J3 edge-placement revision](INTERFACE_REVIEW.md) is applied: the header, control buffer, input resistors and auxiliary rail-entry components are regrouped near the bottom edge.

## Open and review

Open `poc_lev.kicad_pro` with KiCad 10.0.3 or later. The schematic is one flat sheet; the PCB is a routed four-layer, 146 × 96 mm board. Standard KiCad symbol/footprint libraries are required. Project-specific libraries are included and use `${KIPRJMOD}` paths.

- `poc_lev.kicad_sch` — editable schematic; exact 34-net specification.
- `poc_lev.kicad_pcb` — editable board, filled copper and four mounting holes.
- `poc_lev.kicad_pro`, `poc_lev.kicad_dru` — project settings and layout rules.
- `poc_lev.kicad_sym`, `lib.pretty/`, library tables — local symbols and footprints.
- `BOM.csv` — 64 electrical parts plus six test points and four mounting holes, including required component ratings.
- `VERIFICATION.md`, `reports/verification.json` — measured results and method.
- `DESIGN_NOTES.md` — source corrections, calculations, stackup and release items.
- `BRING_UP.md` — control pinout, current sign, logic states and required bench-test ladder.
- `reports/schematic-preview.png`, `reports/pcb-preview.png` — review images; native files remain authoritative.
- `sources/` — supplied brief and source documents/figures used during the review.

No fabrication order has been placed. No Gerber set is represented as approved for fabrication.

## Validation

On this Mac, run `zsh scripts/check.sh`. This invokes native KiCad ERC, native DRC and an independent parser that reconstructs schematic connectivity from wire/pin/label geometry, cross-checks the native XML netlist and checks the PCB pad mappings. Gate-loop measurements include component pad spans and the explicit source-return traces; via traversal contributes the nominal 1.6 mm board thickness. Parallel copper-plane returns are not assigned an invented length or inductance.

The matching requirement is checked within each half-bridge. The two shunt-to-filter copper paths are explicitly length matched. Decoupling distances are pad-center placement measurements; they are not field-extracted inductance values. Native DRC enforces 0.25 mm courtyard clearance and prohibits inner-layer tracks.

## Rebuild sources

The native files are ready to open without Python. Scripts are also supplied for reproducibility. `scripts/rebuild.sh` **overwrites the generated schematic and PCB**, so save any manual edits elsewhere first and close KiCad.

The build uses free, local software: KiCad 10.0.3, its bundled Python 3.9/pcbnew/wx, and NumPy, SciPy and Shapely in `.venv`. The virtual environment itself is not part of the delivery archive. On the build machine it was created with:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
zsh scripts/rebuild.sh
```

`KICAD_CLI`, `KICAD_PYTHON` and `KICAD_SITE_PACKAGES` can override the macOS tool locations. The source scripts also contain the installed standard-library location; adapt it if building on another operating system. No cloud autorouter or account is needed.
