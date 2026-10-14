"""Conditional engineering calculations. No result here is a hardware measurement."""
from pathlib import Path
import json,math,csv
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parent.parent
C_NOM=3*470e-6

def shutdown(v0,i0,l,r,c,vf=1.0,step=1e-5):
    # Coil remains connected; all gates off; isolated DC link accepts diode current.
    # TVS disabled in this model. Coil R and two constant diode drops dissipate energy.
    def deriv(t,y):
        i,v,er,ed=y
        return [-(v+r*i+2*vf)/l,i/c,r*i*i,2*vf*i]
    def stop(t,y):return y[0]
    stop.terminal=True;stop.direction=-1
    sol=solve_ivp(deriv,[0,.1],[i0,v0,0,0],events=stop,rtol=1e-10,atol=1e-11,max_step=step)
    assert len(sol.t_events[0])==1
    i,v,er,ed=sol.y[:,-1]
    ec=.5*c*(v*v-v0*v0);ei=.5*l*i0*i0
    assert abs(ec+er+ed-ei)<1e-7
    return dict(peak_bus_V=float(v),decay_ms=float(sol.t[-1]*1000),coil_heat_J=float(er),diode_heat_J=float(ed),added_cap_energy_J=float(ec),energy_residual_J=float(ec+er+ed-ei))
# Cross-check the integrator against the independent lossless energy identity.
check=shutdown(60,30,.010,0,C_NOM,0)
assert abs(check['peak_bus_V']-math.sqrt(60**2+.010*30**2/C_NOM))<1e-6
refined=shutdown(60,30,.010,2,C_NOM,step=5e-6)
assert abs(refined['peak_bus_V']-shutdown(60,30,.010,2,C_NOM)['peak_bus_V'])<1e-6
transients=[]
for v in [60,70]:
 for l in [.00925,.010]:
  for scale in [1,.8]:
   for i in [10,16,30]:
    c=C_NOM*scale
    transients.append(dict(initial_bus_V=v,initial_current_magnitude_A=i,coil_L_H=l,coil_R_ohm_assumed=2,bulk_C_F=c,ideal_lossless_peak_V=math.sqrt(v*v+l*i*i/c),**shutdown(v,i,l,2,c)))
thermals=[]
for f in [16000,32000]:
 for i in [10,16,30]:
  pc=i*i*.00672*.75;ps=3.2*(i/30)*(f/16000);p=pc+ps
  thermals.append(dict(current_A=i,frequency_Hz=f,assumed_duty=.75,conduction_W=pc,switching_W=ps,total_per_hard_switching_FET_W=p,assumed_ambient_C=40,proposed_junction_target_C=125,assumed_case_sink_C_per_W=.5,required_sink_ambient_max_C_per_W=(125-40)/p-.34-.5))
ripple=[dict(current_A=i,effective_active_duty=d,conditional_bank_ripple_A_rms=i*math.sqrt(d*(1-d)),ideal_equal_share_each_A_rms=i*math.sqrt(d*(1-d))/3) for i in [10,16,30] for d in [.5,.75]]
limits=[dict(initial_bus_V=v,bulk_C_F=C_NOM*scale,coil_L_H=.010,voltage_ceiling_V=ceiling,lossless_current_for_ceiling_A=math.sqrt(C_NOM*scale*(ceiling**2-v**2)/.010)) for v in [60,70] for scale in [1,.8] for ceiling in [80,90,100]]
result=dict(status='ANALYSIS_ONLY_NOT_HARDWARE_QUALIFIED',hardware_measurements_performed=0,models=dict(shutdown='Coil connected, all gates off, bus supply cannot absorb regeneration, no TVS action, R=2 ohm assumed, 1 V per conducting body diode assumed, constant L/C; excludes wiring inductance/ESR/ESL and temperature dependence.',thermal='Extrapolates source-brief switching loss, not a transistor switching simulation. Rds=6.72 milliohm from brief; hot-value scaling is not a guaranteed datasheet maximum.',ripple='Constant load current, active/freewheel unipolar PWM, source supplies only DC average, capacitor bank carries all AC bus ripple, equal sharing assumed.'),solver_checks='PASS: lossless energy identity, dissipative energy conservation, step refinement',shutdown_sweep=transients,thermal_budget=thermals,conditional_ripple=ripple,lossless_energy_thresholds=limits)
(ROOT/'qualification/analysis.json').write_text(json.dumps(result,indent=2)+'\n')
for name,rows in [('shutdown_sweep',transients),('thermal_budget',thermals),('conditional_ripple',ripple),('lossless_energy_thresholds',limits)]:
 with (ROOT/'qualification'/str(name+'.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps([x for x in transients if x['initial_bus_V']==60 and x['coil_L_H']==.010 and x['initial_current_magnitude_A']==30],indent=2))
print(json.dumps(thermals,indent=2))
