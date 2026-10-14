from sexpr import *
from pathlib import Path
base=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
for lib,names in {'Driver_FET':['IR2184'],'Amplifier_Current':['INA240A2D'],'74xGxx':['74LVC2G17'],'Device':['Q_NMOS_GDS','R_Shunt','C_Polarized'],'Transistor_FET':['IRF100B201']}.items():
    s=parse((base/(lib+'.kicad_sym')).read_text())
    for n in names:
        sy=next((x for x in children(s,'symbol') if x[1]==n),None)
        print(lib,n,'NOT FOUND' if sy is None else [(p[1],one(p,'number')[1],one(p,'name')[1],one(p,'at')[1:]) for p in walk(sy,'pin')], 'extends',one(sy,'extends') if sy else '')
