"""Reuse existing PCB heat-spreading solver on Rev F1, with explicit budgets.

Applied losses and convection coefficients are sensitivity assumptions, not
validated switching losses or a measured fan-to-board heat-transfer coefficient.
The model cannot establish continuous 20 A qualification.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'MV_Board_RevF1'
sys.path.insert(0,str(ROOT/'Verification_Independent'))
import native as n
p=OUT/'KiCad/MV24_RevF1.kicad_pcb'
b=n.sx.loads(p.read_text());n.read_board=lambda:b
import thermal as th
# The existing solver's 1.065mm central dielectric is thicker than F1's .9392mm;
# retained conservative vertical-path approximation, explicitly recorded below.
powers={'Q1':5.,'Q2':3.5,'U1':1.2,'R7':1.5,'L1':3.2}
powers.update({f'C{i}':.15 for i in range(1,9)});powers.update({f'C{i}':.2 for i in range(13,16)})
rows=[]
for h,mesh in [(8,1.),(30,1.),(50,1.),(50,.5)]:
    r,t=th.solve(powers,h=h,step=mesh,ambient=30)
    r.update(board_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
             assumptions='Loss budgets are unvalidated assumptions. Convection h does not prove a particular fan delivers cooling. Original solver retains thicker 1.065mm central dielectric (candidate .9392mm).')
    rows.append(r)
    print(h,mesh,{k:round(v,1) for k,v in r['component_board_C'].items() if k in ['Q1','Q2','U1','R7','L1']},flush=True)
    if mesh==.5:
        th.np.save(OUT/'Verification/thermal-screen.npy',t)
        fig,ax=th.plt.subplots(figsize=(10,7));im=ax.imshow(t[0],extent=[20,170,130,20],cmap='inferno')
        fig.colorbar(im,label='Predicted PCB surface temperature (C)')
        ax.set_title('Rev F1: assumed losses, 30 C ambient, h=50 W/m2K per face\nSensitivity only; not a measured cooling or 20 A rating')
        for ref in ['Q1','Q2','U1','L1']:
            f=n.footprint_map(b)[ref];x,y=n.child(f,'at')[1:3];ax.text(x,y,ref,color='cyan',fontsize=9)
        fig.savefig(OUT/'Verification/review/thermal-screen.png',dpi=150);th.plt.close(fig)
(OUT/'Verification/thermal-screen.json').write_text(json.dumps(dict(scope=__doc__,rows=rows),indent=2)+'\n')
