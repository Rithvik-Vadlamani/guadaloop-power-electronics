"""Package the exact verified design; refuse stale verification hashes."""
from pathlib import Path
import zipfile,hashlib,json
root=Path(__file__).resolve().parent.parent
r=json.loads((root/'reports/verification.json').read_text())
assert r['DRC_violations']==r['unconnected_items']==0
for name,h in r['file_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,'Stale verification: '+name
base=['README.md','DESIGN_NOTES.md','BRING_UP.md','VERIFICATION.md','HARDWARE_QUALIFICATION.md','INTERFACE_REVIEW.md','BOM.csv','poc_lev.kicad_pro','poc_lev.kicad_sch','poc_lev.kicad_pcb','poc_lev.kicad_sym','poc_lev.kicad_dru','sym-lib-table','fp-lib-table','design_manifest.json','placement.json','symbol_uuids.json']
reports=['erc.rpt','final-drc.json','verification.json','schematic.net.xml','sense_pair.json','power_stitching.json','interface_placement.json','pcb-preview.png','schematic-preview.png','gate-detail.svg','gate-detail.png','schematic-svg/poc_lev.svg']
scripts=['design.py','sexpr.py','build_schematic.py','build_board.py','route_board.py','power_stitch.py','finish_board.py','verify_design.py','write_verification.py','view_gate.py','package.py','qualify_analysis.py','relocate_interface.py','check.sh','rebuild.sh','requirements.txt']
files=[root/x for x in base]+[root/'reports'/x for x in reports]+[root/'scripts'/x for x in scripts]+list((root/'lib.pretty').glob('*.kicad_mod'))+list((root/'sources').glob('*'))+list((root/'qualification').glob('*'))
assert all(p.is_file() and p.stat().st_size for p in files)
manifest=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root))+'\n' for p in sorted(files))
(root/'MANIFEST.sha256').write_text(manifest);files.append(root/'MANIFEST.sha256')
archive=root/'poc_lev_review_package.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files):z.write(p,'poc_lev/'+str(p.relative_to(root)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for p in files:assert z.read('poc_lev/'+str(p.relative_to(root)))==p.read_bytes()
print('Archive verified:',archive.name,len(files),'files',archive.stat().st_size,'bytes')
print('Native DRC:',r['DRC_violations'],'violations;',r['unconnected_items'],'unconnected')
