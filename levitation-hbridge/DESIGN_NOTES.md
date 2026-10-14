# poc_lev design record

This is a single-channel, four-MOSFET H-bridge for a nominal 60 V levitation coil. The engineering target is 30 A, with initial bring-up at 10 A. **The design is not a qualified 30 A assembly.** Pack voltage, coil parameters, transient behavior, heatsink fit/performance and the original brief's human pinout check remain release items.

## Decisions and source corrections

- The user approved retaining **CSS2H-2512R-L500FE with Bourns' Kelvin PCB pickup**, correcting the brief's description of it as a four-terminal component. The footprint has two main solder lands and separately named copper sense pickups connected inside the footprint using KiCad net-tie groups. The main lands are 1.80 × 3.40 mm with a 3.40 mm inner gap, from the manufacturer's drawing. The sense extensions are implementation dimensions; the manufacturer does not dimension their width in the drawing. [Bourns, page 2](https://www.bourns.com/docs/product-datasheets/css2h-2512.pdf).
- The user approved revising the horizontal bands to prioritize short gate loops while preserving 25 mm FET pitch and nearby bridge ceramics. The final arrangement is the deliverable; drivers and gate components occupy spaces between and around the FETs.
- Driver pinout: 1 IN, 2 active-low SD, 3 COM, 4 LO, 5 VCC, 6 VS, 7 HO, 8 VB. The SOIC lead drawing is on **page 5**, not page 1. Page 6's timing diagram shows both outputs low while SD is low. These pages were visually inspected; this does not substitute for the human signoff explicitly requested by the brief. R19 is included as the shutdown pulldown in the design. U1/U2 use the SOIC ordering code IR2184SPBF. [Infineon / International Rectifier PD60174 revG](https://www.infineon.com/assets/row/public/documents/24/49/infineon-ir21844s-datasheet-en.pdf).
- C24's normative netlist uses pin 2 as positive. A local polarized symbol and matching local footprint deliberately number the **positive lead 2**, preserving the netlist without reversing an electrolytic.
- INA240 SOIC pin 3 is REF2 and pin 7 is REF1. The board follows the supplied pin-level netlist: REF2 goes to 3.3 V and REF1 to ground. Their average is still 1.65 V. Pin 4 is NC and may be grounded. The SOIC and TSSOP pinouts are different. [TI INA240, page 3](https://www.ti.com/lit/ds/symlink/ina240.pdf).
- D8 uses a unidirectional zener/TVS drawing with pin 1 cathode at +60 V. D2 uses a Schottky symbol. All turn-off diodes have their anodes at the MOSFET gates.
- J1/J2 use the supplied local Molex footprint. Its pins are staggered: **12.70 mm in X and 13.00 mm in Y**, with 3.9624 mm drills. This is not a generic inline 12.7 mm terminal block. [Molex product drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/389/38969/389690002_sd.pdf).
- The user approved moving J3 and the control interface to the bottom edge. J3 pin 1 is (107,110) mm; pin 8 is (124.78,110) mm. U4, its bypass, input/SD resistors, auxiliary rail entry and supply test points are nearby. The existing vertical mating header is retained. See `INTERFACE_REVIEW.md`.
- The reference list comprises exactly 64 electrical components, four mounting holes and six test points. R15–R18 are intentionally absent. No components were bought.

## Arithmetic and limits

Inputs below come from the brief unless identified otherwise. Estimates are not measurements.

| Check | Expression | Result / interpretation |
|---|---|---|
| Sense voltage at 30 A | 30 A × 0.0005 Ω | 0.015 V |
| Sense gain | 0.015 V × 50 | 0.750 V |
| ISNS range at ±30 A | 1.65 V ± 0.750 V | 0.90–2.40 V |
| Shunt loss at 30 A | 30² × 0.0005 | 0.45 W |
| Differential RC pole | 1 / [2π × (10 + 10) Ω × 1 nF] | 7.96 MHz; primarily an RF filter |
| Bulk capacitance | 3 × 470 µF | 1410 µF nominal |
| Bleed power at 60 V | 60² / 22000 | 0.164 W; 2512 specified |
| Bleed time constant | 22000 × 0.001410 | 31.02 s |
| Bleed from 60 V to 1 V | 31.02 × ln(60) | 127.0 s; verify with a meter |
| Stored coil energy, example L=9.25 mH, I=30 A | 0.5 × 0.00925 × 30² | 4.1625 J |
| Ideal bus rise, same example | √[60² + 2 × 4.1625 / 0.001410] | 97.5 V, before tolerances and ringing |
| Same calculation using the stated ~10 mH assumption | √[60² + 0.010 × 30² / 0.001410] | 99.915 V; only 0.085 V below 100 V before tolerances |
| 10 A, L=9.25 mH | E=0.4625 J; √[60² + 2E/0.001410] | 65.2 V |
| Miller estimate, symmetric path | 310 pF × 60 V × 5.2 V / 45 nC | 2.15 V |
| Brief's asymmetric estimate | 2.15 × (4.7+3)/(10+3) | 1.27 V; parasitics are unverified |
| Ideal bootstrap droop from gate charge alone | 255 nC / 1 µF | 0.255 V; effective capacitance, leakage and duty also matter |
| Assumed 2 Ω coil at 30 A | I × R = 30 × 2 | 60 V average, with no allowance for semiconductor/wiring losses |
| Same coil at an effective 0.75 bus duty | 60 × 0.75 / 2 | 22.5 A steady state, neglecting losses |

The 9.25 mH example and the unmeasured “~10 mH” assumption are distinct. A current-source energy dump into bulk capacitance is not a transient clamp simulation. Capacitance tolerance, ESR/ESL, switch state, wiring inductance and the pack's ability to absorb regeneration all affect the result.

The brief's MOSFET estimates are about 1.6 W per hard-switching FET at 10 A and 7.7 W at 30 A, at 16 kHz. These are carried-forward estimates, not new thermal validation. Switching loss changes with frequency. No 30 A thermal release is implied by 2 oz copper or a passing DRC.

See `HARDWARE_QUALIFICATION.md` for the subsequent conditional transient, ripple and thermal analysis. The nominal 10 mH energy calculation above corrects the earlier 100.1 V arithmetic error. At −20% bulk capacitance, its lossless result is 107.604 V.

## Open release items

1. **Q6: maximum charged pack voltage.** Still unknown. Keep D8=5.0SMDJ70A as instructed. Its stated 113 V rated clamp is above the MOSFET/capacitor ratings; do not assume it protects every operating condition.
2. **A1: coil R/L.** Still unmeasured. Confirm the current/duty operating envelope and regenerative energy experimentally before relying on a 30 A target. Bootstrap high-side drivers also require refresh; unrestricted 100% duty is not an acceptable firmware operating mode.
3. **INA240 transient exposure.** TI specifies an 80 V recommended common-mode maximum and 90 V absolute maximum. The brief's 97.5 V energy example exceeds both. Resolve the transient envelope before coil/pack operation. [TI INA240, page 4](https://www.ti.com/lit/ds/symlink/ina240.pdf).
4. **Human driver review.** Verify the actual ordered package against the archived lead-assignment and timing pages. No physical board has been powered or tested.
5. **Thermal/mechanical validation.** Select actual individual heatsinks, check their envelopes against the nearby parts, and verify temperature at the intended current/frequency. MOSFET tabs are live drains. Insulate any arrangement that could join different drain nodes electrically. The brief's common-bar solution at 30 A remains a separate thermal/mechanical design.
6. **Layout qualification.** Read `reports/verification.json` and the generated verification summary. DRC does not establish commutation inductance, 30 A temperature rise or loop matching through a plane. A <5 nH claim requires a suitable extraction model or measurement.
7. **Procurement detail.** Unspecified passive MPNs remain unspecified. The BOM retains mandatory voltage/package/dielectric requirements, especially 100 V for C1–C10. Confirm effective bootstrap capacitance, capacitor ripple ratings, pulse ratings and component tolerances before ordering.

## Fabrication intent

Four layers, 146 × 96 mm board, nominal 1.60 mm overall thickness. Copper: F.Cu 70 µm, In1.Cu 35 µm, In2.Cu 35 µm, B.Cu 70 µm. Dielectrics: 0.20 / 0.97 / 0.20 mm; two nominal 0.01 mm solder-mask layers bring the encoded stack to 1.60 mm. The fabrication stack must be confirmed with the chosen vendor.

In1.Cu is a continuous ground zone and In2.Cu a continuous +60 V zone, with necessary antipads and no signal tracks. High-current switch/output routes use broad copper zones, with a via array into the shunt's bridge-side land and distributed stitching between parallel outer-layer switch-node corridors. Narrow tracks on SW_A/SW_B serve driver source reference and test/sense connections, not coil-current transport. Exact filled-pour geometry, including pad necks and clearance cutouts, must be assessed for current and temperature; a nominal 12 mm polygon alone is not a current rating.
