"""Record the scoped image review performed by Codex; not a hardware approval."""
from pathlib import Path
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[OUT/'Documentation/Board.png',OUT/'Documentation/Schematic.png']
files+=sorted((OUT/'Verification/review').glob('MV24_RevF1-*.png'))
native=json.loads((OUT/'Verification/final-native/board-checks.json').read_text())
review=dict(reviewer='Codex',date='2026-09-20',
    scope='Rendered schematic, 3D assembly preview, four copper layers, solder masks, silkscreens; native unchanged-outline comparison. Not a Gerber/drill or physical-board review.',
    input_hashes=native['input_hashes'],artifact_hashes={str(p.relative_to(OUT)):sha(p) for p in files},
    findings=[
        'Replacement values visible and main power/feedback topology readable.',
        'Component placement preserved; widened VIN bottom heat path and separate bottom SW island visible.',
        'Top solder-mask openings over the new in-pad vias require filled/capped manufacture; process specified in fabrication notes.',
        'Inherited compact silkscreen crowding around C8/R1 remains; some prototype text is obscured by the large inductor in the assembled view. Not corrected to avoid unrelated native changes.',
        'Outline-only raster offers little contrast at image edges; outline preservation is established by native geometry comparison, not this image alone.',
        'All four copper layers inspected; this does not establish current capacity, thermal performance or EMC.'
    ],status='reviewed_with_documented_limitations')
(OUT/'Verification/visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
cmd=['python3','/Users/rithvik/.codex/skills/kicad-design/scripts/kicad_design.py','--project',str(OUT/'Verification/evidence'),'verify-evidence',str(OUT/'Verification/evidence/packet.json')]
r=subprocess.run(cmd,capture_output=True,text=True)
(OUT/'Verification/evidence/verification-result.txt').write_text(r.stdout+r.stderr)
assert r.returncode==0,r.stdout+r.stderr
handoff_path=OUT/'Verification/manufacturing-review/inspection.json'
handoff=json.loads(handoff_path.read_text()) if handoff_path.exists() else None
if handoff:
    assert all(sha(Path(p))==h for p,h in handoff['input_hashes'].items()),'Handoff native inputs stale'
    assert all(sha(OUT/p)==h for p,h in handoff['artifact_hashes'].items()),'Handoff artifacts stale'
status=dict(design='MV24 Rev F1',status='board_prototype_handoff_prepared_pending_vendor_DFM' if handoff else 'prototype_candidate_not_released',
    native_erc='pass',native_drc='pass',independent_connectivity='pass',unchanged_layout_and_mosfets='pass',
    averaged_loop_screen='completed_under_declared_assumptions',thermal_screen='completed_not_qualified',
    visual_review='reviewed_with_documented_limitations',hardware_test='not_performed',
    manufacturing_export_review='reviewed_for_board_prototype_with_documented_limits' if handoff else 'not_performed',continuous_20A_rating='unassessed',
    precharge='deferred_by_user',battery_interface_fusing='pending_with_deferred_input_work',
    decision_record='Documentation/Engineering-notes.md',test_plan='Documentation/Fabrication-and-test.md',
    source_hashes={str(p.relative_to(OUT)):sha(p) for p in [OUT/'KiCad/MV24_RevF1.kicad_pcb',OUT/'KiCad/MV24_RevF1.kicad_sch',OUT/'Procurement/BOM.csv']})
(OUT/'Release-status.json').write_text(json.dumps(status,indent=2)+'\n')
manifest={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='Manifest.sha256' and p.suffix not in ['.lck','.prl'] and '.history' not in p.parts and 'Handoff' not in p.parts and p.name!='.DS_Store'}
(OUT/'Manifest.sha256').write_text(''.join(f'{h}  {p}\n' for p,h in sorted(manifest.items())))
print(r.stdout)
print('Recorded scoped review and prototype status; manifest files:',len(manifest))
