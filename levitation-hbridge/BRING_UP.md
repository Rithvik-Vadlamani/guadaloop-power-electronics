# Bring-up and firmware interface

No hardware testing has been performed. Close the release items in `DESIGN_NOTES.md` before energizing the board.

## Connector J3

| Pin | Signal | Requirement |
|---|---|---|
| 1 | +12V_IN | External gate-drive supply, before D2 |
| 2 | +3.3V | External regulated logic/INA supply |
| 3 | GND | MCU return |
| 4 | PWM_A_IN | 3.3 V MCU PWM, connector-side 10 k pulldown |
| 5 | PWM_B_IN | 3.3 V MCU PWM, connector-side 10 k pulldown |
| 6 | SD | Low disables both driver outputs; high enables switching |
| 7 | ISNS | 1.65 V nominal at zero current; +25 mV/A |
| 8 | GND | MCU return |

Positive current flows **SW_A → R1 → COIL_A → J1.2 → coil → J1.1 → SW_B**. Calculate `I_A = (V_ISNS - calibrated_zero_V) / 0.025`. Calibrate zero and gain; do not invert the sign in a feedback loop without confirming a known positive test current.

| SD | PWM_A | PWM_B | Settled bridge state |
|---|---|---|---|
| Low | X | X | All gates off |
| High | Low | Low | Q2/Q4 on; low-side recirculation |
| High | High | Low | Positive coil voltage |
| High | Low | High | Negative coil voltage |
| High | High | High | High-side recirculation; bootstrap limitations apply |

Switching transitions include driver deadtime and propagation delays. These rows are steady logic states, not permission to hold either high-side MOSFET on indefinitely. Start at 16 kHz. Enforce bootstrap refresh, valid supply sequencing and bounded duty. The brief specifies a 32 kHz ceiling; it does not establish thermal operation there. Sample ISNS after switching disturbances have settled and verify the timing on the actual circuit.

Before inductive testing, resolve the regeneration/clamp and capacitor-ripple findings in `HARDWARE_QUALIFICATION.md` and define an energy-safe stopping method. A bench supply may not absorb returned energy; SD low can initiate regeneration.

## Required ladder

1. With power disconnected, verify component orientation, shunt pickup continuity, FET/driver pin mapping, gate pulldowns and absence of bus shorts. Check heatsink-to-tab insulation wherever different drain nodes could otherwise become joined.
2. Use a **current-limited bench supply**, never an initial connection directly to the pack. Set SD low before applying power. Verify the 3.3 V rail, protected gate supply, shutdown behavior and zero-current ISNS first.
3. Follow the brief's load/voltage ladder: **12 V into a power resistor → 12 V into the coil → 60 V into a resistor → 60 V into the coil**. Start the specified current bring-up at 10 A only after the lower-power checks succeed. Choose a resistor/load and current limit appropriate to each test; the brief does not specify their ratings.
4. At every rung, verify both gate-source voltages, deadtime, switch-node overshoot, supply rails, current sign and temperatures before proceeding. Use measurement equipment appropriate to floating high-side gates and the bus voltage.
5. **Do not do the 60 V power-up alone.** J2 has no reverse-polarity protection and no keying: verify + and − before every connection.
6. **Do not hot-plug the pack.** The brief identifies cable-inductance/inrush ringing as a risk to the 100 V devices. Resolve pack connection and regeneration behavior before pack operation.
7. After disconnection, measure the bus before handling it. The nominal 22 kΩ / 1410 µF bleed reaches about 1 V in 127 s from 60 V; elapsed time is not proof of discharge.

This board has no overcurrent controller, fault latch or second channel. The external controller and bench setup must provide the intended test control. No test in this document has been claimed as completed.
