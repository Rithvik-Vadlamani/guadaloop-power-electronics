"""Read native KiCad geometry for independent export reconciliation; no PCB edits."""
from pathlib import Path
import pcbnew, json, math, hashlib, csv
OUT=Path(__file__).resolve().parents[1]
p=OUT/'KiCad/MV24_RevF1.kicad_pcb';b=pcbnew.LoadBoard(str(p))
def mm(v):return round(pcbnew.ToMM(v),6)
def point(v):return (mm(v.x),-mm(v.y)) # KiCad global export coordinates, Y up
holes=[];parts=[];fill=[]
pads=[(f.GetReference(),pad) for f in b.GetFootprints() for pad in f.Pads() if pad.GetNumber() and pad.GetAttribute()==pcbnew.PAD_ATTRIB_SMD and (pad.IsOnLayer(pcbnew.F_Cu) or pad.IsOnLayer(pcbnew.B_Cu))]
for f in b.GetFootprints():
    parts.append(dict(ref=f.GetReference(),value=f.GetValue(),xy=point(f.GetPosition()),rotation=f.GetOrientationDegrees(),side='top' if f.GetLayer()==pcbnew.F_Cu else 'bottom'))
    for pad in f.Pads():
        sx,sy=pcbnew.ToMM(pad.GetDrillSize())
        if not sx or not sy:continue
        x,y=point(pad.GetPosition());d=min(sx,sy);half=abs(sx-sy)/2
        a=math.radians(pad.GetOrientationDegrees());dx,dy=(half,0) if sx>sy else (0,half)
        vx,vy=dx*math.cos(a)+dy*math.sin(a),-dx*math.sin(a)+dy*math.cos(a)
        pts=sorted([(round(x-vx,6),round(y+vy,6)),(round(x+vx,6),round(y-vy,6))])
        holes.append(dict(plated=pad.GetAttribute()!=pcbnew.PAD_ATTRIB_NPTH,diameter=round(d,6),points=pts,source=f.GetReference()+'.'+pad.GetNumber()))
for v in b.GetTracks():
    if not isinstance(v,pcbnew.PCB_VIA):continue
    xy=point(v.GetPosition());holes.append(dict(plated=True,diameter=mm(v.GetDrillValue()),points=[xy,xy],source='via'))
    # Conservative fabrication selection: any copper via annulus bounding box
    # intersecting a numbered SMD copper pad bounding box. May include adjacent
    # vias; deliberately never relies solely on the hole center being in pad.
    hits=sorted({r+'.'+pad.GetNumber() for r,pad in pads if pad.GetBoundingBox().Intersects(v.GetBoundingBox())})
    if hits:fill.append(dict(x_mm=xy[0],y_mm=xy[1],hole_mm=mm(v.GetDrillValue()),net=v.GetNetname(),near_pad=';'.join(hits)))
fill.sort(key=lambda a:(a['hole_mm'],a['x_mm'],a['y_mm']))
(OUT/'Verification/handoff-native-inventory.json').write_text(json.dumps(dict(board_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),holes=holes,parts=parts,fill_vias=fill),indent=2)+'\n')
with (OUT/'Manufacturing/filled-vias.csv').open('w',newline='') as s:
    w=csv.DictWriter(s,fieldnames=['x_mm','y_mm','hole_mm','net','near_pad']);w.writeheader();w.writerows(fill)
print('Native holes:',len(holes),'Selected fill/cap vias:',len(fill))
