from pathlib import Path
src=Path('scripts/route_board.py').read_text().split('# Dedicated gate copper')[0]
src=src.replace('for t in list(b.GetTracks()):b.RemoveNative(t)','for t in []:pass').replace('for z in list(b.Zones()):b.RemoveNative(z)','for z in []:pass')
src=src.replace('    if g.geom_type==\'MultiPolygon\':',"    return\n    if g.geom_type=='MultiPolygon':")
src=src.replace('for xx in [110.5,112,113.5,115]:','for xx in []:')
exec(compile(src,'routing-engine','exec'))
for t in b.GetTracks():
    n=t.GetNetname().lstrip('/')
    if isinstance(t,p.PCB_VIA):g=Point(*xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2);ls=[0,1];typ='via'
    else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2);ls=[0 if t.GetLayer()==p.F_Cu else 1];typ='track'
    geo.append((n,ls,g,typ,''))
for n in ['SNS_P_F','SNS_N_F']:routepins(n,NETS[n],.25,True)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(ROOT/'poc_lev.kicad_pcb'),b)
print('Filtered sense routes saved')
