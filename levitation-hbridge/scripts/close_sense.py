from pathlib import Path
src=Path('scripts/route_board.py').read_text().split('# Dedicated gate copper')[0]
src=src.replace('for t in list(b.GetTracks()):b.RemoveNative(t)','for t in []:pass').replace('for z in list(b.Zones()):b.RemoveNative(z)','for z in []:pass').replace("    if g.geom_type=='MultiPolygon':","    return\n    if g.geom_type=='MultiPolygon':").replace('for xx in [110.5,112,113.5,115]:','for xx in []:')
exec(compile(src,'routing-engine','exec'))
seen=set()
for t in list(b.GetTracks()):
    if isinstance(t,p.PCB_VIA):
        key=(t.GetNetname(),xy(t.GetPosition()))
        if key in seen:b.RemoveNative(t);continue
        seen.add(key)
    n=t.GetNetname().lstrip('/')
    if isinstance(t,p.PCB_VIA):g=Point(*xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2);ls=[0,1];typ='via'
    else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2);ls=[0 if t.GetLayer()==p.F_Cu else 1];typ='track'
    geo.append((n,ls,g,typ,''))
n='SNS_N_F'
def feed(a):
    candidates=[]
    for ix in range(-40,41):
        for iy in range(-40,41):
            c=(round(a[0]+ix*.1,4),round(a[1]+iy*.1,4));point=Point(*c);line=LineString([a,c])
            if math.dist(a,c)<.5:continue
            good=True
            for other,ls,g,typ,key in geo:
                if typ=='power_zone':continue
                if typ=='pad' and point.distance(g)<.42:good=False;break
                if other!=n and (point.distance(g)<.52 or (0 in ls and line.distance(g)<.33)):good=False;break
            if good:candidates.append((math.dist(a,c),c))
    if not candidates:return None
    _,c=min(candidates);addtrack(n,0,a,c,.25);addvia(n,c,.6,.3);return c
start=xy(P['C20.2'].GetPosition());end=xy(P['U3.1'].GetPosition());a=feed(start);c=feed(end);print('feeds',a,c,flush=True)
if a and c:
    # Permit routing in the bus region: fill supplies clearance around the sense trace.
    geo[:]=[g for g in geo if g[3]!='power_zone']
    route(n,a,c,.25,False,[1],[1])
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(ROOT/'poc_lev.kicad_pcb'),b)
