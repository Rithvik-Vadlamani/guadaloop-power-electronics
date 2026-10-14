"""Parallel outer copper and clear-space stitching across the power corridors."""
from design import *
import pcbnew as p,wx,math
from shapely.geometry import Point,Polygon,LineString,box
app=wx.App(False);assert not list(ROOT.glob('*.lck'));b=p.LoadBoard(str(ROOT/'poc_lev.kicad_pcb'));MM=p.FromMM;V=lambda x,y:p.VECTOR2I(MM(x),MM(y));xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
N={n:b.FindNet('/'+n) for n in NETS};objects=[];paste=[]
for f in b.GetFootprints():
 for a in f.Pads():
  cx,cy=xy(a.GetPosition());sx,sy=xy(a.GetSize());r=math.radians(a.GetOrientationDegrees())
  g=Polygon([(cx+u*math.cos(r)-v*math.sin(r),cy+u*math.sin(r)+v*math.cos(r)) for u,v in [(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)]])
  objects.append((a.GetNetname(),g))
  if a.GetAttribute()==p.PAD_ATTRIB_SMD:paste.append(g)
for t in b.GetTracks():
 g=Point(*xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)
 objects.append((t.GetNetname(),g))
paths={'SW_A':[(65.08,30),(73,43),(73,57),(116.4,57)],'SW_B':[(115.08,30),(125,42),(145,42),(145,90)]}
count={}
for net,pts in paths.items():
 g=LineString(pts).buffer(6,join_style=2,cap_style=2)
 z=p.ZONE(b);z.SetNet(N[net]);z.SetLayer(p.F_Cu);z.SetLocalClearance(MM(.4));z.SetMinThickness(MM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetAssignedPriority(4);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.Outline().NewOutline()
 for x,y in list(g.exterior.coords)[:-1]:z.Outline().Append(MM(x),MM(y))
 b.Add(z);count[net]=0
 # 0.9/0.45 mm through vias; array only in common front/back power-zone interiors.
 xmin,ymin,xmax,ymax=g.bounds
 for ix in range(math.ceil(xmin/2.5),math.floor(xmax/2.5)+1):
  for iy in range(math.ceil(ymin/2.5),math.floor(ymax/2.5)+1):
   c=(ix*2.5,iy*2.5);pt=Point(*c)
   if not g.buffer(-.8).contains(pt):continue
   if any(pt.distance(ob)<.7 for n,ob in objects if n!='/'+net):continue
   if any(pt.distance(ob)<.6 for ob in paste):continue
   if any(pt.distance(ob)<.7 for n,ob in objects if n=='/'+net):continue
   v=p.PCB_VIA(b);v.SetPosition(V(*c));v.SetWidth(MM(.9));v.SetDrill(MM(.45));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(N[net]);b.Add(v);objects.append(('/'+net,pt.buffer(.45)));count[net]+=1
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(ROOT/'poc_lev.kicad_pcb'),b)
print('Added power stitching',count)
(ROOT/'reports/power_stitching.json').write_text(json.dumps(count,indent=2)+'\n')
