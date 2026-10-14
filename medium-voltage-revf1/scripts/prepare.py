"""Create an isolated Rev F1 workspace; never edit Rev F or Rev G."""
from pathlib import Path
import hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'MV_Board_RevF1'
BASE = ROOT / 'MV_Board_RevF'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['Verification', 'Verification/native', 'Verification/review', 'Documentation', 'Procurement', 'Sources']:
    (OUT/name).mkdir(parents=True, exist_ok=True)
assert not (OUT/'KiCad').exists(), 'Do not overwrite an existing candidate'
baseline = {str(p.relative_to(BASE)): digest(p) for p in BASE.rglob('*') if p.is_file() and '.history' not in p.parts and p.suffix not in ['.lck', '.prl'] and p.name != '.DS_Store'}
(OUT/'Verification/baseline-sha256.json').write_text(json.dumps(baseline, indent=2)+'\n')
shutil.copytree(BASE/'KiCad', OUT/'KiCad', ignore=shutil.ignore_patterns('.history', '*.lck', '*.prl', '.DS_Store'))
for suffix in ['kicad_sch','kicad_pcb','kicad_pro','kicad_dru']:
    (OUT/f'KiCad/MV24_RevF.{suffix}').rename(OUT/f'KiCad/MV24_RevF1.{suffix}')
for name in ['intent.json','independent-pin-intent.json']:
    shutil.copy2(BASE/'Verification'/name, OUT/'Verification'/name)
shutil.copy2(BASE/'Procurement/BOM.csv', OUT/'Procurement/BOM.csv')
for p in (BASE/'Verification/evidence/datasheets').glob('*.pdf'):
    shutil.copy2(p, OUT/'Sources'/p.name)
print('Created', OUT, 'from', BASE, 'with', len(baseline), 'baseline file hashes')
