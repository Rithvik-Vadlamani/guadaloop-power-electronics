"""Native pcbnew board builder. No inner-layer signal routing."""
from design import *
from sexpr import *
import pcbnew as p,math,uuid,copy,wx
app=wx.App(False)
BASE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
MM=p.FromMM
V=lambda x,y:p.VECTOR2I(MM(x),MM(y))
def layers(ls):
    s=p.LSET()
    for l in ls:s.AddLayer(l)
    return s
b=p.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(MM(1.6))
uuids=json.loads((ROOT/'symbol_uuids.json').read_text())
# Custom polarity numbering; no reversed electrolytic on +12 V.
s=parse((BASE/'Capacitor_THT.pretty/CP_Radial_D8.0mm_P3.50mm.kicad_mod').read_text());s[1]='CP_Radial_D8.0mm_P3.50mm_Positive2'
for pad in children(s,'pad'):pad[1]='2' if pad[1]=='1' else '1'
(ROOT/'lib.pretty'/str(s[1]+'.kicad_mod')).write_text(dump(s))
# Bourns main lands: 1.80 x 3.40 mm, inner gap 3.40 mm.
# Copper sense terminals are intentionally tied at inner land edge, not separate component leads.
f=p.FOOTPRINT(b);f.SetFPID(p.LIB_ID('poc_lev','CSS2H_2512_Kelvin'));f.SetReference('REF**');f.SetValue('CSS2H-2512R-L500FE');f.SetAttributes(p.FP_SMD)
def fp_line(f,a,c,layer,width=.05):
    sh=p.PCB_SHAPE(f);sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(V(*a));sh.SetEnd(V(*c));sh.SetLayer(layer);sh.SetWidth(MM(width));f.Add(sh)
for num,x,y,w,h in [('1',-2.6,0,1.8,3.4),('4',2.6,0,1.8,3.4),('2',-1.35,0,.8,.4),('3',1.35,0,.8,.4)]:
    pad=p.PAD(f);pad.SetNumber(num);pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetShape(p.PAD_SHAPE_RECT);pad.SetPosition(V(x,y));pad.SetSize(V(w,h));pad.SetLayerSet(layers([p.F_Cu,p.F_Mask]+([p.F_Paste] if num in ['1','4'] else [])));f.Add(pad)
f.AddNetTiePadGroup('1,2');f.AddNetTiePadGroup('3,4')
for layer,box,w in [(p.F_CrtYd,(-3.8,-2,3.8,2),.05),(p.F_Fab,(-3.175,-1.525,3.175,1.525),.1)]:
    x1,y1,x2,y2=box
    for a,c in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:fp_line(f,a,c,layer,w)
f.Reference().SetPosition(V(0,-2.8));f.Reference().SetTextSize(V(.8,.8));f.Value().SetVisible(False)
f.SetLibDescription('Bourns CSS2H-2512 datasheet p2: 1.8x3.4 main lands, 3.4 gap; PCB Kelvin takeoff with net-tie groups. Two physical terminals.')
p.FootprintSave(str(ROOT/'lib.pretty'),f)
N={}
for i,n in enumerate(NETS,1):nt=p.NETINFO_ITEM(b,'/'+n,i);b.Add(nt);N[n]=nt
# Placement bands in mm. All four TO-220s 0 degrees / same tab direction.
# Board 150 x 100 mm; 25 mm FET pitch.
POS={'Q2':(35,30,0),'Q1':(60,30,0),'Q4':(85,30,0),'Q3':(110,30,0),
'J2':(34,80,180),'J1':(145,90,180),'C11':(45,94,0),'C12':(65,94,0),'C13':(85,94,0),
'U1':(50,28,0),'U2':(100,28,0),
'R1':(119,57,0),'U3':(116.5,72,90),'R12':(115,63,270),'R13':(118,63,270),'C20':(116.5,66.5,0),'C21':(111,73,90),
'U4':(64,63,0),'C23':(67.5,63,90),'J3':(45,65,0),'D2':(47,58,0),'C24':(35,56,0),'C22':(50,64,0),
'R24':(49,70,0),'R25':(49,74,0),'R19':(53,73,0),
'R3':(62,52,90),'R6':(38,49.5,90),'R7':(112,52,90),'R10':(85,52,90),
'D8':(25,42,90),'R14':(25,50,0),
'H1':(18,23,0),'H2':(152,23,0),'H3':(18,108,0),'H4':(152,108,0),
'TP1':(66,57,0),'TP2':(108,57,0),'TP3':(110,77,0),'TP4':(28,56,0),'TP5':(35,87,0),'TP6':(104,77,0)}
# User-approved bottom-edge control interface.
POS.update({'J3':(107,110,90),'U4':(115,101,0),'C23':(118.7,101,90),'C22':(110,102.5,90),'R24':(114.62,106,90),'R25':(117.16,106,90),'R19':(119.7,106,90),'D2':(127.8,100.5,180),'C24':(134.5,103,0),'TP4':(129,105.7,0),'TP5':(130,110,0)})
# User-approved revision: gate loops take precedence over the horizontal bands.
for off,base in [(0,1),(50,6)]:
    for j,(x,y) in enumerate([(38,24.05),(41.5,24.05),(61,24.05),(64.5,24.05),(44.33,27.5)]):POS['C'+str(base+j)]=(x+off,y,270 if j==4 else 90)
for off,refs in [(0,('R2','R4','D5','D4','R20','R21','C16','C14','C15','D1','R5')),(50,('R9','R11','D7','D6','R22','R23','C17','C19','C18','D3','R8'))]:
    rh,rl,dh,dl,oh,ol,cb,bulk,byp,db,rb=refs
    POS[rh]=(56.1+off,24,270 if off==0 else 90)
    POS[rl]=(46+off,34.55,180 if off==0 else 0)
    POS[dh]=(59.05+off,33.4,0)
    POS[dl]=(34.8+off,33.9,180)
    POS[oh]=(55.5+off,32.1,90)
    POS[ol]=(39.1+off,33.9,0)
    POS[cb]=(55.05+off,28.43,270)
    POS[bulk]=(51.9+off,32.15,180)
    POS[byp]=(48.2+off,32.2,180)
    POS[db]=(50.8+off,41,180)
    POS[rb]=(57.3+off,41,180 if off==0 else 0)
FP={}
for ref,c in PARTS.items():
    lib,name=c['footprint'].split(':');path=ROOT/'lib.pretty' if lib=='poc_lev' else BASE/(lib+'.pretty')
    f=p.FootprintLoad(str(path),name)
    assert f,ref
    f.SetFPID(p.LIB_ID(lib,name));f.SetReference(ref);f.SetValue(c['value']);b.Add(f)
    x,y,a=POS[ref];f.SetPosition(V(x,y));f.SetOrientationDegrees(a)
    f.SetPath(p.KIID_PATH('/'+str(uuid.uuid5(uuid.NAMESPACE_URL,'poc-lev/root'))+'/'+uuids[ref]))
    for pad in f.Pads():
        pin=ref+'.'+pad.GetNumber()
        if pin in PINS:pad.SetNet(N[PINS[pin]])
    f.Reference().SetTextSize(V(.8,.8));f.Reference().SetTextThickness(MM(.13));f.Value().SetVisible(False)
    # References below small parts, above FETs, connector reference in clear body area.
    f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));f.Reference().SetPosition(V(x,y+(2.1 if ref[0] in 'RCD' else 4)))
    if ref.startswith('Q'):f.Reference().SetPosition(V(x+2.54,23))
    if ref.startswith('H'):f.Reference().SetVisible(False)
    FP[ref]=f
# Edge first and explicitly dimensioned in deliverables.
for a,c in [((12,18),(158,18)),((158,18),(158,114)),((158,114),(12,114)),((12,114),(12,18))]:
    sh=p.PCB_SHAPE();sh.SetShape(p.SHAPE_T_SEGMENT);sh.SetStart(V(*a));sh.SetEnd(V(*c));sh.SetLayer(p.Edge_Cuts);sh.SetWidth(MM(.05));b.Add(sh)
def txt(s,x,y,size=1,layer=p.F_SilkS):
    t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(V(x,y));t.SetTextSize(V(size,size));t.SetTextThickness(MM(.15));t.SetLayer(layer);b.Add(t)
txt('POC LEV  /  REV A REVIEW',65,104,1.5);txt('60 V  |  16 kHz  |  2/1/1/2 oz',65,107,1)
txt('BENCH SUPPLY FIRST - NO HOT PLUG',65,110,1)
txt('BUS +',34,85,1.2);txt('BUS -',21,61,1.2)
txt('COIL B',145,95,1);txt('COIL A',132,72,1)
txt('SD: LOW = OFF',137,111,.8)
for i,label in enumerate(['12V','3V3','G','A','B','SD','IS','G']):txt(label,107+i*2.54,112.6,.8)
# Plane definitions; refill after routing. Inner layers have no tracks.
def zone(net,layer,points,priority=0):
    z=p.ZONE(b);z.SetLayer(layer);z.SetNet(N[net]);z.SetLocalClearance(MM(.4));z.SetMinThickness(MM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetAssignedPriority(priority);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    z.Outline().NewOutline()
    for x,y in points:z.Outline().Append(int(MM(x)),int(MM(y)))
    b.Add(z);return z
plane=[(12.6,18.6),(157.4,18.6),(157.4,113.4),(12.6,113.4)]
zone('GND',p.In1_Cu,plane);zone('+60V',p.In2_Cu,plane)
# Initial outer power corridors. Detailed pours finalized after gate/sense routing.
zone('GND',p.F_Cu,[(13,19),(157,19),(157,32),(13,32)])
zone('+60V',p.B_Cu,[(13,19),(157,19),(157,32),(13,32)])
# Switch-node wide conductors occupy the lower power strip on B.Cu. Pad stubs via arrays added by router.
zone('SW_A',p.B_Cu,[(36,32),(72,32),(72,54),(117,54),(117,61),(70,61),(58,49),(36,49)])
zone('SW_B',p.B_Cu,[(84,32),(115,32),(115,49),(143,49),(143,75),(132,75),(132,60),(111,60),(111,52),(84,52)])
zone('COIL_A',p.F_Cu,[(118,55),(128,55),(128,67),(118,67)])
# Ground and bus plating via array infrastructure created by routing script.
p.SaveBoard(str(ROOT/'poc_lev.kicad_pcb'),b)
# Stackup exact from brief: copper 0.07/0.035/0.035/0.07; dielectric 0.2/0.97/0.2 = 1.58 excluding masks.
s=(ROOT/'poc_lev.kicad_pcb').read_text();start=s.index('\n\t(setup')
stack='''\n\t\t(stackup
 (layer "F.SilkS" (type "Top Silk Screen"))
 (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.07))
 (layer "dielectric 1" (type "prepreg") (thickness 0.2) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In1.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 2" (type "core") (thickness 0.97) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In2.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 3" (type "prepreg") (thickness 0.2) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.07))
 (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
 (layer "B.SilkS" (type "Bottom Silk Screen"))
 (copper_finish "ENIG") (dielectric_constraints yes))'''
s=s[:start]+s[start:].replace('(setup','(setup'+stack,1);(ROOT/'poc_lev.kicad_pcb').write_text(s)
pro={"meta":{"filename":"poc_lev.kicad_pro","version":1},"board":{"design_settings":{"rules":{"min_clearance":0.2,"min_track_width":0.25,"min_via_diameter":0.6,"min_through_hole_diameter":0.3,"min_copper_edge_clearance":0.5},"rule_severities":{"courtyards_overlap":"error"}}},"net_settings":{"classes":[{"name":"Default","clearance":0.2,"track_width":0.25,"via_diameter":0.6,"via_drill":0.3,"diff_pair_width":0.25,"diff_pair_gap":0.25}],"meta":{"version":3}}}
(ROOT/'poc_lev.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
(ROOT/'placement.json').write_text(json.dumps(POS,indent=2)+'\n')
print('Placed',len(FP),'footprints')
