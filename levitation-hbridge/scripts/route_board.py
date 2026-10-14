"""Deterministic two-outer-layer router with geometric clearance masks.
Power transfer uses 12 mm corridor pours; signal stubs do not carry coil current.
Final authority is native KiCad DRC, never this router's own occupancy grid.
"""
from design import *
import pcbnew as p,wx,numpy as np,math,heapq,time
from scipy.ndimage import distance_transform_edt
from shapely.geometry import Point,box,LineString,Polygon
from shapely.ops import unary_union
from shapely import contains_xy
app=wx.App(False); b=p.LoadBoard(str(ROOT/'poc_lev.kicad_pcb'))
MM=p.FromMM; V=lambda x,y:p.VECTOR2I(MM(x),MM(y)); xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
L=[p.F_Cu,p.B_Cu];STEP=.2;X0=12;Y0=18;NX=731;NY=481
FP={f.GetReference():f for f in b.GetFootprints()};P={f.GetReference()+'.'+a.GetNumber():a for f in b.GetFootprints() for a in f.Pads() if a.GetNumber()};N={n:b.FindNet('/'+n) for n in NETS}
POWER=['GND','+60V','SW_A','SW_B','COIL_A'];GATE=['G_Q1','G_Q2','G_Q3','G_Q4','HO_A','LO_A','HO_B','LO_B','OFF_Q1','OFF_Q2','OFF_Q3','OFF_Q4']
# Clear previous tracks and zones so reruns are deterministic.
for t in list(b.GetTracks()):b.RemoveNative(t)
for z in list(b.Zones()):b.RemoveNative(z)
geo=[]; tracks=[];vias=[]
# Shapes are conservative rectangular pad envelopes including rotated shapes.
for key,pad in P.items():
    print('PAD',key,type(pad.GetPosition()),type(pad.GetSize()),flush=True) if not hasattr(pad.GetSize(),'x') or not hasattr(pad.GetPosition(),'x') else None
    cx,cy=xy(pad.GetPosition());sx,sy=xy(pad.GetSize());a=math.radians(pad.GetOrientationDegrees())
    corners=[(cx+u*math.cos(a)-v*math.sin(a),cy+u*math.sin(a)+v*math.cos(a)) for u,v in [(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)]]
    g=Polygon(corners)
    lay=[0,1] if pad.GetAttribute()==p.PAD_ATTRIB_PTH else [0]
    if pad.GetAttribute()==p.PAD_ATTRIB_NPTH:lay=[0,1]
    n=pad.GetNetname().lstrip('/') or '__HOLE__'
    geo.append((n,lay,g,'pad',key))
for ref in ['H1','H2','H3','H4']:
    c=xy(FP[ref].GetPosition());geo.append(('__HOLE__',[0,1],Point(*c).buffer(1.6),'hole',ref))
def zone(n,l,g,pri=0):
    if g.geom_type=='MultiPolygon':
        for part in g.geoms:zone(n,l,part,pri)
        return
    z=p.ZONE(b);z.SetNet(N[n]);z.SetLayer(l);z.SetLocalClearance(MM(.4));z.SetMinThickness(MM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetAssignedPriority(pri);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.Outline().NewOutline()
    for x,y in list(g.exterior.coords)[:-1]:z.Outline().Append(MM(x),MM(y))
    b.Add(z)
plane=box(12.6,18.6,157.4,113.4)
zone('GND',p.In1_Cu,plane);zone('+60V',p.In2_Cu,plane);zone('GND',p.F_Cu,plane);zone('+60V',p.B_Cu,plane)
# Thick pours between power pins; clipped by lower-priority plane, pads and signal tracks.
powerpaths={
'SW_A':([(37.54,30),(65.08,30),(73,43),(73,57),(116.4,57)],1),
'SW_B':([(87.54,30),(115.08,30),(125,42),(145,42),(145,90)],1),
'COIL_A':([(121.6,57),(132.3,57),(132.3,77)],0)}
for n,(pts,l) in powerpaths.items():
    g=LineString(pts).buffer(6,join_style=2,cap_style=2);zone(n,L[l],g,2);geo.append((n,[l],g,'power_zone',n))
for net,x1,x2 in [('SW_A',33,69),('SW_B',83,119)]:
    g=box(x1,19.5,x2,31.6);zone(net,p.F_Cu,g,2);geo.append((net,[0],g,'power_zone','front-power-bridge'))
# Feed R1 power lands with 12-via arrays on bridge side; short solid top copper patch.
g=box(109.5,54.3,117.3,59.7);zone('SW_A',p.F_Cu,g,3);geo.append(('SW_A',[0],g,'power_zone','R1-feed'))
def addtrack(n,l,a,c,width):
    if math.dist(a,c)<.00001:return
    t=p.PCB_TRACK(b);t.SetStart(V(*a));t.SetEnd(V(*c));t.SetWidth(MM(width));t.SetLayer(L[l]);t.SetNet(N[n]);b.Add(t);tracks.append((n,l,a,c,width));geo.append((n,[l],LineString([a,c]).buffer(width/2),'track',''))
def addvia(n,a,d=.7,drill=.35):
    if any(nn==n and math.dist(aa,a)<.2 for nn,aa,dd in vias):return
    v=p.PCB_VIA(b);v.SetPosition(V(*a));v.SetWidth(MM(d));v.SetDrill(MM(drill));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(N[n]);b.Add(v);vias.append((n,a,d));geo.append((n,[0,1],Point(*a).buffer(d/2),'via',''))
for xx in [110.5,112,113.5,115]:
    for yy in [55,57,59]:addvia('SW_A',(xx,yy),.9,.45)
# Minimum clearance computation from actual shapes, with grid sampling margin.
def paint(mask,g,layers,buffer):
    g=g.buffer(buffer);a,c,d,e=g.bounds
    i0=max(0,int(math.floor((a-X0)/STEP)));i1=min(NX-1,int(math.ceil((d-X0)/STEP)))
    j0=max(0,int(math.floor((c-Y0)/STEP)));j1=min(NY-1,int(math.ceil((e-Y0)/STEP)))
    if i0>i1 or j0>j1:return
    xx=X0+np.arange(i0,i1+1)*STEP;yy=Y0+np.arange(j0,j1+1)*STEP
    occ=contains_xy(g,xx[None,:],yy[:,None])
    for l in layers:mask[l,j0:j1+1,i0:i1+1]|=occ

def masks(n,w):
    m=np.zeros((2,NY,NX),dtype=bool);vm=np.zeros_like(m)
    equiv={'SNS_P':{'SW_A'},'SNS_N':{'COIL_A'},'SW_A':{'SNS_P'},'COIL_A':{'SNS_N'}}
    for other,ls,g,typ,key in geo:
        if typ=='power_zone':continue  # Native zone fill creates copper clearance; avoid false routing dead ends.
        same=other==n or (key.startswith('R1.') and other in equiv.get(n,set()))
        if typ=='power_zone' and other in equiv.get(n,set()):same=True
        if not same:
            paint(m,g,ls,(.24 if typ!='power_zone' else .45)+w/2+.08)
            if typ!='power_zone':paint(vm,g,ls,.24+.35+.08)
        elif typ=='pad': # no via in paste pads, including same-net pads
            paint(vm,g,ls,.4)
        elif typ=='via': # Reuse its center explicitly; do not drill a second nearby hole.
            paint(vm,g,ls,.6)
    m[:,:5,:]=True;m[:,-5:,:]=True;m[:,:,:5]=True;m[:,:,-5:]=True
    vm[:,:5,:]=True;vm[:,-5:,:]=True;vm[:,:,:5]=True;vm[:,:,-5:]=True
    return m,np.any(vm,axis=0)
def ij(a):return (int(round((a[0]-X0)/STEP)),int(round((a[1]-Y0)/STEP)))
def coords(x,y):return(round(X0+x*STEP,5),round(Y0+y*STEP,5))
def node(l,x,y):return(l*NY+y)*NX+x
def decode(z):x=z%NX;z//=NX;return z//NY,x,z%NY
ROUTE_LOG=[]
def route(n,a,c,w=.25,allowvias=True,startlayers=[0],endlayers=[0]):
    m,vm=masks(n,w);sx,sy=ij(a);tx,ty=ij(c)
    # Existing same-net vias are already real inter-layer connections. Their smaller
    # diameters may be legal even where the new 0.7 mm via mask is conservative.
    for nn,aa,dd in vias:
        if nn==n:
            vi,vj=ij(aa);vm[vj,vi]=False;m[:,vj,vi]=False
    starts=[node(l,sx,sy) for l in startlayers];goals={node(l,tx,ty) for l in endlayers}
    # Exact pad escape included as sub-grid segment; local matching cell permitted.
    for l in startlayers:m[l,sy,sx]=False
    for l in endlayers:m[l,ty,tx]=False
    def h(x,y,l):
        dx=abs(x-tx);dy=abs(y-ty);return max(dx,dy)+.414214*min(dx,dy)+(0 if l in endlayers else 15)
    queue=[(h(sx,sy,l),0,z) for l,z in zip(startlayers,starts)];heapq.heapify(queue);best={z:0 for z in starts};prev={};found=None;count=0
    dirs=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414214),(-1,1,1.414214),(1,-1,1.414214),(-1,-1,1.414214)]
    while queue:
        _,g,z=heapq.heappop(queue)
        if g!=best.get(z):continue
        if z in goals:found=z;break
        count+=1
        if count>600000:break
        l,x,y=decode(z)
        for dx,dy,cost in dirs:
            xx=x+dx;yy=y+dy
            if not(0<=xx<NX and 0<=yy<NY) or m[l,yy,xx]:continue
            if dx and dy and (m[l,y,xx] or m[l,yy,x]):continue
            zz=node(l,xx,yy);gg=g+cost
            if gg<best.get(zz,1e30):best[zz]=gg;prev[zz]=z;heapq.heappush(queue,(gg+1.05*h(xx,yy,l),gg,zz))
        if allowvias and not vm[y,x]:
            ll=1-l;zz=node(ll,x,y);gg=g+22
            if gg<best.get(zz,1e30):best[zz]=gg;prev[zz]=z;heapq.heappush(queue,(gg+1.05*h(x,y,ll),gg,zz))
    if found is None:
        ROUTE_LOG.append(dict(net=n,start=a,end=c,status='FAILED',visited=count));print('FAILED',n,a,c,count,flush=True);return False
    path=[found]
    while path[-1] in prev:path.append(prev[path[-1]])
    path=path[::-1];points=[decode(z) for z in path]
    # Coalesce collinear grid segments. Start/end connect to precise pad center.
    l=points[0][0];last=a;run=[];length=0
    def flush(seq,l,start,end_exact=None):
        nonlocal length
        ps=[start]+[coords(x,y) for _,x,y in seq]+([end_exact] if end_exact else [])
        slim=[]
        for pt in ps:
            if slim and math.dist(slim[-1],pt)<1e-6:continue
            while len(slim)>1:
                v1=(slim[-1][0]-slim[-2][0],slim[-1][1]-slim[-2][1]);v2=(pt[0]-slim[-1][0],pt[1]-slim[-1][1])
                if abs(v1[0]*v2[1]-v1[1]*v2[0])<1e-7 and v1[0]*v2[0]+v1[1]*v2[1]>=0:slim.pop()
                else:break
            slim.append(pt)
        for aa,cc in zip(slim,slim[1:]):addtrack(n,l,aa,cc,w);length+=math.dist(aa,cc)
    for t in points:
        if t[0]!=l:
            aa=coords(t[1],t[2])
            reuse=[pos for nn,pos,d in vias if nn==n and math.dist(pos,aa)<.15]
            if reuse:aa=min(reuse,key=lambda pos:math.dist(pos,aa))
            flush(run,l,last,aa);addvia(n,aa);l=t[0];last=aa;run=[]
        run.append(t)
    flush(run,l,last,c)
    ROUTE_LOG.append(dict(net=n,start=a,end=c,status='ROUTED',length_mm=round(length,3),vias=sum(points[i][0]!=points[i-1][0] for i in range(1,len(points)))))
    print('Routed',n,round(length,2),'mm',flush=True)
    return True

def padlayers(pad):return [0,1] if pad.GetAttribute()==p.PAD_ATTRIB_PTH else [0]
def routepins(n,keys,width=.25,allowvias=True):
    keys=list(keys)
    if len(keys)<2:return
    connected=[keys.pop(0)]
    while keys:
        _,a,c=min((math.dist(xy(P[a].GetPosition()),xy(P[c].GetPosition())),a,c) for a in connected for c in keys)
        route(n,xy(P[a].GetPosition()),xy(P[c].GetPosition()),width,allowvias,padlayers(P[a]),padlayers(P[c]));connected.append(c);keys.remove(c)
# Ground return and INA supply reference are routed before competing signals.
addvia('GND',(116.265,73.075),.6,.3)
addtrack('GND',0,xy(P['U3.2'].GetPosition()),(116.265,73.075),.25)
for q,u in [(2,1),(4,2)]:route('GND',xy(P['Q%d.3'%q].GetPosition()),xy(P['U%d.3'%u].GetPosition()),.45,False,[0],[0])
# Explicit local routes keep COM capacitor returns inside the driver body.
def manual(n,pts,w=.45):
    for a,c in zip(pts,pts[1:]):addtrack(n,0,a,c,w)
for off,u in [(0,1),(50,2)]:
    def loc(n,pts,w=.45):manual(n,[(x+off,y) for x,y in pts],w)
    loc('GND',[(47.525,28.635),(49.5,28.635),(50,29.135),(50,30.8),(50.95,32.15)])
    loc('GND',[(50,30.8),(47.25,30.8),(47.25,32.2)])
    loc('+12V',[(52.475,29.905),(52.85,30.28),(52.85,32.15)])
    loc('+12V',[(52.85,32.15),(52.85,34),(50.9,34),(49.15,32.2)])
    loc('HO_A' if u==1 else 'HO_B',[(52.475,27.365),(53.89,27.365),(53.89,28.43),(56.2,28.43),(56.2,30.4875),(55.5,31.1875)],.4)
    sn='SW_A' if u==1 else 'SW_B'
    loc(sn,[(52.475,28.635),(53.145,28.635),(53.69,29.18),(53.95,29.18),(54.85,29.18),(55.05,29.38)],.4)
    addvia(sn,(53.95+off,29.18),.6,.3)
    pts=[(65.08,30),(64.4,29.32),(64.4,28.8),(64,28.4),(54.73,28.4),(53.95,29.18)]
    for a,c in zip(pts,pts[1:]):addtrack(sn,1,(a[0]+off,a[1]),(c[0]+off,c[1]),.45)
    loc('LO_A' if u==1 else 'LO_B',[(47.525,29.905),(46,29.905),(46,35.5),(48.4125,35.5),(48.4125,34.55),(47.4625,34.55)])
# Gate landing and off paths are routed around the explicit driver routes.
for n in GATE:
    keys=[k for k in NETS[n] if k not in ['R3.2','R6.2','R7.2','R10.2']]
    if n.startswith('G_Q'):
        for k in keys[1:]:route(n,xy(P[keys[0]].GetPosition()),xy(P[k].GetPosition()),.45,False,padlayers(P[keys[0]]),[0])
    elif n.startswith('HO_'):route(n,xy(P[keys[0]].GetPosition()),xy(P[keys[1]].GetPosition()),.45,False)
    elif n.startswith('LO_'):route(n,xy(P[keys[0]].GetPosition()),xy(P[keys[-1]].GetPosition()),.45,False)
    else:routepins(n,keys,.45,False)
# Bootstrap and supply caps local to each driver.
for n in ['VB_A','VB_B','BOOT_A','BOOT_B']:routepins(n,NETS[n],.45,True)
# Kelvin pair starts at inner shunt land edges, not force pad centers.
for n in ['SNS_P','SNS_N','SNS_P_F','SNS_N_F']:routepins(n,NETS[n],.25,False)
# Remaining gate pulldown branches, far from switching paths.
for n,k in [('G_Q1','R3.2'),('G_Q2','R6.2'),('G_Q3','R7.2'),('G_Q4','R10.2')]:
    nearest=min((z for z in NETS[n] if z!=k),key=lambda z:math.dist(xy(P[z].GetPosition()),xy(P[k].GetPosition())))
    route(n,xy(P[nearest].GetPosition()),xy(P[k].GetPosition()),.45,True,padlayers(P[nearest]),[0])
# Source-reference low-current branches to switch node. Power current stays in pours.
for n,q in [('SW_A','Q1.3'),('SW_B','Q3.3')]:
    keys=[k for k in NETS[n] if not k.startswith(('Q','J','R1.','U','C'))]
    routepins(n,[q]+keys,.45,True)
addtrack('GND',0,xy(P['U4.2'].GetPosition()),(114.9,101),.25);addvia('GND',(114.9,101),.6,.3)
addtrack('GND',0,xy(P['C23.2'].GetPosition()),(120.2,100.05),.25);addvia('GND',(120.2,100.05),.6,.3)
manual('+3.3V',[(116.1375,101),(118,101),(118.7,101.95)],.25)
# Establish off-pad escapes for the compact buffer before long supply/control routing.
for net,pin,end in [('PWM_A_IN','U4.1',(112.5,100.05)),('PWM_B_IN','U4.3',(112.5,101.95)),('PWM_B','U4.4',(117.35,101.95)),('PWM_A','U4.6',(117.35,100.05))]:
    addtrack(net,0,xy(P[pin].GetPosition()),end,.25);addvia(net,end,.6,.3)
for n in ['SD','+12V','+12V_IN','+3.3V','PWM_A_IN','PWM_B_IN','PWM_A','PWM_B','ISNS']:
    routepins(n,NETS[n],.45 if n.startswith('+12') else .25,True)
# Every SMD plane pad gets a nearby feed via; no dependence on incidental outer fill.
for n in ['GND','+60V']:
    for key in NETS[n]:
        pad=P[key]
        if pad.GetAttribute()==p.PAD_ATTRIB_PTH:continue
        if key in ['C14.2','C15.2','C18.2','C19.2','U1.3','U2.3','U4.2','C23.2']:continue
        a=xy(pad.GetPosition());m,vm=masks(n,.6);chosen=None
        # Prefer escapes normal to long side; select nearest legal via off pad.
        candidates=[]
        for radius in [.9,1.2,1.5,1.8,2.2,2.6,3.2]:
            for theta in range(0,360,30):
                c=(a[0]+radius*math.cos(math.radians(theta)),a[1]+radius*math.sin(math.radians(theta)));ii,jj=ij(c);c=coords(ii,jj)
                if 0<=ii<NX and 0<=jj<NY and not vm[jj,ii]:candidates.append(c)
            if candidates:break
        for c in candidates[:3]:
            if route(n,a,c,.3 if key.startswith('U') else .6,False,[0],[0]):chosen=c;addvia(n,c);break
        if chosen is None:print('PLANE FEED FAILED',key,flush=True)
    print('Plane feeds',n,flush=True)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(ROOT/'poc_lev.kicad_pcb'),b)
(ROOT/'reports/routing.json').write_text(json.dumps(ROUTE_LOG,indent=2))
(ROOT/'reports/copper_paths.json').write_text(json.dumps(dict(tracks=tracks,vias=vias),indent=2))
print('Finished',len(tracks),'segments',len(vias),'vias; failures',sum(x['status']=='FAILED' for x in ROUTE_LOG),flush=True)
