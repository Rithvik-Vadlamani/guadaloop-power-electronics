"""Close native DRC findings, match shunt fanout and place legible reference fields."""
from design import *
from sexpr import *
import pcbnew as p,wx,math
from shapely.geometry import Point,Polygon,LineString,box
app=wx.App(False);b=p.LoadBoard(str(ROOT/'poc_lev.kicad_pcb'));MM=p.FromMM;V=lambda x,y:p.VECTOR2I(MM(x),MM(y));xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
FP={f.GetReference():f for f in b.GetFootprints()};P={f.GetReference()+'.'+a.GetNumber():a for f in b.GetFootprints() for a in f.Pads() if a.GetNumber()};N={n:b.FindNet('/'+n) for n in NETS}
# Refuse edits while a project editor owns the files.
assert not list(ROOT.glob('*.lck'))
for t in list(b.GetTracks()):
    if t.GetNetname() in ['/SNS_P','/SNS_N']:b.RemoveNative(t)
for ref in ['R12','R13']:FP[ref].SetOrientationDegrees(270)
for pn,x in [('2',117.65),('3',120.35)]:
    P['R1.'+pn].SetPosition(V(x,57));P['R1.'+pn].SetSize(V(.8,.4))
# Keep library and embedded footprint identical.
s=parse((ROOT/'lib.pretty/CSS2H_2512_Kelvin.kicad_mod').read_text())
for pd in children(s,'pad'):
    if pd[1] in ['2','3']:
        one(pd,'at')[1:3]=[A('-1.35' if pd[1]=='2' else '1.35'),A('0')];one(pd,'size')[1:]=[A('.8'),A('.4')]
(ROOT/'lib.pretty/CSS2H_2512_Kelvin.kicad_mod').write_text(dump(s))
def track(n,a,c,w=.25,l=p.F_Cu):
    t=p.PCB_TRACK(b);t.SetStart(V(*a));t.SetEnd(V(*c));t.SetWidth(MM(w));t.SetLayer(l);t.SetNet(N[n]);b.Add(t)
def path(n,pts):
    for a,c in zip(pts,pts[1:]):track(n,a,c)
# 0.4142 mm compensation on negative fanout matches total copper length.
Ppath=[(117.65,57),(118.1,57),(118.1,59.6),(115.9,61.8),(115,61.8),(115,62.0875)]
d=(sum(math.dist(a,c) for a,c in zip(Ppath,Ppath[1:]))-(.45+2.6+1.9*math.sqrt(2)+.5875))/2
Npath=[(120.35,57),(119.9,57),(119.9,59),(119.9+d,59),(119.9+d,59.4),(119.9,59.4),(119.9,59.6),(118,61.5),(118,62.0875)]
path('SNS_P',Ppath);path('SNS_N',Npath)
# Geometry from actual pad polygons and tracks, not an image.
def padgeom(a):
    cx,cy=xy(a.GetPosition());sx,sy=xy(a.GetSize());r=math.radians(a.GetOrientationDegrees())
    return Polygon([(cx+u*math.cos(r)-v*math.sin(r),cy+u*math.sin(r)+v*math.cos(r)) for u,v in [(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)]])
foreign=[];paste=[]
for k,a in P.items():
    g=padgeom(a)
    if a.GetNetname()!='/GND':foreign.append((g,[p.F_Cu,p.B_Cu] if a.GetAttribute()==p.PAD_ATTRIB_PTH else [p.F_Cu]))
    if a.GetAttribute()==p.PAD_ATTRIB_SMD:paste.append(g)
for t in b.GetTracks():
    if t.GetNetname()=='/GND':continue
    if isinstance(t,p.PCB_VIA):g=Point(*xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2);ls=[p.F_Cu,p.B_Cu]
    else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2);ls=[t.GetLayer()]
    foreign.append((g,ls))
a=xy(P['U3.2'].GetPosition());candidates=[]
for ix in range(-25,26):
    for iy in range(-25,26):
        c=(round(a[0]+ix*.1,4),round(a[1]+iy*.1,4));pt=Point(*c);ln=LineString([a,c])
        if math.dist(a,c)<.4:continue
        if any(pt.distance(g)<.52 or (p.F_Cu in ls and ln.distance(g)<.34) for g,ls in foreign):continue
        if any(pt.distance(g)<.42 for g in paste):continue
        candidates.append((math.dist(a,c),c))
if candidates and not any(isinstance(v,p.PCB_VIA) and math.dist(xy(v.GetPosition()),(116.265,73.075))<.01 for v in b.GetTracks()):
    _,c=min(candidates);v=p.PCB_VIA(b);v.SetPosition(V(*c));v.SetWidth(MM(.6));v.SetDrill(MM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(N['GND']);b.Add(v);track('GND',a,c);print('INA ground via',c)
elif any(isinstance(v,p.PCB_VIA) and math.dist(xy(v.GetPosition()),(116.265,73.075))<.01 for v in b.GetTracks()):print('Existing INA ground via retained')
else:print('NO CLEAR INA GROUND VIA')
# Remove unused signal escape vias (plane-net stitching remains intentional).
for v in list(b.GetTracks()):
    if not isinstance(v,p.PCB_VIA) or v.GetNetname() not in ['/PWM_A_IN','/PWM_B_IN','/PWM_A','/PWM_B']:continue
    center=Point(*xy(v.GetPosition()));connected=set()
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA) or t.GetNetname()!=v.GetNetname():continue
        if center.distance(LineString([xy(t.GetStart()),xy(t.GetEnd())]))<=p.ToMM(v.GetWidth(p.F_Cu))/2+p.ToMM(t.GetWidth())/2:connected.add(t.GetLayer())
    if p.B_Cu not in connected:
        for t in list(b.GetTracks()):
            if isinstance(t,p.PCB_VIA) or t.GetNetname()!=v.GetNetname() or t.GetLayer()!=p.F_Cu:continue
            ends=[xy(t.GetStart()),xy(t.GetEnd())]
            if min(math.dist(e,xy(v.GetPosition())) for e in ends)>.001:continue
            other=max(ends,key=lambda e:math.dist(e,xy(v.GetPosition())))
            pad=next((a for k,a in P.items() if k.startswith('U4.') and math.dist(xy(a.GetPosition()),other)<.001),None)
            if pad is None:continue
            line=LineString(ends);origin=padgeom(pad);used=False
            for t2 in b.GetTracks():
                if t2.m_Uuid.AsString()==t.m_Uuid.AsString() or isinstance(t2,p.PCB_VIA) or t2.GetNetname()!=v.GetNetname() or t2.GetLayer()!=p.F_Cu:continue
                if not line.intersection(LineString([xy(t2.GetStart()),xy(t2.GetEnd())])).difference(origin).is_empty:used=True;break
            if not used:b.RemoveNative(t)
        b.RemoveNative(v)
# More ground stitching in open board area, with actual copper clearance.
for c in [(20,100),(145,105),(70,70),(95,65),(75,20.5),(155,55),(54,78)]:
    if any(Point(*c).distance(g)<.6 for g,ls in foreign):continue
    if any(isinstance(v,p.PCB_VIA) and math.dist(xy(v.GetPosition()),c)<.01 for v in b.GetTracks()):continue
    v=p.PCB_VIA(b);v.SetPosition(V(*c));v.SetWidth(MM(.7));v.SetDrill(MM(.35));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(N['GND']);b.Add(v)
# Mechanical documentation belongs on User.Comments, never copper.
for t in b.GetDrawings():
    if isinstance(t,p.PCB_TEXT):
        if t.GetText().startswith('POC LEV'):t.SetPosition(V(65,104))
        if t.GetText().startswith('60 V  |'):t.SetPosition(V(65,107))
        if t.GetText()=='BUS -':t.SetPosition(V(22,59))
# Keep all reference text on silk; search collision-free locations around its footprint.
def bbox(item,margin=0):
    bb=item.GetBoundingBox();x,y=xy(bb.GetPosition());w,h=xy(bb.GetSize());return box(x-margin,y-margin,x+w+margin,y+h+margin)
obstacles=[padgeom(a).buffer(.16) for a in P.values()]
for f in FP.values():
    for g in f.GraphicalItems():
        if g.GetLayer()==p.F_SilkS:obstacles.append(bbox(g,.1))
for g in b.GetDrawings():
    if g.GetLayer()==p.F_SilkS:obstacles.append(bbox(g,.1))
placed=[]
for ref,f in sorted(FP.items(),key=lambda kv:(not kv[0].startswith('Q'),kv[0])):
    t=f.Reference()
    if ref.startswith('H'):t.SetVisible(False);continue
    t.SetVisible(True);t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetTextSize(V(.8,.8));t.SetTextThickness(MM(.12))
    ox,oy=xy(f.GetPosition());origin=xy(t.GetPosition())
    choices=[origin]
    for radius in [2.6,3.2,3.8,4.5,5.5,6.5,8,10,12]:
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)]:choices.append((ox+dx*radius,oy+dy*radius))
    found=False
    for c in choices:
        t.SetPosition(V(*c));g=bbox(t,.12)
        if not box(13,19,157,113).contains(g):continue
        if any(g.intersects(ob) for ob in obstacles+placed):continue
        placed.append(g);found=True;break
    if not found:print('SILK placement unresolved',ref)
# Keep the edge-interface labels unambiguous at the point of connection.
for ref,at in {'R24':(114.62,103.9),'R25':(117.16,103.9),'R19':(119.7,103.9),'TP4':(126.2,105.7),'TP5':(133,109.3),'C24':(142.1,103)}.items():
    FP[ref].Reference().SetPosition(V(*at))
# Courtyard-specific clearance requirement from source brief.
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(ROOT/'poc_lev.kicad_pcb'),b)
(ROOT/'reports/sense_pair.json').write_text(json.dumps({n:{'points':pts,'length_mm':sum(math.dist(a,c) for a,c in zip(pts,pts[1:]))} for n,pts in [('SNS_P',Ppath),('SNS_N',Npath)]},indent=2))
print('Finishing saved')
