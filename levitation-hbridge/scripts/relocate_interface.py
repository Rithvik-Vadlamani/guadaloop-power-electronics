"""Move only the user-approved control interface; reroute/refill in the following build steps."""
from design import *
import pcbnew as p,wx
app=wx.App(False);assert not list(ROOT.glob('*.lck')),'Close project editors before file edits'
b=p.LoadBoard(str(ROOT/'poc_lev.kicad_pcb'));MM=p.FromMM;V=lambda x,y:p.VECTOR2I(MM(x),MM(y))
POS={'J3':(107,110,90),'U4':(115,101,0),'C23':(118.7,101,90),'C22':(110,102.5,90),'R24':(114.62,106,90),'R25':(117.16,106,90),'R19':(119.7,106,90),'D2':(127.8,100.5,180),'C24':(134.5,103,0),'TP4':(129,105.7,0),'TP5':(130,110,0)}
for f in b.GetFootprints():
 ref=f.GetReference()
 if ref in POS:
  x,y,a=POS[ref];f.SetPosition(V(x,y));f.SetOrientationDegrees(a)
  f.Reference().SetPosition(V(x,y-3));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
for t in b.GetDrawings():
 if isinstance(t,p.PCB_TEXT):
  if t.GetText().startswith('POC LEV'):t.SetPosition(V(65,104))
  if t.GetText().startswith('60 V  |'):t.SetPosition(V(65,107))
  if t.GetText().startswith('BENCH SUPPLY'):t.SetPosition(V(65,110))
  if t.GetText()=='SD: LOW = OFF':t.SetPosition(V(137,111));t.SetTextSize(V(.8,.8));t.SetTextThickness(MM(.12))
# Remove prior edge pin legends when rerunning this migration.
for t in list(b.GetDrawings()):
 if isinstance(t,p.PCB_TEXT) and abs(p.ToMM(t.GetPosition().y)-112.6)<.001:b.RemoveNative(t)
labels=['12V','3V3','G','A','B','SD','IS','G']
for i,label in enumerate(labels):
 t=p.PCB_TEXT(b);t.SetText(label);t.SetPosition(V(107+i*2.54,112.6));t.SetTextSize(V(.8,.8));t.SetTextThickness(MM(.1));t.SetLayer(p.F_SilkS);b.Add(t)
p.SaveBoard(str(ROOT/'poc_lev.kicad_pcb'),b)
placement=json.loads((ROOT/'placement.json').read_text());placement.update(POS);(ROOT/'placement.json').write_text(json.dumps(placement,indent=2)+'\n')
(ROOT/'reports/interface_placement.json').write_text(json.dumps({'change':'User-approved edge control interface','positions_mm_degrees':POS,'J3_pad_row_to_bottom_edge_mm':4,'mating_envelope_status':'Actual plug/harness dimensions not supplied; mechanical mating fit not qualified'},indent=2)+'\n')
print('Moved',len(POS),'interface footprints')
