# Verification record — poc_lev

Verified with KiCad 10.0.3 on 2026-09-06. Native files, not preview images, are the connectivity authority. See `reports/verification.json` for numerical detail and hashes of the checked design files.

## Completed file checks

| Check | Result |
|---|---|
| Native schematic ERC | 0 errors, 0 warnings |
| Independent reconstruction from schematic pin/wire/label geometry | Exact normative net membership |
| Native XML netlist versus independent reconstruction | Exact match |
| PCB pad nets versus schematic | Exact match |
| Electrical components / total physical items | 64 / 74 |
| Nets / connected component pins | 34 / 168 |
| Native PCB DRC | 0 violations, 0 unrouted connections |
| Courtyard clearance | 0.25 mm rule passes |
| Control interface | J3 along bottom edge, pin 1 (107,110) to pin 8 (124.78,110) mm; 4 mm from pad row to edge |
| FET order and pitch | Q2, Q1, Q4, Q3; 25 mm; all 0° |
| Copper stack | Four layers, 70 / 35 / 35 / 70 µm copper |
| Inner copper | GND and +60 V zones; no inner-layer tracks |
| C1–C10 BOM voltage | 100 V mandatory on every line |
| Bridge ceramics | Closest capacitor-pad to FET drain/source-pad centers: 4.499–4.733 mm, within 5 mm |
| Bootstrap capacitor placement | Both VB/VS pad-center distances within 3 mm |
| Driver VCC capacitor placement | Both VCC/COM pad-center distances within 5 mm; direct front-layer copper paths, no intervening vias required |
| Shunt to input-filter pair | 7.349 / 7.349 mm |

## Gate routing measurements

| FET | Turn-on complete loop, mm | Turn-off complete loop, mm | Turn-on branch copper, mm | Turn-off branch copper, mm |
|---|---:|---:|---:|---:|
| Q1 | 34.830 | 34.580 | 16.184 | 13.734 |
| Q2 | 34.521 | 34.285 | 23.253 | 20.817 |
| Q3 | 34.830 | 34.580 | 16.184 | 13.734 |
| Q4 | 34.520 | 34.285 | 23.252 | 20.817 |

All complete loops are below 35 mm. Turn-off is shorter than turn-on both as copper-only branches and when component pad spans are included. Turn-on mismatch is 0.895% for leg A and 0.898% for leg B, using `(longer − shorter) / shorter × 100`; both are below 10%.

The independent trace graph includes T junctions, a 1.6 mm traversal for each through via, resistor pad spans and, for turn-off, diode pad spans. The high-side source returns have an explicit bottom-layer segment and one via; the low-side returns have explicit front-layer tracks. Parallel filled copper is present but is not assigned an artificial path length. Length matching is a geometric check, not a measurement of driver timing or gate inductance.

## Scope of the geometry claims

Ceramic and decoupling proximity values above are **placement distances**, not copper-route lengths. The JSON report also lists the actual front-only driver-capacitor routes: these range from 2.400 to 8.497 mm. The bootstrap and VCC loops have not been field extracted. The bridge ceramic check uses the nearest drain/source pad of a FET in the corresponding leg, and does not claim that both capacitor terminals are within 5 mm of both commutating power nodes.

The explicitly matched sense paths run from the Bourns Kelvin pickup to R12/R13. The short fanout after the differential filter is separate and is not claimed to have equal total length. The user-approved Bourns part has two physical terminals; the four PCB net names are implemented using two manufacturer-sized force lands and two inner-edge sense pickups with local net-tie groups.

The nominal switch-node corridors have 12 mm zone width, parallel outer-layer copper and distributed through-via stitching. Native filled-zone connectivity passes. Pad necks, antipads and clearance cutouts reduce the local copper section; a nominal zone width does not establish a 30 A temperature-rise rating.

## Checks requiring physical data or separate qualification

- The **<5 nH commutation-loop target remains unverified**. No field solver or hardware inductance measurement was performed.
- Charged-pack voltage Q6 and coil R/L A1 remain unresolved, as in the supplied brief.
- The specified INA240, MOSFET and capacitor transient margins require resolution before pack/coil operation. The carried-forward 97.5 V example exceeds the INA240's 90 V absolute input limit; using 10 mH gives 99.915 V at nominal capacitance and 107.604 V at −20% capacitance. See `HARDWARE_QUALIFICATION.md` for model assumptions and additional ripple/thermal checks.
- Heatsink envelopes, operating temperature, capacitor ripple performance, switching waveforms and 30 A operation are untested.
- The brief explicitly requested a human driver-pinout check. Archived package/timing figures are supplied for that review. No human signoff is represented as completed.

These items are release holds documented in `DESIGN_NOTES.md`; clean ERC/DRC does not close them. Follow `BRING_UP.md` before any powered testing. No fabrication order or component purchase has been made.

## Files and reproducibility

`reports/erc.rpt` and `reports/final-drc.json` are native KiCad reports. `scripts/verify_design.py` asserts the reported connectivity and quantitative layout checks; it fails if a checked requirement regresses. `scripts/check.sh` regenerates the native reports and reruns the independent checks. `scripts/rebuild.sh` regenerates the design from its source scripts.
