"""Add assembly-only labels and a fabrication via map without altering PCB artwork."""
from pathlib import Path
import json,csv,xml.etree.ElementTree as E
import pymupdf as fitz, gerbonara
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
OUT=Path(__file__).resolve().parents[1];A=OUT/'Assembly';M=OUT/'Manufacturing'
d=json.loads((OUT/'Verification/handoff-native-inventory.json').read_text())
refs={r['Reference'] for r in csv.DictReader((A/'bom.csv').open())}
src=A/'assembly-drawing.svg';root=E.parse(src).getroot();ns='{http://www.w3.org/2000/svg}'
present={t.text for t in root.iter(ns+'text')}
added=[]
for p in d['parts']:
    if p['ref'] not in refs or p['ref'] in present:continue
    x,y=p['xy'];t=E.SubElement(root,ns+'text',{'x':str(x-20),'y':str(-y-20+.35),'font-size':'1.4','text-anchor':'middle','fill':'#004488','font-family':'sans-serif'})
    t.text=p['ref'];added.append(p['ref'])
dst=A/'assembly-reference-map.svg';E.ElementTree(root).write(dst,encoding='unicode')
doc=fitz.open(dst);page=doc[0];s=2400/page.rect.width;page.get_pixmap(matrix=fitz.Matrix(s,s),alpha=False).save(dst.with_suffix('.png'))
fig,axes=plt.subplots(1,2,figsize=(15,7),gridspec_kw={'width_ratios':[1.5,1]})
for ax in axes:
    ax.add_patch(Rectangle((20,-130),150,110,fill=False,color='black',lw=.8))
    for h in d['holes']:
        x=sum(p[0] for p in h['points'])/2;y=sum(p[1] for p in h['points'])/2
        ax.add_patch(Circle((x,y),h['diameter']/2,fill=False,color='#aaaaaa',lw=.5))
    for v in d['fill_vias']:
        ax.add_patch(Circle((v['x_mm'],v['y_mm']),.75,fill=False,color='#c0392b',lw=1.))
    ax.set_aspect('equal');ax.set_xlabel('Gerber / drill X (mm)');ax.set_ylabel('Gerber / drill Y (mm)');ax.grid(alpha=.15)
axes[0].set(xlim=(16,174),ylim=(-134,-16),title='38 selected fill-and-cap vias (red circles)')
axes[1].set(xlim=(72,106),ylim=(-90,-57),title='Power-stage detail — use CSV for exact centers')
for r,offset in [('Q1',(4,1)),('Q2',(4,-1)),('U1',(-5,0)),('R7',(4,-1))]:
    p=next(p for p in d['parts'] if p['ref']==r);x,y=p['xy'];axes[1].annotate(r,xy=(x,y),xytext=(x+offset[0],y+offset[1]),color='#004488')
fig.suptitle('Rev F1 fabrication selection — resin fill, planarize, copper cap\n38 includes inherited and adjacent vias; not 38 newly added vias',fontsize=11)
fig.tight_layout();fig.savefig(M/'filled-vias-map.png',dpi=160,bbox_inches='tight');plt.close(fig)
for side in ['F','B']:
    p=A/f'stencil/MV24_RevF1-{side}_Paste.gbr';g=gerbonara.GerberFile.open(p)
    q=OUT/f'Verification/manufacturing-review/{side}-paste.svg';q.write_text(str(g.to_svg(force_bounds=((72,-89),(106,-57)))))
    doc=fitz.open(q);s=1400/doc[0].rect.width;doc[0].get_pixmap(matrix=fitz.Matrix(s,s),alpha=False).save(q.with_suffix('.png'))
print('Added assembly-only labels:',sorted(added))
