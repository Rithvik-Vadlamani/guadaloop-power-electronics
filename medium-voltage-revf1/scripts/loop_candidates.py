"""Reuse Rev F's averaged CCM equations with independent R10/R11 corners.

This is not a switched-controller, startup, DCM, constant-power-load or fault
simulation. It selects a prototype compensation candidate, not a guarantee.
"""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'MV_Board_RevF1/Verification'
source=ROOT/'MV_Board_RevF/Verification/loop_screen.py'
original=source.read_text().split('result=dict(')[0]
program=original.replace('[6.4e-6,12e-6]', '[9.6e-6,18e-6]')
program=program.replace("d['frequency']['wider_10pct_min_Hz']", '89630').replace("d['frequency']['wider_10pct_max_Hz']", '110456')
program=program.replace('for L,C,esr,load,a,b,c,r,f,gain,gbw', 'for L,C,esr,load,a,b,c,r,r11,f,gain,gbw')
program=program.replace('[.98,1.02],', '[.9775,1.0225],[.9775,1.0225],')
program=program.replace('2200*r+', '2200*r11+').replace('R10_R11_scale=r,', 'R10_scale=r,R11_scale=r11,')
rows=[]
for r10 in [7500,7870,8060,8200,8250,8450,8660]:
    scope={'__file__':str(source)}
    exec(compile(program.replace('6810*r',f'{r10}*r'),str(source),'exec'),scope)
    result=dict(R10_ohm=r10,C26_F=3.3e-9,crossings=len(scope['rows']),missing_crossings=len(scope['missing']),
                minimum=min(scope['rows'],key=lambda x:x['phase_margin_deg']),
                maximum_crossover=max(scope['rows'],key=lambda x:x['crossover_Hz']))
    rows.append(result)
    print(r10, result['minimum']['phase_margin_deg'],result['missing_crossings'],flush=True)
(OUT/'loop-candidates.json').write_text(json.dumps(dict(scope=__doc__,equation_source=str(source.relative_to(ROOT)),
    equation_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    assumptions=['L=9.6..18uH includes explicit 20% initial and additional 20% multiplicative DC-bias allowance; not guaranteed',
    'Cout=1128..1692uF and ESR=.00367..02933ohm inherited scenarios',
    'Independent R10/R11 +/-2.25% includes 1% initial and 125K x100ppm/K allowance',
    '100k RT 0.1% +25ppm/K x125K and assumed oscillator +/-10%',
    'Gain and bandwidth are typical/sensitivity values; no nonlinear or supply-dynamic validation'],rows=rows),indent=2)+'\n')
