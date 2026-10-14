# Rev F1 — bare-board prototype fabrication package

Scope: fabricate the existing compact converter PCB. External battery/precharge work is deferred and is not part of this package. This is prototype artwork for fabricator DFM/quotation, not hardware qualification or authorization to place an order.

## Fabrication instructions — required with the Gerbers

| Property | Requirement |
|---|---|
| Board | MV24 Rev F1, 150 × 110 mm, rectangular closed outline |
| Stack | Four copper layers: F.Cu / In1.Cu / In2.Cu / B.Cu |
| Nominal total thickness | 1.60 mm |
| Copper | 70 / 35 / 35 / 70 µm (nominal 2 / 1 / 1 / 2 oz) |
| Finish | ENIG |
| Mask | Both sides; use supplied openings |
| Legend | Top only; bottom legend is intentionally empty |
| Plated features | 261 total: 255 round holes and six slots |
| Non-plated features | Four 3.20 mm mounting holes |
| L1 plated slots | Two 4.0 × 8.8 mm overall slots; do not interpret as 4.0 mm round holes |
| J1/J2 plated slots | Four 0.6 × 1.7 mm overall slots |
| Via-in-pad process | Resin fill, planarize, and copper cap the 38 selected vias in `filled-vias.csv`; see `filled-vias-map.png` |

The 38-via process list is a conservative manufacturing selection including existing vias and vias adjacent to component pads, plus two test-pad vias. It is **not** a count of newly added vias. The board revision added 37 vias total, of which 12 are directly inside the MOSFET pads. No further vias were added while preparing this handoff.

All selected vias are 0.30, 0.40, 0.45 or 0.50 mm finished hole diameter. Apply the copper-capped process before final surface finishing. Ordinary solder-mask tenting or ink plugging is not a substitute at these locations. Other vias may follow the supplied mask artwork. A vendor may propose filling all small vias for process simplicity, but must confirm cost and process before approval. **Do not fill component lead holes, connector slots, L1 slots or mounting holes.**

The CSV uses the same absolute millimeter coordinate frame as Gerber/Excellon: X positive right; Y negative below the design origin. Do not negate Y a second time. Native source positions have finer precision than the drill export; at two drill centers, rounding differs by 0.0005 mm. Match centers within the exported 0.001 mm precision.

Native nominal dielectric thicknesses are 0.2104 / 0.9392 / 0.2104 mm, with nominal 0.015 mm solder mask per side. The fabricator must confirm a realizable equivalent stack, finished copper, insulation material, slot tolerance, mask webs and filled/capped pad planarity. Do not silently substitute a standard thin-copper process.

## Files and review

- Nine `.gbr` files: four copper, two mask, two silkscreen, one outline. Empty bottom silkscreen is deliberate.
- `*-PTH.drl` and `*-NPTH.drl`: separate plated/non-plated Excellon drill files, millimeters.
- Drill maps and report: supporting inspection artifacts, not extra machining layers.
- `*-job.gbrjob`: native layer/stack metadata.
- `filled-vias.csv` and `filled-vias-map.png`: required selective fill/cap instructions.

Actual Gerbers were parsed and rendered with Gerbonara. Every exported hole/slot was compared against native KiCad geometry, and the four outline segments were checked for the intended closed 150 × 110 mm rectangle. Four copper layers, masks, legend, outline, drill layers and power-stage details were visually reviewed. Reports and image hashes are retained under `Verification/manufacturing-review/`.

## Before fabrication

Obtain fabricator DFM confirmation of the stack and fill/cap process; inspect its production-file preview. The board includes fine-pitch controller pads and heavy copper. Ask the vendor to flag any clearance/mask/etch constraints rather than modify them silently. Source design ERC/DRC pass, but that does not replace the vendor's process-specific DFM.

No order has been placed. Initial operation is limited to a supervised, current-limited bench setup with the documented cooling plan. Direct battery connection, continuous 20 A performance and fault qualification are not approved by this package.
