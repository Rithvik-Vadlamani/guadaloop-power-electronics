# MV24 Rev F1 — compact prototype candidate

Rev F1 implements the agreed minimal-change revisions to Rev F, except precharge. It preserves the original CSD19532Q5BT MOSFETs, all component positions, connector positions, mounting holes and board outline. Rev F is preserved separately. No board has been built or tested.

## What changed

| Item | Rev F | Rev F1 | Purpose |
|---|---|---|---|
| L1 | 10 µH, CPRX3231L-100MC | 15 µH, CPRX3231L-150MC | Coordinate inductance with the reduced switching frequency to limit ripple. Same package family and placement; revised terminal slots. |
| R6 | 75 kΩ | 100 kΩ, RT0805BRD07100KL | Reduce nominal switching frequency from approximately 133 kHz to 100 kHz, reducing gate-drive demand and frequency-dependent losses. |
| R10 | 6.81 kΩ | 8.2 kΩ, RC0805FR-078K2L | Retune compensation for the revised power stage. C26 remains 3.3 nF. |
| Copper | 35/15.2/15.2/35 µm | 70/35/35/70 µm | Improve conduction and heat spreading without enlarging the board. |
| MOSFET cooling paths | Original copper and vias | Local VIN copper extended, small bottom SW island, 37 additional thermal vias | Transfer heat away from the existing MOSFET packages. |
| Surface finish | OSP | ENIG | Flat assembly surface compatible with the specified filled-and-capped in-pad via process. |

There are still **51 fitted electronic/connector parts: three substitutions, zero added fitted parts**. The 63 PCB footprints also include six test points, four mounting holes and two unpopulated snubber positions. Vias are board features, not additional BOM components. External cooling equipment is separate from that count.

## Files

- `KiCad/MV24_RevF1.kicad_pro`: native editable project with local libraries/models.
- `Procurement/BOM.csv`: updated exact-part prototype BOM. Prices and availability have not been refreshed; this is not a purchase-ready quotation.
- `Documentation/Board.png` and `Documentation/Schematic.png`: reviewed previews.
- `Documentation/Engineering-notes.md`: design rationale, calculation scope and remaining uncertainties.
- `Documentation/Fabrication-and-test.md`: required PCB process, cooling fixture and staged test plan.
- `Verification/final-native/`: final ERC, DRC, native netlists and independent connectivity reports.
- `Verification/final-audit.json`: unchanged-layout/MOSFET/BOM comparison and report freshness checks.
- `Manufacturing/`: reviewed four-layer Gerbers, plated/non-plated drills, fabrication requirements and a selective filled-via map.
- `Assembly/`: reconciled 51-part BOM/placements, labeled assembly drawing and populated-variant stencil artwork with process-review instructions.

## Status

Native KiCad 10.0.3 ERC and DRC pass with no reported violations, unconnected items or schematic parity findings. Independent schematic/PCB connectivity and pad-map checks pass. All 154 tracked baseline files are unchanged. These checks establish consistency and routing-rule compliance, not power performance or safety qualification.

The averaged loop screen supports the chosen compensation as a prototype candidate. Thermal screening still indicates substantial heating and sensitivity to airflow/model resolution. **Continuous 24 V / 20 A operation is a design target, not an established rating.**

Precharge and the associated battery connection/fusing decisions are intentionally deferred as a separate scope. Do not directly hot-plug the battery into this candidate. The board-only fabrication/assembly handoff is prepared independently for fabricator DFM and a supervised bench prototype; it does not wait for a battery-interface redesign. Vendor process acceptance and assembler stencil/orientation review remain required before ordering. No hardware-performance or battery-use release is implied.
