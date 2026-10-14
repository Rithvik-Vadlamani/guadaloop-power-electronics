"""Normative pin/net manifest; changes from source brief are explicitly documented."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
PARTS={}; NETS={}
def part(ref,value,lib,fp,mpn='',rating='',note=''):
    PARTS[ref]=dict(ref=ref,value=value,lib=lib,footprint=fp,mpn=mpn,rating=rating,note=note)
def net(name,pins):
    assert name not in NETS
    NETS[name]=pins.split()
R8='Resistor_SMD:R_0805_2012Metric'; C8='Capacitor_SMD:C_0805_2012Metric'
SO='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
for i in range(1,5):part('Q'+str(i),'IRF100B201','Transistor_FET:Q_NMOS_GDS','Package_TO_SOT_THT:TO-220-3_Vertical','IRF100B201','100V','Individual insulated clip-on heatsink; 30A thermal design unqualified')
for i in range(1,25):
    v='1u';rating='100V X7R';fp='Capacitor_SMD:C_1210_3225Metric';lib='Device:C';mpn=''
    if i in [5,10]:v='100n';fp=C8
    if i in [11,12,13]:v='470u';rating='100V';fp='Capacitor_THT:CP_Radial_D16.0mm_P7.50mm';lib='Device:C_Polarized';mpn='100ZLH470MEFC16X31.5'
    if 14<=i<=19:v='100n' if i in [15,18] else '1u';rating='50V' if i in [15,18] else '25V';fp=C8
    if i==20:v='1n';rating='50V C0G';fp=C8
    if i in [21,23]:v='100n';rating='25V X7R';fp=C8
    if i==22:v='10u';rating='10V X7R';fp=C8
    if i==24:v='220u';rating='25V';fp='poc_lev:CP_Radial_D8.0mm_P3.50mm_Positive2';lib='poc_lev:C_Polarized_Positive2'
    part('C'+str(i),v,lib,fp,mpn,rating,'C24 positive pad 2 preserves source netlist' if i==24 else '')
rs={1:'0.5m',2:'10',3:'10k',4:'10',5:'1',6:'10k',7:'10k',8:'1',9:'10',10:'10k',11:'10',12:'10',13:'10',14:'22k',19:'3.3k',20:'4.7',21:'4.7',22:'4.7',23:'4.7',24:'10k',25:'10k'}
for i,v in rs.items():
    fp=R8;lib='Device:R';mpn='';rating='0.125W'
    if i in [2,4,9,11]:fp='Resistor_SMD:R_1206_3216Metric';rating='0.25W; pulse capability to verify'
    if i==14:fp='Resistor_SMD:R_2512_6332Metric';rating='1W'
    if i==1:fp='poc_lev:CSS2H_2512_Kelvin';lib='Device:R_Shunt';mpn='CSS2H-2512R-L500FE';rating='6W 1%'
    part('R'+str(i),v,lib,fp,mpn,rating,'Two-terminal component with manufacturer-recommended Kelvin PCB pickup; user accepted' if i==1 else '')
for i in range(1,9):
    v='ES1D' if i in [1,3] else 'SS34' if i==2 else '5.0SMDJ70A' if i==8 else '1N4148W'
    fp='D_SMA' if i<=3 else 'D_SMC' if i==8 else 'D_SOD-123'
    part('D'+str(i),v,'Device:D_Schottky' if i==2 else 'Device:D_Zener' if i==8 else 'Device:D','Diode_SMD:'+fp,v)
for i in [1,2]:part('U'+str(i),'IR2184S','Driver_FET:IR2184',SO,'IR2184SPBF',note='SOIC-8 ordering code; pinout human review required by brief')
part('U3','INA240A2DR','poc_lev:INA240A2D',SO,'INA240A2DR')
part('U4','74LVC2G17','74xGxx:74LVC2G17','Package_TO_SOT_SMD:SOT-23-6','74LVC2G17GV','3.3V')
for i in [1,2]:part('J'+str(i),'38969-0002','Connector_Generic:Conn_01x02','poc_lev:CONN_SD-38969-001_02P_MOL','38969-0002','50A 600V')
part('J3','CONTROL','Connector_Generic:Conn_01x08','Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical')
for i in range(1,5):part('H'+str(i),'M3','Mechanical:MountingHole','MountingHole:MountingHole_3.2mm_M3')
for i,v in enumerate(['SW_A','SW_B','ISNS','+12V','GND','GND'],1):part('TP'+str(i),v,'Connector:TestPoint','TestPoint:TestPoint_Pad_D2.0mm');net('TP_TEMP'+str(i),'') if False else None
net('+60V','J2.1 Q1.2 Q3.2 '+' '.join('C%d.1'%i for i in range(1,14))+' D8.1 R14.1')
net('GND','J2.2 J3.3 J3.8 Q2.3 Q4.3 '+' '.join('C%d.2'%i for i in list(range(1,16))+[18,19,21,22,23])+' C24.1 R6.1 R10.1 R19.2 R24.2 R25.2 U1.3 U2.3 U3.2 U3.4 U3.7 U4.2 D8.2 R14.2 TP5.1 TP6.1')
net('+12V','D2.1 C14.1 C15.1 C18.1 C19.1 C24.2 R5.1 R8.2 U1.5 U2.5 TP4.1')
net('+12V_IN','J3.1 D2.2')
net('+3.3V','J3.2 C21.1 C22.1 C23.1 U3.3 U3.6 U4.5')
net('SW_A','Q1.3 Q2.2 R1.1 R3.1 U1.6 C16.2 TP1.1')
net('SW_B','Q3.3 Q4.2 R7.1 U2.6 C17.2 J1.1 TP2.1')
net('COIL_A','R1.4 J1.2')
net('SNS_P','R1.2 R12.1');net('SNS_N','R1.3 R13.1')
net('SNS_P_F','R12.2 C20.1 U3.8');net('SNS_N_F','R13.2 C20.2 U3.1')
net('ISNS','U3.5 J3.7 TP3.1')
net('G_Q1','Q1.1 R2.2 R3.2 D5.2');net('G_Q2','Q2.1 R4.2 R6.2 D4.2')
net('G_Q3','Q3.1 R9.1 R7.2 D7.2');net('G_Q4','Q4.1 R11.1 R10.2 D6.2')
net('HO_A','U1.7 R2.1 R20.2');net('LO_A','U1.4 R4.1 R21.2')
net('HO_B','U2.7 R9.2 R22.2');net('LO_B','U2.4 R11.2 R23.2')
net('VB_A','U1.8 C16.1 D1.1');net('VB_B','U2.8 C17.1 D3.1')
net('BOOT_A','D1.2 R5.2');net('BOOT_B','D3.2 R8.1')
for d,r in [(5,20),(4,21),(7,22),(6,23)]:net('OFF_Q'+str({5:1,4:2,7:3,6:4}[d]),'D%d.1 R%d.1'%(d,r))
net('SD','U1.2 U2.2 R19.1 J3.6')
net('PWM_A_IN','J3.4 R24.1 U4.1');net('PWM_A','U4.6 U1.1')
net('PWM_B_IN','J3.5 R25.1 U4.3');net('PWM_B','U4.4 U2.1')
PINS={}
for n,ps in NETS.items():
    for p in ps:
        assert p not in PINS,p
        PINS[p]=n
assert len([p for p in PARTS if not p.startswith(('TP','H'))])==64
if __name__=='__main__':
    (ROOT/'design_manifest.json').write_text(json.dumps(dict(parts=PARTS,nets=NETS),indent=2)+'\n')
