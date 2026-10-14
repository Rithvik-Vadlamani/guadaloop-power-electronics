"""Record the actual completed image review and archive the board-only handoff."""
from pathlib import Path
import json,hashlib,subprocess,zipfile
OUT=Path(__file__).resolve().parents[1];V=OUT/'Verification/manufacturing-review'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
native=json.loads((OUT/'KiCad/reports/board-checks.json').read_text())
checks=json.loads((V/'checks.json').read_text())
assert native['status']=='pass' and checks['status']=='machine_comparison_pass'
assert checks['board_sha256']==sha(OUT/'KiCad/MV24_RevF1.kicad_pcb')
files=[p for folder in ['Manufacturing','Assembly'] for p in (OUT/folder).rglob('*') if p.is_file()]
files+=[p for p in V.iterdir() if p.suffix in ['.png','.svg']]
review=dict(reviewer='Codex',date='2026-09-20',status='reviewed_for_prototype_vendor_DFM',
    input_hashes=native['input_hashes'],artifact_hashes={str(p.relative_to(OUT)):sha(p) for p in files},
    inspected=['all-layers.png: four copper layers, both masks, both silkscreens, closed outline, plated/non-plated drilling',
        'top-copper-detail.png, bottom-copper-detail.png, top-mask-detail.png: power-stage geometry and pad openings',
        'assembly-drawing.png and assembly-reference-map.png: full-board reference coverage, capacitor polarity markings, component orientation and DNP crosses',
        'filled-vias-map.png with filled-vias.csv: required selected-via process locations',
        'F-paste.png and F-paste-populated.png: MOSFET/controller windowed apertures and removal of DNP stencil openings'],
    findings=['No missing fabrication layers or missing holes found; empty bottom silk and bottom paste intentional.',
        'All 265 drill/slot features match native dimensions/centers to 0.00051mm; outline is the intended 150x110mm rectangle.',
        '51 fitted parts exactly reconcile between purchasing BOM, assembly BOM, placement export and native board.',
        'Eight hidden native Fab-layer references were added to a separate assembly drawing only; no PCB or schematic changes.',
        'Filled/capped-via requirements explicitly identify 38 conservative selected locations, including inherited vias; no vias added this turn.',
        'Four DNP paste flashes removed; remaining 116 top paste objects reparse and render identically to source minus DNP.',
        'Inherited tight silkscreen reference spacing remains; separate assembly map is authoritative for placement.',
        'Vendor DFM, filled/capped process confirmation, stencil thickness/aperture process and assembler rotation preview remain unassessed by vendor.',
        'No physical assembly, battery interface, continuous20A performance, thermal or EMC qualification is implied.'])
(V/'inspection.json').write_text(json.dumps(review,indent=2)+'\n')
subprocess.run(['python3',str(OUT/'scripts/record_review.py')],check=True)
handoff=OUT/'Handoff';handoff.mkdir(exist_ok=True)
selected=[]
for p in OUT.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(OUT)
    if rel.parts[0]=='Handoff' or '.history' in rel.parts or p.name=='.DS_Store' or p.suffix in ['.lck','.prl','.npy']:continue
    if rel.parts[:2]==('Assembly','stencil') or p.name=='native-unfiltered-bom.csv':continue
    selected.append(p)
manifest={str(p.relative_to(OUT)):sha(p) for p in sorted(selected)}
archive=handoff/'MV24_RevF1-board-prototype.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in selected:z.write(p,'MV_Board_RevF1/'+str(p.relative_to(OUT)))
    z.writestr('MV_Board_RevF1/Handoff-file-hashes.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for path,h in manifest.items():assert hashlib.sha256(z.read('MV_Board_RevF1/'+path)).hexdigest()==h,path
(handoff/'archive-check.json').write_text(json.dumps(dict(path=archive.name,sha256=sha(archive),files=len(manifest),crc_check='pass',per_file_hash_check='pass',scope='Board-only prototype; vendor DFM and bench testing pending; no order placed'),indent=2)+'\n')
print('Verified archive:',archive,'files:',len(manifest),'bytes:',archive.stat().st_size)
