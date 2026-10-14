# Hardware qualification — NOT RELEASED

Status on 2026-09-06: **physical qualification blocked because no assembled board exists**. The user confirmed that bench equipment is available. No board has been powered, no instruments have been operated, no hardware measurements have been taken, and no purchases have been made.

Completed in this review: component-limit review, 24 conditional shutdown scenarios, six thermal budgets, six capacitor-ripple cases and lossless energy thresholds. These are calculations, not hardware qualification. Reproduce with `.venv/bin/python scripts/qualify_analysis.py`; numerical inputs/results are in `qualification/analysis.json` and the accompanying CSV files.

## Correction to the previous report

The earlier **100.1 V** result was an arithmetic error. For 60 V, 10 mH, 30 A and 1410 µF:

`Vfinal = sqrt(60² + 0.010 × 30² / 0.001410) = 99.914857 V`.

This nominal result is below 100 V by only 0.085 V. With capacitance at −20%, the result is **107.604477 V**. The ZLH series specifies ±20% initial capacitance tolerance. This calculation ignores dissipation, clamp action and regeneration into the supply; it is an energy-transfer scenario, not a prediction that the actual board reaches this voltage. [Rubycon ZLH](https://www.rubycon.co.jp/wp-content/uploads/catalog-aluminum/ZLH.pdf).

## Regenerative shutdown and sensing limits

The physically defined scenario is a **connected coil, all four gates off, and a DC source that cannot absorb returned energy**. It is not the act of unplugging an energized coil: opening the coil wiring introduces arcing and a different circuit.

For a dissipative model, solve until coil current reaches zero:

`L di/dt = −Vbus − Rcoil i − 2 Vf`

`C dVbus/dt = i`

The model uses the unmeasured 10 mH / 2 Ω coil assumption and an illustrative constant 1 V drop per conducting body diode. It excludes TVS conduction, ESR/ESL, wiring inductance, switching recovery, temperature dependence and source absorption.

| Starting bus / current | Bulk C | Lossless energy scenario | Dissipative model, no TVS | Current-decay time |
|---|---:|---:|---:|---:|
| 60 V / 30 A | 1410 µF | 99.915 V | 87.742 V | 2.746 ms |
| 60 V / 30 A | 1128 µF (−20%) | 107.604 V | 93.730 V | 2.641 ms |

Numerical verification independently checks the lossless energy identity, conservation of capacitor/coil/diode energy in every simulated case, and a halved integration step. Those checks pass. They validate the numerical implementation of the stated model, not the assumptions or physical assembly.

INA240 recommended common-mode operation is −4 to +80 V; absolute limits extend to −6 and +90 V. With negative coil current under the project's sign convention, the shunt is on the high return path during diode regeneration and its common mode can be approximately `Vbus + Vf`. Positive-current shutdown places it near the low-side diode instead. Both polarities therefore need testing. The differential input capacitor does not clamp common mode. [TI INA240 specifications](https://www.ti.com/lit/ds/symlink/ina240.pdf).

The fitted 5.0SMDJ70A has a 70 V standoff, breakdown range of 77.8–86.0 V, and a specified 113 V maximum clamp at 44.3 A for its stated pulse waveform. These specifications do **not** guarantee an 80 V bus ceiling. A linearized TVS estimate is not accepted as a guaranteed clamp model, and none was used to award a pass. [Littelfuse 5.0SMDJ](https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_5_0smdj_datasheet.pdf?assetguid=2b2f4a8c-2e81-4894-8d41-3d748bb79e68).

**Disposition: transient qualification is not demonstrated.** Establish maximum pack voltage and the supply's absorption behavior, then resolve the sensor/bus clamp envelope with component tolerances and wiring parasitics. Keep input common-mode voltage within the recommended range with engineering margin; absolute maximum is not an operating target. A clamp/braking-path or component-rating change may be required. No such redesign has been silently substituted into the specified circuit.

## Bulk capacitor ripple

For constant coil current, active/freewheel unipolar PWM, and a source that supplies only the average current, the capacitor bank supplies the AC component of a 0/I bus-current pulse:

`Icap,rms = Icoil × sqrt(D × (1 − D))`.

| Coil current | Active duty | Conditional bank ripple | Each capacitor, equal sharing |
|---|---:|---:|---:|
| 10 A | 0.75 | 4.330 A RMS | 1.443 A RMS |
| 16 A | 0.75 | 6.928 A RMS | 2.309 A RMS |
| 30 A | 0.75 | 12.990 A RMS | 4.330 A RMS |
| 30 A | 0.50 | 15.000 A RMS | 5.000 A RMS |

The specified 100 V / 470 µF / 16 × 31.5 mm ZLH part is rated 2.4 A RMS at 105°C and 100 kHz. Three parts give 7.2 A only under ideal sharing at that rating condition. The listed frequency factor for this capacitance range is 0.94 at 10 kHz and 1.00 at 100 kHz; no exact 16 kHz factor is invented here. [Rubycon ZLH tables](https://www.rubycon.co.jp/wp-content/uploads/catalog-aluminum/ZLH.pdf).

**Disposition: the bank fails the conditional 30 A ripple screen if it carries the modeled AC current.** This is not a measured capacitor current. PWM sequence, source impedance, ceramics, frequency spectrum, unequal sharing and temperature change actual stress. Measure each bulk capacitor's ripple and temperature with the intended supply/harness. If that screen represents the intended operating condition, revise the bank/ripple-current path before high-current operation.

## Thermal budget

The source brief's hot on-resistance estimate and switching-loss estimate are retained as assumptions:

`Pcond = I² × 0.00672 Ω × 0.75`

`Psw = 3.2 W × (I / 30 A) × (frequency / 16 kHz)`.

For an illustrative 40°C ambient and a **proposed, unapproved 125°C junction design target**, assume a 0.5°C/W interface and calculate:

`RθSA,max = (125 − 40) / (Pcond + Psw) − 0.34 − 0.5`.

| Current | Frequency | Estimated loss per hard-switching FET | Required sink-to-ambient resistance |
|---|---:|---:|---:|
| 10 A | 16 kHz | 1.571 W | ≤53.28°C/W |
| 16 A | 16 kHz | 2.997 W | ≤27.52°C/W |
| 30 A | 16 kHz | 7.736 W | ≤10.15°C/W |
| 30 A | 32 kHz | 10.936 W | ≤6.93°C/W |

IRF100B201 specifies 0.34°C/W maximum junction-to-case resistance. The 0.5°C/W case-to-sink figure is typical for a flat greased interface, not a guaranteed value for an insulating pad. The device's 175°C absolute junction limit is not the proposed design target. Its 4.2 mΩ maximum resistance is specified at 25°C; the brief's 6.72 mΩ hot estimate is not a new guaranteed maximum. [Infineon IRF100B201](https://www.infineon.com/assets/row/public/documents/24/49/infineon-irf100b201-datasheet-en.pdf).

**Disposition: heatsink selection and temperature testing are still required.** Actual PWM behavior determines which FETs hard-switch. Reverse-recovery and other losses are not fully modeled. Insulation, mounting, airflow and mutual heating must be included. No heatsink envelope has been approved against this PCB. The two 2 oz copper layers do not qualify the thermal assembly.

## Remaining physical qualification record

Every item below is **NOT RUN**. Record board revision/serial, exact fitted parts, operator, date, instrument models/calibration, probe arrangement, uncertainty, ambient, supply/load conditions and raw captures. `qualification/measurement_record.json` contains empty fields; do not substitute simulated values.

| ID | Required evidence | Release criterion / dependency |
|---|---|---|
| Q01 | Pack maximum voltage and source/BMS regenerative absorption | Establish Q6 and approved transient envelope |
| Q02 | Coil resistance versus temperature and inductance versus bias/current | Establish A1; validate the operating and energy model |
| Q03 | Human comparison of actual driver package/marking with lead diagram and SD timing; assembled polarity/continuity inspection | Pin mapping and disabled-state assembly signoff |
| Q04 | Actual heatsink/interface/clearance inspection; no unintended connection between live tabs | Mechanical fit and insulation verified |
| Q05 | Low-energy rail sequencing and SD/PWM truth-table captures | Correct supplies, all gates off with SD low, correct commanded polarity, bootstrap refresh |
| Q06 | Both polarities of known low current with ISNS/ADC captures | Correct sign and zero; define and meet the project's accuracy budget |
| Q07 | Gate-source and switch-node waveforms at each approved rung | No cross-conduction; margins to ratings; acceptable ringing and bootstrap droop |
| Q08 | Characterized commutation-loop impedance or validated extraction including terminals, vias, planes and package model | Demonstrate the specified <5 nH target; trace length alone is insufficient |
| Q09 | Bulk-capacitor ripple by device and frequency, bus ripple, temperatures | Within applicable derated component ratings with uncertainty/margin |
| Q10 | FET case/sink and PCB/connector/shunt temperatures at steady state | Meet approved ambient/junction and component-temperature limits |
| Q11 | Approved shutdown/regeneration and connection-transient tests with an energy-safe fixture | Meet the resolved voltage/current/energy envelope in both polarities |
| Q12 | Repeated operation at approved current/duty/frequency corners | Repeatable function and no rating violations; 30 A release requires all dependencies |

Do not start with a pack or a 30 A fault test. Follow the low-energy ladder in `BRING_UP.md`. Before inductive testing, establish the safe stop and energy-absorption method: setting SD low or disconnecting a source can itself return energy to the DC link. An ordinary bench supply may be unable to sink it. Do not deliberately open an energized coil connection to reproduce the lumped model above. The brief requires another person present for 60 V testing.

The <5 nH extraction, fabricated copper/current heating, assembly inspection and waveform/thermal tests cannot be closed by the analyses in this file. **There is no qualified operating-current rating yet, including 10 A.** Ten amperes is the brief's bring-up target after the lower-energy checks, not an already-approved operating point.
