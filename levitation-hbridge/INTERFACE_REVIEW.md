# J3 control-interface revision — applied

The user approved moving the control interface out of the narrow space beside J2 and C11. The routed PCB now places **J3 along the bottom edge**, to the right of the bulk capacitors.

## Final arrangement

| Component group | Placement |
|---|---|
| J3 control header | Pin 1 at (107,110) mm; pin 8 at (124.78,110) mm; rotated 90° in the PCB plane |
| U4 buffer and C23 bypass | Centered near (115,101) mm |
| R24/R25 input pulldowns and R19 SD bias | Row above J3, at y=106 mm |
| C22 logic-rail bulk | Near (110,102.5) mm |
| D2 protected auxiliary-rail entry | Near (127.8,100.5) mm |
| C24 auxiliary bulk | Near (134.5,103) mm |
| TP4 protected +12 V / TP5 ground | Beside the header and auxiliary entry |

The J3 pad row is **4 mm from the bottom board edge**. Its courtyard ends at y=111.77 mm, leaving 2.23 mm to the edge at y=114 mm. Eight silkscreen legends identify the pins in the same order as the unchanged schematic: `12V, 3V3, G, A, B, SD, IS, G`. The first pin is external **+12V_IN**; TP4 measures protected +12V after D2. Full interface names and firmware logic are in `BRING_UP.md`.

The buffer, input pulldowns, bypass and SD bias are grouped with the header. The power-stage FETs, gate components, ceramics, shunt and sense amplifier retain their placements. The board title and bench-supply legend moved left to make room for the control interface.

## What this improves

Previously J3's courtyard was only 1.3814 mm from J2 in the horizontal direction and 1.20 mm vertically from C11's bounding box. Those assembly clearances did not establish room for fingers or a cable. The new edge location gives the harness a direct path off the board without passing the tall bulk capacitors or bus-entry terminal.

The existing header still **mates vertically**. Rotating it in the board plane does not make it a right-angle connector. The actual mating plug dimensions, cable bend radius, strain relief and enclosure opening remain unprovided, so physical mating fit is not claimed as qualified.

## Verification

See `VERIFICATION.md` and `reports/verification.json` for native ERC/DRC, exact net membership, filled-zone connectivity and gate/sense checks on this revision. `reports/interface_placement.json` records the moved footprints. No qualified current rating or thermal/transient release is implied by the connector move.
