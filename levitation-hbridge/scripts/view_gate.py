from sexpr import *
from pathlib import Path
import math
root=Path(__file__).resolve().parent.parent
b=parse((root/'poc_lev.kicad_pcb').read_text());out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 20 40 22" width="1600" height="880"><rect x="30" y="20" width="40" height="22" fill="#111"/>']
colors={'/GND':'#888','/+12V':'#b38eff','/SW_A':'#55ff90','/HO_A':'#ff6454','/LO_A':'#ffd35c','/G_Q1':'#ff8cce','/G_Q2':'#00caff','/OFF_Q1':'#ff9e60','/OFF_Q2':'#4f7dff','/VB_A':'#fff'}
for t in children(b,'segment'):
 n=one(t,'net')[1];l=one(t,'layer')[1]
 if n not in colors or l!='F.Cu':continue
 a=one(t,'start')[1:];c=one(t,'end')[1:]
 out.append(f'<path d="M{a[0]},{a[1]} L{c[0]},{c[1]}" stroke="{colors[n]}" stroke-width="{one(t,"width")[1]}"/>')
for f in children(b,'footprint'):
 ref=next(a[2] for a in children(f,'property') if a[1]=='Reference');at=one(f,'at');x,y=map(float,at[1:3]);deg=float(at[3]) if len(at)>3 else 0;r=math.radians(deg)
 if not 30<x<70 or not 20<y<42:continue
 for pd in children(f,'pad'):
  px,py=map(float,one(pd,'at')[1:3]);cx=x+px*math.cos(r)+py*math.sin(r);cy=y-px*math.sin(r)+py*math.cos(r);w,h=map(float,one(pd,'size')[1:]);n=one(pd,'net');col=colors.get(n[1] if n else '', '#668066')
  out.append(f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" transform="rotate({-deg} {cx} {cy})" fill="{col}" stroke="#fff" stroke-width=".04"/><text x="{cx}" y="{cy+.16}" font-size=".5" text-anchor="middle" fill="#000">{pd[1]}</text>')
 out.append(f'<text x="{x}" y="{y}" font-size=".65" text-anchor="middle" fill="#fff">{ref}</text>')
out.append('</svg>');(root/'reports/gate-detail.svg').write_text(''.join(out))
