# Guadaloop power electronics

Selected power electronics designs from my work on Guadaloop. This repository collects editable schematics and PCB layouts so the designs can be reviewed without digging through unrelated project files.

| Design | What it covers | Files |
| --- | --- | --- |
| Levitation H-bridge | A nominal 60 V bidirectional coil-driver channel, including gate driving and current sensing. | [Design and review notes](levitation-hbridge/README.md) |
| 60 V to 24 V buck converter | A buck-converter design with a 10 A output target. | [Editable design](buck-60v-24v/) |
| Medium-voltage board, Rev F1 | A compact prototype power-board revision with revised inductance, compensation, and thermal copper. | [Design notes](medium-voltage-revf1/README.md) |

These are engineering designs and review packages. Their voltage/current targets are design requirements; the included files do not establish measured hardware performance.

My broader team work includes power distribution, PCB assembly, and enclosure work. This repository contains the design files located for this publication. It does not include every team design or claim sole authorship of collaborative work.

For my wireless power transfer models and results, see [the separate wireless power repository](https://github.com/Rithvik-Vadlamani/guadaloop-wireless-power-transfer).

## Open the designs

Use KiCad with the standard symbol and footprint libraries installed. Each folder contains its own project and local library tables. Start with the `.kicad_pro` file. Some projects were saved with KiCad 10; the levitation design requires KiCad 10.0.3 or later.

Saved review results describe the revision and assumptions recorded in each package. Native design files are the source of truth. No fabrication or hardware testing was performed as part of publishing this repository.
