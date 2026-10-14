"""Scoped native Rev F1 edits, regenerated from the preserved Rev F baseline.

No new circuit nets, precharge, MOSFET substitutions, or component moves.
KiCad performs final fill/export/DRC; geometry below only selects candidate vias.
"""
from pathlib import Path
import sys, copy, csv, json, uuid, shutil
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'MV_Board_RevF'; OUT=ROOT/'MV_Board_RevF1'; K=OUT/'KiCad'
sys.path.insert(0,str(ROOT/'Verification_Independent'))
import native as n
S=n.sx.Symbol
b=n.sx.loads((BASE/'KiCad/MV24_RevF.kicad_pcb').read_text())
s=n.sx.loads((BASE/'KiCad/MV24_RevF.kicad_sch').read_text())
changes={
 'L1':dict(value='15u / CPRX3231L',mpn='CPRX3231L-150MC',footprint='MV:CODACA_CPRX3231L_150MC',url='https://www.codaca.com/Productsctr_CPRX3231L.html',reason='Coordinate 15uH with 100kHz to reduce gate-drive demand without increasing nominal ripple'),
 'R6':dict(value='100k',mpn='RT0805BRD07100KL',url='https://www.yageogroup.com/component-documentation/download/specsheet/RT0805BRD07100KL',reason='100kHz nominal; reduced gate-supply and switching demand'),
 'R10':dict(value='8.2k',mpn='RC0805FR-078K2L',url='https://www.yageogroup.com/component-documentation/download/specsheet/RC0805FR-078K2L',reason='Compensation selected with 15uH/100kHz; 46.94deg minimum in declared averaged-model scenarios')}
def property_set(obj,key,value):
    p=next((p for p in n.children(obj,'property') if p[1]==key),None)
    if p is not None:p[2]=value
    elif key=='Datasheet':
        p=copy.deepcopy(next(p for p in n.children(obj,'property') if p[1]=='Value'))
        p[1:3]=[key,value]
        effects=n.child(p,'effects')
        if effects and not n.child(effects,'hide'):effects.append([S('hide'),S('yes')])
        obj.append(p)
def update(obj,c):
    for field,value in [('Value',c['value']),('MPN',c['mpn']),('Datasheet',c['url'])]:property_set(obj,field,value)
    if 'footprint' in c:property_set(obj,'Footprint',c['footprint'])
fm=n.footprint_map(b)
for sym in n.children(s,'symbol'):
    ref=n.props(sym).get('Reference')
    if ref in changes:update(sym,changes[ref])
def project_names(obj):
    if isinstance(obj,list):
        if n.tag(obj)=='project' and len(obj)>1 and obj[1]=='MV24_RevF':obj[1]='MV24_RevF1'
        for a in obj:project_names(a)
project_names(s)
# Replace three inherited four-way junctions by separated T connections.
for sym in n.children(s,'symbol'):
    if n.props(sym).get('Reference')=='#FLG04':
        n.child(sym,'at')[1]-=2.54
        for p in n.children(sym,'property'):
            if n.child(p,'at'):n.child(p,'at')[1]-=2.54
def wire(a,z):
    s.append([S('wire'),[S('pts'),[S('xy'),*a],[S('xy'),*z]],[S('stroke'),[S('width'),0],[S('type'),S('default')]],[S('uuid'),str(uuid.uuid4())]])
def junction(x,y):
    s.append([S('junction'),[S('at'),x,y],[S('diameter'),0],[S('color'),0,0,0,0],[S('uuid'),str(uuid.uuid4())]])
junction(88.9,152.4)
for x,end_y in [(254.,264.16),(264.16,242.57)]:
    for w in n.children(s,'wire'):
        pts=n.children(n.child(w,'pts'),'xy')
        if [a[1:3] for a in pts]==[[x,233.68],[x,end_y]]:
            pts[0][2]=236.22
            wire([x+2.54,233.68],[x+2.54,236.22]);wire([x+2.54,236.22],[x,236.22])
            junction(x+2.54,233.68)
for sym in n.children(n.child(s,'lib_symbols'),'symbol'):
    if sym[1]=='Device:L':
        fp=n.child(sym,'property')
        for p in n.children(sym,'property'):
            if p[1]=='ki_fp_filters':p[2]+=' CODACA_CPRX3231L_150MC'
device=n.sx.loads((BASE/'KiCad/Device.kicad_sym').read_text())
for sym in n.children(device,'symbol'):
    if sym[1]=='L':
        for p in n.children(sym,'property'):
            if p[1]=='ki_fp_filters':p[2]+=' CODACA_CPRX3231L_150MC'
(K/'Device.kicad_sym').write_text(n.sx.dumps(device)+'\n')
title=n.child(s,'title_block')
if title:
    n.child(title,'title')[1]='MV / fluids supply - Rev F1 compact prototype'
    title.append([S('rev'),'F1'])
for ref,c in changes.items():
    update(fm[ref],c)
    if 'footprint' in c:fm[ref][1]=c['footprint']
# Preserve terminal centers and copper lands. Larger plated slots accommodate
# the 15uH part's A=20.2+/-0.8, B=1.6+/-0.3 and 6.0+/-0.3 mm terminals.
lib=n.sx.loads((BASE/'KiCad/footprints/MV.pretty/CODACA_CPRX3231L_100MC.kicad_mod').read_text())
lib[1]='CODACA_CPRX3231L_150MC'
for obj in [lib,fm['L1']]:
    property_set(obj,'Value','15u / CPRX3231L')
    for p in n.children(obj,'pad'):
        if p[1] in ['1','2']:n.child(p,'drill')[1:]=[S('oval'),4.0,8.8]
    if n.child(obj,'descr'):n.child(obj,'descr')[1]='CODACA CPRX3231L-150MC; 4.0x8.8mm plated tolerance slots; original terminal centers retained'
    for model in n.children(obj,'model'):model[1]=str(model[1]).replace('CPRX3231L_100MC','CPRX3231L_150MC')
(K/'footprints/MV.pretty/CODACA_CPRX3231L_150MC.kicad_mod').write_text(n.sx.dumps(lib)+'\n')
shutil.copy2(BASE/'KiCad/3dmodels/CODACA_CPRX3231L_100MC.wrl',K/'3dmodels/CODACA_CPRX3231L_150MC.wrl')
for text in n.children(b,'gr_text'):
    text[1]=text[1].replace('Rev F','Rev F1')
stack=n.child(n.child(b,'setup'),'stackup')
for layer in n.children(stack,'layer'):
    if layer[1] in ['F.Cu','B.Cu']:n.child(layer,'thickness')[1]=.070
    elif layer[1] in ['In1.Cu','In2.Cu']:n.child(layer,'thickness')[1]=.035
    elif layer[1]=='dielectric 2':n.child(layer,'thickness')[1]=.9392
n.child(n.child(b,'general'),'thickness')[1]=1.6
# ENIG keeps the fine-pitch controller/power-device lands flat for assembly.
n.child(stack,'copper_finish')[1]='ENIG'
# Complete Q1's heat path: Rev F's bottom VIN plane stopped above the MOSFET.
# Broaden its top copper locally and extend the bottom VIN plane to the same
# outline, so the existing drain vias reach a real bottom heat spreader.
vin_top=next(z for z in n.children(b,'zone') if n.child(z,'net') and n.child(z,'net')[1]=='/VIN' and n.child(z,'layer')[1]=='F.Cu')
for pt in n.children(n.child(n.child(vin_top,'polygon'),'pts'),'xy'):
    if pt[1:3] in [[89,67.5],[89,62]]:pt[1]=85
vin_bottom=next(z for z in n.children(b,'zone') if n.child(z,'net') and n.child(z,'net')[1]=='/VIN' and n.child(z,'layer')[1]=='B.Cu')
n.child(vin_bottom,'polygon')[1:]=copy.deepcopy(n.child(vin_top,'polygon')[1:])
# Compact backside SW island immediately below Q2. It is electrically live;
# no direct metal heatsink contact is permitted. No enlargement of top SW loop.
z=copy.deepcopy(next(z for z in n.children(b,'zone') if n.child(z,'net') and n.child(z,'net')[1]=='/SW'))
z[:]=[x for x in z if n.tag(x) not in ['filled_polygon','fill_segments']]
n.child(z,'uuid')[1]=str(uuid.uuid4()); n.child(z,'layer')[1]='B.Cu'
n.child(z,'polygon')[1]=[S('pts')]+[[S('xy'),x,y] for x,y in [(92.5,68.5),(106.5,68.5),(106.5,79.5),(92.5,79.5)]]
if n.child(z,'priority'):n.child(z,'priority')[1]=10
else:z.append([S('priority'),10])
conn=n.child(z,'connect_pads')
if conn and n.child(conn,'clearance'):n.child(conn,'clearance')[1]=.35
b.append(z)
# Read-only shared copper extractor; point at this in-memory candidate.
n.read_board=lambda:b
import copper as c
cu,pads,vertical,holes=c.geometry(b)
from shapely.geometry import Point,LineString,box,Polygon
from shapely.ops import unary_union
allpads=unary_union([p[2] for ps in pads.values() for p in ps])
added=[]
vin_outline=Polygon([p[1:3] for p in n.children(n.child(n.child(vin_top,'polygon'),'pts'),'xy')])
for net,region,back in [('/SW',(93,106,69,79),box(92.5,68.5,106.5,79.5)),('/VIN',(85,96,62,68),vin_outline)]:
    front=vin_outline if net=='/VIN' else cu[(net,'F.Cu')]
    safe=front.intersection(back).buffer(-.45).difference(allpads.buffer(.42)).difference(holes.buffer(.45))
    tracks=[LineString([n.child(t,'start')[1:3],n.child(t,'end')[1:3]]).buffer(n.child(t,'width')[1]/2+.6) for t in n.children(b,'segment') if n.child(t,'net')[1]!=net]
    if tracks:safe=safe.difference(unary_union(tracks))
    x0,x1,y0,y1=region
    for x in c.np.arange(x0,x1,1.25):
        for y in c.np.arange(y0,y1,1.25):
            # Restrict to the close-to-Q2 positions confirmed by native refill.
            if net=='/SW' and (float(x),float(y)) not in [(96.75,69.),(96.75,70.25),(98.,69.),(98.,70.25),(98.,72.75),(98.,74.),(98.,75.25),(99.25,74.)]:continue
            if not safe.contains(Point(x,y)):continue
            if any((v['x']-x)**2+(v['y']-y)**2<1.1**2 for v in vertical):continue
            b.append([S('via'),[S('at'),float(x),float(y)],[S('size'),.7],[S('drill'),.3],[S('layers'),'F.Cu','B.Cu'],[S('net'),net],[S('uuid'),str(uuid.uuid4())]])
            vertical.append(dict(x=x,y=y));added.append(dict(net=net,x_mm=float(x),y_mm=float(y)))
# Direct drain-pad heat paths. These must be resin-filled, planarized and
# copper-capped for solderability; ordinary open via-in-pad is not specified.
for net,xs,ys in [('/VIN',[92.3,94.2],[63.2,65.,65.8]),('/SW',[94.1,95.4],[71.6,73.,74.4])]:
    for x in xs:
        for y in ys:
            b.append([S('via'),[S('at'),x,y],[S('size'),.7],[S('drill'),.3],[S('layers'),'F.Cu','B.Cu'],[S('net'),net],[S('uuid'),str(uuid.uuid4())]])
            added.append(dict(net=net,x_mm=x,y_mm=y,in_pad=True,finish='resin-filled and copper-capped'))
(K/'MV24_RevF1.kicad_pcb').write_text(n.sx.dumps(b)+'\n')
(K/'MV24_RevF1.kicad_sch').write_text(n.sx.dumps(s)+'\n')
project=json.loads((K/'MV24_RevF1.kicad_pro').read_text())
ignored={k:v for k,v in project.get('erc',{}).get('rule_severities',{}).items() if v=='ignore'}
# Re-enable previously ignored categories to inspect rather than conceal them.
for key in ignored:project['erc']['rule_severities'][key]='warning'
(K/'MV24_RevF1.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
with (BASE/'Procurement/BOM.csv').open(newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames; rows=list(reader)
for row in rows:
    row.update(unit_price='',stock='',eta='',status='Rev F1 prototype candidate; availability not refreshed',purchase_note='',purchase_quantity=row['quantity'])
    if row['refs'] in changes:
        a=changes[row['refs']];row.update(mpn=a['mpn'],value=a['value'],url=a['url'],sku='',supplier='Manufacturer source; distributor selection pending',purchase_note=a['reason'])
        if 'footprint' in a:row['footprint']=a['footprint']
with (OUT/'Procurement/BOM.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
(OUT/'Verification/revision-edits.json').write_text(json.dumps(dict(changes=changes,added_thermal_vias=added,restored_erc_categories=ignored,
    copper_um=[70,35,35,70],thickness_mm=1.6,finish='ENIG',new_fitted_components=0,unchanged_mosfets=['Q1','Q2'],precharge='not implemented; user deferred'),indent=2)+'\n')
print('Updated 3 fitted components; thermal vias added:',{net:sum(x['net']==net for x in added) for net in ['/VIN','/SW']},'Restored ERC categories:',ignored)
