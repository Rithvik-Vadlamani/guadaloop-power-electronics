"""Read-only native design comparison; write a scoped audit report."""
from pathlib import Path
import hashlib, json, csv, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'MV_Board_RevF1'; BASE=ROOT/'MV_Board_RevF'
sys.path.insert(0,str(ROOT/'Verification_Independent'))
import native as n
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((OUT/'Verification/baseline-sha256.json').read_text())
changed=[f for f,h in baseline.items() if not (BASE/f).exists() or sha(BASE/f)!=h]
a=n.sx.loads((BASE/'KiCad/MV24_RevF.kicad_pcb').read_text())
b=n.sx.loads((OUT/'KiCad/MV24_RevF1.kicad_pcb').read_text())
fa,fb=n.footprint_map(a),n.footprint_map(b)
placement=[r for r in fa if r not in fb or n.child(fa[r],'at')!=n.child(fb[r],'at')]
def edges(board):
    return [v for v in board if n.tag(v).startswith('gr_') and n.child(v,'layer')==[n.sx.Symbol('layer'),'Edge.Cuts']]
def bom(p):
    return {ref:{k:row[k] for k in ['mpn','value','footprint']} for row in csv.DictReader(p.open()) for ref in row['refs'].split(',')}
ba,bb=bom(BASE/'Procurement/BOM.csv'),bom(OUT/'Procurement/BOM.csv')
diff={r:{'before':ba.get(r),'after':bb.get(r)} for r in ba.keys()|bb.keys() if ba.get(r)!=bb.get(r)}
edits=json.loads((OUT/'Verification/revision-edits.json').read_text())
vias={(round(v[1],4),round(v[2],4)):t for t in n.children(b,'via') for v in [n.child(t,'at')]}
netnames={v[1]:v[2] for v in n.children(b,'net')}
via_errors=[]
for e in edits['added_thermal_vias']:
    xy=(round(e['x_mm'],4),round(e['y_mm'],4));v=vias.get(xy)
    if v is None or netnames.get(n.child(v,'net')[1],n.child(v,'net')[1])!=e['net'] or n.child(v,'drill')[1]!=.3 or n.child(v,'size')[1]!=.7 or str(n.child(v,'free')[1])!='yes':
        via_errors.append(e)
mosfet_errors=[]
for r in ['Q1','Q2']:
    if fa[r][1]!=fb[r][1] or n.props(fa[r])!=n.props(fb[r]) or n.children(fa[r],'pad')!=n.children(fb[r],'pad'):
        mosfet_errors.append(r)
fresh_errors=[]
for name in ['board-checks','schematic-checks']:
    report=json.loads((OUT/f'Verification/final-native/{name}.json').read_text())
    assert report['status']=='pass'
    fresh_errors += [p for p,h in report['input_hashes'].items() if sha(Path(p))!=h]
result=dict(baseline_files_checked=len(baseline),baseline_changes=changed,footprint_count=len(fb),
    moved_footprints=placement,added_footprints=sorted(fb.keys()-fa.keys()),removed_footprints=sorted(fa.keys()-fb.keys()),
    outline_identical=edges(a)==edges(b),mosfet_changes=mosfet_errors,fitted_parts_before=len(ba),fitted_parts_after=len(bb),
    fitted_part_changes=diff,added_via_count=len(n.children(b,'via'))-len(n.children(a,'via')),
    expected_thermal_vias=len(edits['added_thermal_vias']),thermal_via_errors=via_errors,stale_native_inputs=fresh_errors,
    board_sha256=sha(OUT/'KiCad/MV24_RevF1.kicad_pcb'),schematic_sha256=sha(OUT/'KiCad/MV24_RevF1.kicad_sch'))
assert not (changed or placement or mosfet_errors or via_errors or fresh_errors)
assert edges(a)==edges(b) and fa.keys()==fb.keys() and len(ba)==len(bb)==51
assert set(diff)=={'L1','R6','R10'} and result['added_via_count']==37
result['status']='pass'
(OUT/'Verification/final-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
