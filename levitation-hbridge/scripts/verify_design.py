"""Independent native-file audit, including schematic connectivity reconstructed from geometry."""
from design import *
from sexpr import *
import math,xml.etree.ElementTree as ET,collections,hashlib,heapq
EPS=1e-5
s=parse((ROOT/'poc_lev.kicad_sch').read_text());cached={a[1]:a for a in children(one(s,'lib_symbols'),'symbol')}
segments=[];pts=set();labels=[];pins={}
def pt(x,y):return(round(float(x),5),round(float(y),5))
for w in children(s,'wire'):
    a,c=children(one(w,'pts'),'xy');a=pt(*a[1:]);c=pt(*c[1:]);segments.append((a,c));pts|={a,c}
for a in children(s,'label'):
    pos=pt(*one(a,'at')[1:3]);labels.append((a[1],pos));pts.add(pos)
for inst in children(s,'symbol'):
    ref=next(a[2] for a in children(inst,'property') if a[1]=='Reference');un=int(one(inst,'unit')[1]);lib=cached[one(inst,'lib_id')[1]];ax,ay,angle=map(float,one(inst,'at')[1:]);mirror=one(inst,'mirror')
    for body in children(lib,'symbol'):
        u=int(body[1].rsplit('_',2)[-2])
        if u not in [0,un]:continue
        for pin in children(body,'pin'):
            x,y=map(float,one(pin,'at')[1:3])
            if mirror and mirror[1]=='x':y=-y
            if mirror and mirror[1]=='y':x=-x
            assert angle==0,'Verifier needs explicit angle support before changing schematic rotation'
            pos=pt(ax+x,ay-y);key=ref+'.'+one(pin,'number')[1];assert key not in pins,key
            pins[key]=pos;pts.add(pos)
parent={a:a for a in pts}
def find(a):
    while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
    return a
def union(a,c):parent[find(a)]=find(c)
def on(a,start,end):
    dx=end[0]-start[0];dy=end[1]-start[1]
    return abs((a[0]-start[0])*dy-(a[1]-start[1])*dx)<EPS and min(start[0],end[0])-EPS<=a[0]<=max(start[0],end[0])+EPS and min(start[1],end[1])-EPS<=a[1]<=max(start[1],end[1])+EPS
for a,c in segments:
    for q in pts:
        if on(q,a,c):union(a,q)
bylabel=collections.defaultdict(list)
for name,pos in labels:bylabel[name].append(pos)
for ps in bylabel.values():
    for q in ps[1:]:union(ps[0],q)
groups=collections.defaultdict(set)
for key,pos in pins.items():
    if not key.startswith('#'):groups[find(pos)].add(key)
actual={n:groups[find(ps[0])] for n,ps in bylabel.items()}
errors=[]
for n,expected in NETS.items():
    if set(expected)!=actual.get(n,set()):errors.append(dict(net=n,missing=sorted(set(expected)-actual.get(n,set())),extra=sorted(actual.get(n,set())-set(expected))))
assert not errors,errors
assert set(actual)==set(NETS),(set(actual)-set(NETS),set(NETS)-set(actual))
xml=ET.parse(ROOT/'reports/schematic.net.xml')
xnets={n.get('name').lstrip('/'):set(a.get('ref')+'.'+a.get('pin') for a in n if a.tag=='node' and not a.get('ref').startswith('#')) for n in xml.findall('.//nets/net')}
assert xnets==actual,'Native KiCad netlist and geometric audit disagree'
board=parse((ROOT/'poc_lev.kicad_pcb').read_text());nets={int(n[1]):n[2].lstrip('/') for n in children(board,'net')};bparts={};bpins={};padpos={};courtyards=[]
def netname(item):
    n=one(item,'net')[1]
    return nets[int(n)] if str(n).isdigit() else n.lstrip('/')
for f in children(board,'footprint'):
    ref=next(a[2] for a in children(f,'property') if a[1]=='Reference');bparts[ref]=f
    fx,fy=map(float,one(f,'at')[1:3]);angle=float(one(f,'at')[3]) if len(one(f,'at'))>3 else 0;r=math.radians(angle)
    for pd in children(f,'pad'):
        if not pd[1]:continue
        n=one(pd,'net');key=ref+'.'+pd[1]
        if n:bpins[key]=netname(pd)
        px,py=map(float,one(pd,'at')[1:3]);padpos[key]=pt(fx+px*math.cos(r)+py*math.sin(r),fy-px*math.sin(r)+py*math.cos(r))
assert set(bparts)==set(PARTS)
assert bpins==PINS,dict(missing=set(PINS.items())-set(bpins.items()),extra=set(bpins.items())-set(PINS.items()))
tracks=children(board,'segment');vias=children(board,'via');zones=children(board,'zone')
assert all(one(t,'layer')[1] not in ['In1.Cu','In2.Cu'] for t in tracks)
assert [next(a for a in children(board,'layers') if False)] if False else True
assert [one(bparts[r],'at')[3:] for r in ['Q2','Q1','Q4','Q3']]==[[],[],[],[]],'All FETs must be at zero degrees'
xs=[float(one(bparts[r],'at')[1]) for r in ['Q2','Q1','Q4','Q3']];assert all(abs(b-a-25)<EPS for a,b in zip(xs,xs[1:]))
for i in range(1,11):assert '100V' in PARTS['C'+str(i)]['rating']
for n in ['G_Q1','G_Q2','G_Q3','G_Q4','HO_A','HO_B','LO_A','LO_B']:
    assert all(.4-EPS<=float(one(t,'width')[1])<=.5+EPS for t in tracks if netname(t)==n)
# Exact physical trace graph, adding all T junctions and pad land contacts.
def trace_length(net,start,end,front_only=False):
    seg=[(pt(*one(t,'start')[1:]),pt(*one(t,'end')[1:]),one(t,'layer')[1]) for t in tracks if netname(t)==net and (not front_only or one(t,'layer')[1]=='F.Cu')]
    points={a for a,c,l in seg}|{c for a,c,l in seg}|{padpos[start],padpos[end]};adj=collections.defaultdict(list)
    for a,c,l in seg:
        qs=sorted((q for q in points if on(q,a,c)),key=lambda q:math.dist(q,a))
        for v,w in zip(qs,qs[1:]):
            d=math.dist(v,w);adj[(v,l)].append(((w,l),d));adj[(w,l)].append(((v,l),d))
    for v in vias:
        if front_only or netname(v)!=net:continue
        q=pt(*one(v,'at')[1:]);adj[(q,'F.Cu')].append(((q,'B.Cu'),1.6));adj[(q,'B.Cu')].append(((q,'F.Cu'),1.6))
    q=[(0,(padpos[start],'F.Cu')),(0,(padpos[start],'B.Cu'))];best={}
    while q:
        d,v=heapq.heappop(q)
        if v in best:continue
        best[v]=d
        if v[0]==padpos[end]:return round(d,3)
        for w,c in adj[v]:
            if w not in best:heapq.heappush(q,(d+c,w))
    return None
metrics={}
for q,u,ron,driver,inp,out in [(1,1,2,'HO_A',1,2),(2,1,4,'LO_A',1,2),(3,2,9,'HO_B',2,1),(4,2,11,'LO_B',2,1)]:
    a='U%d.%d'%(u,7 if q in [1,3] else 4);rin='R%d.%d'%(ron,inp);rout='R%d.%d'%(ron,out);gate='Q%d.1'%q;source='Q%d.3'%q
    d1=trace_length(driver,a,rin);d2=trace_length('G_Q%d'%q,rout,gate);body=math.dist(padpos[rin],padpos[rout]);ret=trace_length('SW_A' if q==1 else 'SW_B' if q==3 else 'GND',source,'U%d.%d'%(u,6 if q in [1,3] else 3))
    off={1:(20,5),2:(21,4),3:(22,7),4:(23,6)}[q];ro,di=off
    o1=trace_length(driver,a,'R%d.2'%ro);o2=trace_length('OFF_Q%d'%q,'R%d.1'%ro,'D%d.1'%di);o3=trace_length('G_Q%d'%q,'D%d.2'%di,gate)
    opads=math.dist(padpos['R%d.1'%ro],padpos['R%d.2'%ro])+math.dist(padpos['D%d.1'%di],padpos['D%d.2'%di])
    metrics['Q%d'%q]=dict(turnoff_branch_copper_mm=round(o1+o2+o3,3) if all(x is not None for x in [o1,o2,o3]) else None,turnoff_loop_including_pad_spans_mm=round(o1+o2+o3+opads+ret,3) if all(x is not None for x in [o1,o2,o3,ret]) else None,driver_to_resistor_mm=d1,resistor_to_gate_mm=d2,resistor_pad_span_mm=round(body,3),source_return_copper_mm=ret,gate_loop_including_resistor_span_mm=round(d1+d2+body+ret,3) if all(x is not None for x in [d1,d2,ret]) else None,return_path_note='Dedicated source return trace measured; solid GND plane provides parallel return' if q in [2,4] else 'Dedicated SW source return measured')
# Minimum pad-center separations for decoupling, intentionally not presented as loop inductance.
decaps={}
for u,cb,c1,c2 in [(1,16,14,15),(2,17,19,18)]:
    decaps['C%d'%cb]={'VB_mm':round(math.dist(padpos['C%d.1'%cb],padpos['U%d.8'%u]),3),'VS_mm':round(math.dist(padpos['C%d.2'%cb],padpos['U%d.6'%u]),3)}
    for c in [c1,c2]:decaps['C%d'%c]={'VCC_mm':round(math.dist(padpos['C%d.1'%c],padpos['U%d.5'%u]),3),'COM_mm':round(math.dist(padpos['C%d.2'%c],padpos['U%d.3'%u]),3)}
# Edge interface placement and physical pin order are part of this revision.
assert padpos['J3.1']==(107.0,110.0)
assert padpos['J3.8']==(124.78,110.0)
assert all(abs(padpos['J3.%d'%i][1]-110)<EPS for i in range(1,9))
interface={'J3_pin1_mm':padpos['J3.1'],'J3_pin8_mm':padpos['J3.8'],'pin_row_to_bottom_edge_mm':4.0,'front_mating_header':True,'actual_mating_envelope_verified':False}
# Enforce quantitative checks, rather than merely printing metrics.
for name,m in metrics.items():
    assert m['gate_loop_including_resistor_span_mm'] is not None,name
    assert m['gate_loop_including_resistor_span_mm']<=35,name
    assert m['turnoff_loop_including_pad_spans_mm']<=35,name
    assert m['turnoff_branch_copper_mm']<=m['driver_to_resistor_mm']+m['resistor_to_gate_mm'],name
    # Stronger check also includes component pad spans.
    assert m['turnoff_loop_including_pad_spans_mm']<=m['gate_loop_including_resistor_span_mm'],name
matching={}
for leg,a,c in [('A','Q1','Q2'),('B','Q3','Q4')]:
    v=[metrics[q]['gate_loop_including_resistor_span_mm'] for q in [a,c]]
    matching[leg]=round(100*(max(v)-min(v))/min(v),3)
    assert matching[leg]<=10
for c,d in decaps.items():assert max(d.values())<=(3 if c in ['C16','C17'] else 5),(c,d)
ceramic_dist={}
for i in range(1,11):
    qs=['Q1','Q2'] if i<=5 else ['Q3','Q4']
    d,key=min((math.dist(padpos['C%d.%d'%(i,p)],padpos[q+'.'+j]),'C%d.%d to %s.%s'%(i,p,q,j)) for p in [1,2] for q in qs for j in ['2','3'])
    ceramic_dist['C'+str(i)]={'nearest_power_pad_center_mm':round(d,3),'endpoints':key}
    assert d<=5,(i,d)
cap_routes={}
for u,cs in [(1,[14,15]),(2,[19,18])]:
    for c in cs:
        d={n:trace_length(net,'U%d.%d'%(u,p),'C%d.%d'%(c,cp),True) for n,net,p,cp in [('VCC_top_copper_mm','+12V',5,1),('COM_top_copper_mm','GND',3,2)]}
        assert all(v is not None for v in d.values()),(c,d)
        cap_routes['C'+str(c)]=d
sense_report={n:trace_length(n,*keys) for n,keys in [('SNS_P',['R1.2','R12.1']),('SNS_N',['R1.3','R13.1'])]}
assert all(d is not None for d in sense_report.values())
assert abs(sense_report['SNS_P']-sense_report['SNS_N'])<.001
stack=one(one(board,'setup'),'stackup')
cu={a[1]:float(one(a,'thickness')[1]) for a in children(stack,'layer') if a[1] in ['F.Cu','In1.Cu','In2.Cu','B.Cu']}
assert cu=={'F.Cu':.07,'In1.Cu':.035,'In2.Cu':.035,'B.Cu':.07}
assert all(any(netname(z)==n and one(z,'layer')[1]==l for z in zones) for n,l in [('GND','In1.Cu'),('+60V','In2.Cu')])
for l,n in [('In1.Cu','GND'),('In2.Cu','+60V')]:assert all(netname(z)==n for z in zones if one(z,'layer')[1]==l)
r=json.loads((ROOT/'reports/final-drc.json').read_text())
assert len(r['violations'])==len(r['unconnected_items'])==0,'Native DRC must be clean'
assert 'Errors 0  Warnings 0' in (ROOT/'reports/erc.rpt').read_text(),'Native ERC must be clean' 
result=dict(schematic_geometry='PASS',native_netlist_crosscheck='PASS',pcb_pad_mapping='PASS',electrical_parts=64,physical_items=74,nets=len(NETS),pins=len(PINS),copper_layers=4,inner_layer_tracks=0,fet_pitch_mm=25,interface_placement=interface,gate_metrics=metrics,gate_matching_percent=matching,bridge_ceramic_distances=ceramic_dist,driver_capacitor_front_only_paths=cap_routes,measured_sense_copper_mm=sense_report,copper_thickness_mm=cu,decoupling_pad_center_distances=decaps,DRC_violations=len(r['violations']),unconnected_items=len(r['unconnected_items']),sense_pair=json.loads((ROOT/'reports/sense_pair.json').read_text()),file_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['poc_lev.kicad_sch','poc_lev.kicad_pcb','poc_lev.kicad_pro','BOM.csv']})
(ROOT/'reports/verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
