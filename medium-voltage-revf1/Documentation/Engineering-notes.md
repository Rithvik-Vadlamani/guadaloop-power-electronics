# Rev F1 engineering decisions

## Preserve the compact MOSFET implementation

Q1 and Q2 remain exact CSD19532Q5BT devices with unchanged pads, location and orientation. They are not replaced by Rev G's larger implementation. Their 100 V absolute maximum is not an operating target or a guarantee against switching overshoot. At the project-assumed 67.2 V full charge, only 32.8 V separates the DC input from that absolute maximum; cable transients and switch-node ringing must be measured. The battery's actual maximum charge voltage and BMS behavior remain unverified manufacturer specifications.

The original snubber positions R16/C27 remain DNP. Their values should be selected from measured ringing rather than guessed. This is a planned bench-tuning provision, not a fitted suppression circuit.

## Coordinated frequency, inductor and compensation change

Reducing switching frequency alone would increase inductor ripple. R6 and L1 therefore change together. Using the ideal steady-state CCM relation ΔIL = Vout × (1 − Vout/Vin)/(L × fs), at 67.2 V input and 24 V output:

| Nominal calculation | Rev F | Rev F1 |
|---|---:|---:|
| Switching frequency | 133.3 kHz | 100 kHz |
| Inductance | 10 µH | 15 µH |
| Inductor ripple, peak-to-peak | 11.57 A | 10.29 A |
| Peak inductor current at 20 A output | 25.79 A | 25.14 A |
| Total triangular output-capacitor ripple RMS | 3.34 A | 2.97 A |

These are nominal calculations, not worst-case device limits. Inductance falls with bias and temperature, frequency varies, and real switching waveforms include parasitics. The new inductor's maximum published DCR is 1.60 mΩ versus 1.05 mΩ for the old value: less ripple and lower frequency come with higher winding resistance, not a free reduction in every loss.

Gate-drive charge demand scales approximately with switching frequency for fixed drive conditions. Reducing frequency by 25% reduces that component of demand by approximately 25%; it does not imply total board loss falls 25%. The LM5146 VCC table's 20 mA test load is not a hard output-current limit.

R10 = 8.2 kΩ was selected by the project's existing averaged CCM loop equations. The declared sweep covers independent R10/R11 and capacitor tolerances, selected output-capacitance/ESR/load corners, frequency uncertainty, and assumed inductance reduction. It found 6,144 downward unity-gain crossings, none missing, and minimum phase margin approximately 46.94°. That is model evidence only. Some modeled light-load conditions can enter DCM in real hardware; startup, current limit, nonlinear transients, constant-power loads and actual loop bandwidth are not established by this screen. See `Verification/loop-candidates.json` and its script for exact assumptions.

## Thermal and fabrication changes

The stack changes to 70/35/35/70 µm copper, with a nominal 1.60 mm total thickness. Q1's bottom VIN copper now reaches the thermal-via region. Q2 gains a small bottom SW copper island; top-side switching-node geometry remains unchanged. The added vias comprise 23 VIN and 14 SW connections. Twelve of those are within MOSFET drain solder pads and require filled, planarized, copper-capped manufacture.

These copper regions are electrically live: Q1's heat-spreading copper is VIN and Q2's is the switching node. Do not clamp a common bare conductive heatsink across them. Any future cold plate needs properly rated electrical insulation and a reviewed mechanical interface.

The thermal model uses assumed component losses totaling 16.2 W, 30 °C ambient, and assumed convection coefficients. It is not calibrated to the board or a fan. At h = 50 W/m²K on both faces, the 0.5 mm mesh predicts average copper temperatures under Q1/Q2 of about 131.8/129.8 °C; the 1 mm mesh predicts 149.4/142.3 °C. These are not junction temperatures, and the mesh dependence is too large to claim convergence. Natural-convection screening is clearly unfavorable. Consequently forced airflow is required for staged testing, but its sufficiency at 20 A is **unassessed**. Actual loss, airflow, case/junction temperature and ambient dependence must be measured. Preserve the 20 A target while stopping tests below unsafe temperatures.

## Verification and limitations

- Schematic connectivity compared with pre-existing independent intent: pass.
- PCB connectivity and pin-to-pad checks: pass.
- ERC: zero reported violations; previously ignored ERC categories were restored to warnings and causes resolved rather than excluded.
- DRC: zero reported violations, unconnected items and parity findings after refill.
- Board outline and every footprint placement: unchanged from Rev F.
- Exact MOSFET values/properties/pads: unchanged.
- Fitted BOM differences: L1, R6 and R10 only.
- Visual inspection: schematic, 3D preview, all four copper layers and top mask reviewed. This is not a physical assembly or Gerber/drill fabrication review.
- No hardware test, measured switching-stress result, thermal qualification, EMC result or final manufacturing approval exists.

The readable schematic branch cleanup removes inherited four-way junction warnings without changing endpoints. Native reports retain their own `visual_review`/`physical_review` fields; the separate review record documents the narrower image inspection actually performed.

## Sources

Original source PDFs are retained in `Sources/`. Exact replacement values have accepted page-bound records in `Verification/evidence/`.

- [TI LM5146](https://www.ti.com/lit/gpn/LM5146): oscillator, gate supply, compensation and layout guidance.
- [TI CSD19532Q5B](https://www.ti.com/lit/ds/symlink/csd19532q5b.pdf): unchanged MOSFET ratings and package.
- [CODACA CPRX3231L](https://www.codaca.com/Productsctr_CPRX3231L.html): 15 µH part and dimensional family; original dated PDF retained locally.
- [Yageo R6 exact part](https://www.yageogroup.com/component-documentation/download/specsheet/RT0805BRD07100KL) and [R10 exact part](https://www.yageogroup.com/component-documentation/download/specsheet/RC0805FR-078K2L).
- [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) and [via covering](https://jlcpcb.com/help/article/pcb-via-covering): candidate fabrication process. A fabricator must confirm the final stack, clearances and filled/capped via process before ordering.
