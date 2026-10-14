"""Use KiCad's API to preserve intentional thermal-via net assignments."""
from pathlib import Path
import json, pcbnew
BASE=Path(__file__).resolve().parents[1]
p=BASE/'KiCad/MV24_RevF1.kicad_pcb';b=pcbnew.LoadBoard(str(p))
edits=json.loads((BASE/'Verification/revision-edits.json').read_text())
target={(round(a['x_mm'],4),round(a['y_mm'],4)):a['net'] for a in edits['added_thermal_vias']}
for t in b.GetTracks():
    if isinstance(t,pcbnew.PCB_VIA):
        xy=tuple(round(x,4) for x in pcbnew.ToMM(t.GetPosition()))
        if xy in target:
            t.SetNet(b.FindNet(target[xy]));t.SetIsFree(True)
pcbnew.SaveBoard(str(p),b)
print('Native assigned thermal vias:',len(target))
