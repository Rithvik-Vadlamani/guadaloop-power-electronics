# Rev F1 — prototype assembly handoff

Populate exactly 51 fitted components using `bom.csv` (one row per reference) or `grouped-bom.csv` (grouped purchasing list). Do not treat both lists as separate quantities. Do not substitute exact part numbers without review. Current prices and availability have not been checked.

## Included files

- `placements.csv`: native KiCad millimeter coordinates for all 51 fitted parts, including through-hole components. All are top-side. Coordinates use the global origin, X right and Y up; this board has negative Y values. No bottom-side mirroring or assembler-specific rotation conversion has been applied. Verify orientation and origin in the assembler's preview.
- `assembly-reference-map.svg/.png`: native component outlines with added assembly-only reference labels for parts whose Fab-layer reference was hidden. This drawing does not change copper or silkscreen.
- `assembly-drawing.svg/.png`: unmodified native Fab-layer drawing, retained for traceability.
- `stencil-populated/`: top and bottom paste Gerbers for the fitted variant. R16/C27's four aperture flashes have been removed using native X2 component attributes; all remaining aperture geometry was checked unchanged after re-export. Bottom paste is intentionally empty. The stencil maker still needs to review aperture area/profile and stencil thickness for U1/Q1/Q2.
- `stencil/`: unmodified native paste export retained for engineering traceability ONLY; it contains DNP apertures and is excluded from the handoff ZIP. Do not use this raw directory to order the populated-variant stencil.
- `assembly-netlist.xml`: source netlist snapshot, for engineering traceability.
- `native-unfiltered-bom.csv`: raw export reference ONLY. It includes six bare test pads and is NOT the purchasing or population list.

## Population and inspection notes

1. R16 and C27 are **DNP** (do not populate). TP1–TP6 are bare copper test pads with no purchased pins installed. H1–H4 are mounting-hole features, not electronic parts.
2. Q1/Q2 remain CSD19532Q5BT. Confirm pin 1, gate/source/drain orientation and exposed-pad soldering against the retained local footprint and manufacturer package drawing. U1 requires the same pin-1/exposed-pad attention. Assembly coordinates are not a replacement for pin-map inspection.
3. Verify C1–C8 and C13–C15 polarity; follow plus marks and numbered pad/net identity, not the drawn half-circle shading alone. The exact radial capacitors and all through-hole components need lead insertion/hand- or selective-solder operations rather than ordinary SMT placement alone.
4. Use CPRX3231L-150MC for L1, not the old 10 µH part. Confirm its terminals fit the two 4.0 × 8.8 mm plated slots. Keep its existing position and orientation.
5. Filled, planarized and copper-capped vias are required at the selected locations in the manufacturing package. Review pad flatness, solder coverage and voiding under the MOSFETs and controller; an image rendering is not evidence of assembly quality.
6. Review stencil thickness, local aperture reductions/windowing and the reflow profile for the heavy-copper board with the assembler. The native paste artwork is a starting point, not a qualified stencil process. Use inspection appropriate to hidden solder joints.
7. Preserve connector polarity and mating orientation. Inspect input/output shorts and solder quality before first power. Read `Documentation/Fabrication-and-test.md` for current-limited bring-up and cooling requirements.

The generic export initially reported a coverage mismatch because its BOM included TP1–TP6 while KiCad correctly excluded them from placements. The reviewed fitted BOM removes those six bare pads and reconciles all remaining 51 references, exact MPNs, values and footprints with the purchasing list. Every placement was checked against native position, side and rotation.

External fans, fixture hardware and the deferred battery/precharge interface are not included in this 51-part board BOM. No assembly order has been placed.
