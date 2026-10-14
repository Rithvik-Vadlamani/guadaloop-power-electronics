"""Independently parse actual Gerbers/drills and reconcile fitted assembly data."""
from pathlib import Path
import json,csv,math,hashlib,collections,shutil,warnings
import gerbonara, pymupdf as fitz
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parents[1]; M=OUT/'Manufacturing'; A=OUT/'Assembly';V=OUT/'Verification/manufacturing-review'
V.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
native=json.loads((OUT/'Verification/handoff-native-inventory.json').read_text())
assert native['board_sha256']==sha(OUT/'KiCad/MV24_RevF1.kicad_pcb')
with warnings.catch_warnings(record=True) as warnings_seen:
    warnings.simplefilter('always');stack=gerbonara.LayerStack.open(M)
parser_warnings=[str(w.message) for w in warnings_seen]
def key(plated,diameter,points):return(plated,round(diameter,4),tuple(sorted(tuple(round(v,4) for v in p) for p in points)))
expected=collections.Counter(key(h['plated'],h['diameter'],h['points']) for h in native['holes'])
actual=collections.Counter()
for plated,layer in [(True,stack.drill_pth),(False,stack.drill_npth)]:
    for o in layer.objects:
        pts=[(o.x,o.y)]*2 if type(o).__name__=='Flash' else [(o.x1,o.y1),(o.x2,o.y2)]
        actual[key(plated,o.aperture.diameter,pts)]+=1
unmatched=list(actual.elements());max_drill_coordinate_error=0.
for e in expected.elements():
    candidates=[(max(abs(x-y) for p,q in zip(e[2],a[2]) for x,y in zip(p,q)),i) for i,a in enumerate(unmatched) if e[:2]==a[:2]]
    assert candidates,('missing drill',e)
    err,i=min(candidates);assert err<=0.00051,('drill position mismatch',e,unmatched[i],err)
    max_drill_coordinate_error=max(max_drill_coordinate_error,err);unmatched.pop(i)
assert not unmatched,unmatched
outline=stack.graphic_layers[('mechanical','outline')]
edges=[tuple(sorted([(o.x1,o.y1),(o.x2,o.y2)])) for o in outline.objects]
corners=[(20.,-20.),(170.,-20.),(170.,-130.),(20.,-130.)]
assert set(edges)=={tuple(sorted([corners[i],corners[(i+1)%4]])) for i in range(4)}
def png(svg,out,width=1700):
    out.with_suffix('.svg').write_text(str(svg));d=fitz.open(out.with_suffix('.svg'));page=d[0]
    page.get_pixmap(matrix=fitz.Matrix(width/page.rect.width,width/page.rect.width),alpha=False).save(out)
imgs=[]
for name,layer in stack.graphic_layers.items():
    label='-'.join(name);p=V/(label+'.png');png(layer.to_svg(force_bounds=((18,-132),(172,-18))),p)
    imgs.append((label,p))
for label,layer in [('drill-plated',stack.drill_pth),('drill-unplated',stack.drill_npth)]:
    p=V/(label+'.png');png(layer.to_svg(force_bounds=((18,-132),(172,-18))),p);imgs.append((label,p))
gallery=Image.new('RGB',(2400,4*650),'#dddddd');draw=ImageDraw.Draw(gallery)
for i,(label,p) in enumerate(imgs):
    im=Image.open(p);im.thumbnail((790,600));x=(i%3)*800;y=(i//3)*650
    gallery.paste(im,(x,y+32));draw.text((x+12,y+8),label,fill='black')
gallery.save(V/'all-layers.png')
for label in ['top-copper','bottom-copper','top-mask','top-silk']:
    # Tight local power-stage render from actual Gerber primitives.
    side,kind=label.split('-');png(stack.graphic_layers[(side,kind)].to_svg(force_bounds=((72,-89),(106,-57))),V/(label+'-detail.png'),1400)
raw=A/'native-unfiltered-bom.csv'
if not raw.exists():shutil.move(A/'bom.csv',raw)
source={ref:row for row in csv.DictReader((OUT/'Procurement/BOM.csv').open()) for ref in row['refs'].split(',')}
raw_bom={r['Reference']:r for r in csv.DictReader(raw.open())}
placements=list(csv.DictReader((A/'placements.csv').open()))
assert set(raw_bom)-set(source)=={f'TP{i}' for i in range(1,7)}
assert len(placements)==51 and {p['Ref'] for p in placements}==set(source)
partmap={p['ref']:p for p in native['parts']}
for r,row in source.items():
    b=raw_bom[r];assert b['MPN']==row['mpn'] and b['Value']==row['value'] and b['Footprint']==row['footprint'],r
for row in placements:
    p=partmap[row['Ref']]
    assert all(abs(float(row[k])-p['xy'][j])<1e-5 for j,k in enumerate(['PosX','PosY'])),row
    assert abs((float(row['Rot'])-p['rotation'])%360)<1e-5 and row['Side']==p['side'],row
with (A/'bom.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['Reference','Value','MPN','Footprint','Quantity']);w.writeheader()
    for ref in sorted(source):w.writerow(raw_bom[ref])
shutil.copy2(OUT/'Procurement/BOM.csv',A/'grouped-bom.csv')
report=dict(board_sha256=native['board_sha256'],gerber_layers=[list(n) for n in stack.graphic_layers],
    plated_holes=sum(actual[k] for k in actual if k[0]),unplated_holes=sum(actual[k] for k in actual if not k[0]),
    drill_geometry_matches_native=True,max_drill_coordinate_error_mm=max_drill_coordinate_error,drill_rounding_tolerance_mm=0.00051,outline_mm=[150,110],outline_closed=True,
    fitted_assembly_parts=51,assembly_native_geometry_match=True,excluded_bare_testpoints=sorted(set(raw_bom)-set(source)),
    fill_and_cap_selection_count=len(native['fill_vias']),parser_warnings=parser_warnings,
    parser_warning_interpretation='KiCad puts G90 after M95; parser warns but absolute metric coordinates reconcile with every native hole and slot. Plating assigned from explicit PTH/NPTH file separation.',
    visual_review='awaiting_actual_image_inspection',status='machine_comparison_pass',
    file_hashes={str(p.relative_to(OUT)):sha(p) for folder in [M,A] for p in folder.iterdir() if p.is_file()})
(V/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['file_hashes']},indent=2))
