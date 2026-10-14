"""Build a native single-sheet KiCad schematic using installed library symbols."""
from sexpr import *
from design import *
import uuid,copy,math,csv
BASE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'poc-lev/'+s))
LIB={}
def load(lib):
    if lib in LIB:return copy.deepcopy(LIB[lib])
    if lib=='poc_lev:INA240A2D':
        s=load('Amplifier_Current:INA240A2D');s[1]=lib
    elif lib=='poc_lev:C_Polarized_Positive2':
        s=load('Device:C_Polarized');s[1]=lib
        for p in walk(s,'pin'):
            n=one(p,'number');n[1]='2' if n[1]=='1' else '1'
        for x in children(s,'symbol'):x[1]=x[1].replace('C_Polarized','C_Polarized_Positive2')
    else:
        ln,n=lib.split(':');root=parse((BASE/(ln+'.kicad_sym')).read_text())
        s=copy.deepcopy(next(x for x in children(root,'symbol') if x[1]==n))
        e=one(s,'extends')
        if e:
            parent=load(ln+':'+e[1]);s.remove(e)
            for x in children(parent,'symbol'):
                x[1]=x[1].replace(e[1],n);s.append(x)
        s[1]=lib
    LIB[lib]=copy.deepcopy(s);return s
# A2 flat sheet. Main power blocks above, gate drives in middle, control below.
pos={
'Q1':(210,50),'Q2':(210,90),'Q3':(290,50),'Q4':(290,90),'R1':(245,65),'J1':(270,72),'J2':(40,50),
'U1':(90,175),'U2':(290,175),'U3':(450,180),'J3':(55,320),
'U4':(190,300),'D2':(95,300),'C24':(125,300),'C22':(155,345),'C23':(230,350),
'R19':(325,340),'R24':(130,340),'R25':(130,365),'C21':(495,215),'C20':(425,200),'R12':(410,162),'R13':(410,185),
'R14':(70,82),'D8':(35,82)}
for i in range(1,6):pos['C'+str(i)]=(35+(i-1)*30,120)
for i in range(6,11):pos['C'+str(i)]=(350+(i-6)*30,120)
for i in range(11,14):pos['C'+str(i)]=(380+(i-11)*40,55)
for offset,items in [(0,['R2','D5','R20','R3','R4','D4','R21','R6']),(200,['R9','D7','R22','R7','R11','D6','R23','R10'])]:
    for j,r in enumerate(items):pos[r]=(135+offset+(j%4)*30,155+(j//4)*65)
for off,refs in [(0,['C16','D1','R5','C14','C15']),(200,['C17','D3','R8','C19','C18'])]:
    for j,r in enumerate(refs):pos[r]=(35+off+j*32,255)
for i in range(1,5):pos['H'+str(i)]=(400+i*28,340)
for i in range(1,7):pos['TP'+str(i)]=(360+i*28,290)
S=[]
def add(s):S.append(s)
def text(t,x,y,size=1.7):add(f'(text {json.dumps(t)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left bottom)) (uuid {uid("text"+t)}))')
text('POC LEV | 60 V bidirectional coil driver',20,20,3)
text('DESIGN REVIEW | 16 kHz nominal / 32 kHz ceiling | 10 A first bring-up | 30 A requires thermal/transient qualification',20,27,1.6)
for t,x,y in [('BUS ENTRY / BLEED',20,35),('H-BRIDGE / KELVIN SHUNT',190,35),('BULK: 1410 uF, 100 V',370,35),('LEG A: LOCAL BRIDGE CERAMICS',20,102),('LEG B: LOCAL BRIDGE CERAMICS',345,102),('LEG A GATE DRIVE',20,140),('LEG B GATE DRIVE',240,140),('BIDIRECTIONAL SENSE',400,140),('CONTROL / RAIL ENTRY',20,280),('TEST ACCESS',365,276),('M3 MOUNTING',410,323)]:text(t,x,y)
text('Positive current: SW_A -> R1 -> COIL_A. ISNS = 1.65 V + 0.025 V/A x I.',410,230,1.25)
text('R1: two-terminal Bourns part with Kelvin PCB pickup (approved).',410,237,1.15)
text('NO FAB / POWER-UP RELEASE: see README and verification report. R19 fit only after human SD review.',20,390,1.6)
text('J3: 1=12V_IN  2=3V3  3=GND  4=PWM_A  5=PWM_B  6=SD  7=ISNS  8=GND',20,380,1.5)
instances={}
PINXY={}
for ref,p in PARTS.items():
    s=load(p['lib']);units=sorted(set(int(x[1].rsplit('_',2)[-2]) for x in children(s,'symbol') if int(x[1].rsplit('_',2)[-2])>0)) or [1]
    for u in units:
        x,y=pos[ref]
        if ref=='U4':x,y={1:(195,300),2:(195,325),3:(270,330)}[u]
        x,y=round(x/1.27)*1.27,round(y/1.27)*1.27
        su=uid(ref+'/'+str(u));instances[ref]=uid(ref+'/1')
        # Mirror bridge B drawing to put gates outward while preserving pin identity.
        mirrored=ref in ['Q3','Q4'];mirror='(mirror y)' if mirrored else ''
        props=[]
        for key,val,dy,hidden in [('Reference',ref,-8,False),('Value',p['value'],9,False),('Footprint',p['footprint'],0,True),('Datasheet',next((a[2] for a in children(s,'property') if a[1]=='Datasheet'),''),0,True),('MPN',p['mpn'],0,True),('Rating',p['rating'].split(';')[0],12,False),('Design note',p['note'],0,True)]:
            props.append(f'(property {json.dumps(key)} {json.dumps(val)} (at {x+5} {y+dy} 0) (effects (font (size 1.15 1.15)) (justify left)'+(' (hide yes)' if hidden else '')+'))')
        pins=[]
        for body in children(s,'symbol'):
            un=int(body[1].rsplit('_',2)[-2])
            if un not in [0,u]:continue
            for pin in children(body,'pin'):
                pn=one(pin,'number')[1];a=one(pin,'at');px,py,ang=map(float,a[1:]);
                if mirrored:px=-px;ang=180-ang # KiCad mirror x reflects y
                xx,yy=x+px,y-py
                PINXY[ref+'.'+pn]=(xx,yy)
                n=PINS.get(ref+'.'+pn)
                if not n: continue
                length=3.81
                # Pin direction points toward symbol. Wire extends opposite it.
                ex=round(xx-length*math.cos(math.radians(ang)),4);ey=round(yy+length*math.sin(math.radians(ang)),4)
                add(f'(wire (pts (xy {xx} {yy}) (xy {ex} {ey})) (stroke (width 0.254) (type default)) (uuid {uid(ref+str(u)+pn+"wire")}))')
                la=0 if abs(ex-xx)>0.01 else 90
                # label left/right alignment chosen to extend away from component
                just='right' if ex<xx else 'left'
                add(f'(label {json.dumps(n)} (at {ex} {ey} {la}) (effects (font (size 1.05 1.05)) (justify {just} bottom)) (uuid {uid(ref+str(u)+pn+"label")}))')
                pins.append(f'(pin {json.dumps(pn)} (uuid {uid(ref+str(u)+pn+"pin")}))')
        add(f'(symbol (lib_id {json.dumps(p["lib"])}) (at {x} {y} 0) (unit {u}) {mirror} (in_bom yes) (on_board yes) (dnp no) (uuid {su}) '+''.join(props+pins)+f'(instances (project "poc_lev" (path "/{uid("root")}" (reference "{ref}") (unit {u})))))')
# Explicit bridge topology, joining actual pin endpoints. Local labels remain as cross-references.
def wpath(name,points):
    for j,(a,c) in enumerate(zip(points,points[1:])):
        add(f'(wire (pts (xy {a[0]} {a[1]}) (xy {c[0]} {c[1]})) (stroke (width 0.254) (type default)) (uuid {uid(name+str(j))}))')
qa,qb=PINXY['Q1.2'],PINXY['Q3.2']
wpath('bus_bridge',[qa,(qa[0],40.64),(qb[0],40.64),qb])
wpath('midpoint_A',[PINXY['Q1.3'],PINXY['Q2.2']])
wpath('midpoint_B',[PINXY['Q3.3'],PINXY['Q4.2']])
qa,qb=PINXY['Q2.3'],PINXY['Q4.3']
wpath('ground_bridge',[qa,(qa[0],102.87),(qb[0],102.87),qb])
a=PINXY['Q1.3'];z=PINXY['R1.1'];tap=(a[0],60.96)
wpath('shunt_from_A',[tap,(234.95,tap[1]),(234.95,z[1]),z])
q=PINXY['Q3.3'];j=PINXY['J1.1'];wpath('coil_B',[(q[0],j[1]),j])
a=PINXY['R1.4'];j=PINXY['J1.2'];wpath('coil_A',[a,(a[0],j[1]),j])
for k,pt in enumerate([tap,(q[0],PINXY['J1.1'][1])]):
    add(f'(junction (at {pt[0]} {pt[1]}) (diameter 0) (color 0 0 0 0) (uuid {uid("bridge-junction"+str(k))}))')

# Flags use ordinary wires and labels, parsed by KiCad's connectivity engine.
flaglib=load('power:PWR_FLAG')
for i,n in enumerate(['+60V','GND','+12V','+3.3V']):
    x,y=round((35+i*27)/1.27)*1.27,round(365/1.27)*1.27
    add(f'(symbol (lib_id "power:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board yes) (dnp no) (uuid {uid(n+"flag")}) (property "Reference" "#FLG0{i+1}" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "PWR_FLAG" (at {x} {y-5} 0) (effects (font (size 1 1)))) (instances (project "poc_lev" (path "/{uid("root")}" (reference "#FLG0{i+1}") (unit 1)))))')
    add(f'(label "{n}" (at {x} {y} 0) (effects (font (size 1.1 1.1)) (justify left bottom)) (uuid {uid(n+"flabel")}))')
libblock='(lib_symbols '+'\n'.join(dump(s) for s in LIB.values())+')'
header=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid("root")}) (paper "A2") (title_block (title "poc_lev - coil driver") (date "2026-09-06") (rev "A REVIEW") (company "Guadaloop / UT Austin"))'
(ROOT/'poc_lev.kicad_sch').write_text(header+'\n'+libblock+'\n'+'\n'.join(S)+'\n)')
(ROOT/'symbol_uuids.json').write_text(json.dumps(instances))
# Local symbol only; standard symbols remain referenced to installed libraries.
local=[s for k,s in LIB.items() if k.startswith('poc_lev:')]
for s in local:s[1]=s[1].split(':')[1]
(ROOT/'poc_lev.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+''.join(map(dump,local))+')')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "poc_lev") (type "KiCad") (uri "${KIPRJMOD}/poc_lev.kicad_sym") (options "") (descr "Project-local verified mappings")))\n')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "poc_lev") (type "KiCad") (uri "${KIPRJMOD}/lib.pretty") (options "") (descr "Project local footprints")))\n')
with (ROOT/'BOM.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=['ref','value','mpn','rating','footprint','note'],extrasaction='ignore');w.writeheader();w.writerows(PARTS.values())
print('Schematic:',len(PARTS),'physical items,',len(NETS),'nets')
