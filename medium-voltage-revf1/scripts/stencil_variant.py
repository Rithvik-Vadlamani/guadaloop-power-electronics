"""Derive a populated-only stencil from X2 component attributes; preserve raw export."""
from pathlib import Path
import gerbonara,json,hashlib,pymupdf as fitz
OUT=Path(__file__).resolve().parents[1];A=OUT/'Assembly';dest=A/'stencil-populated';dest.mkdir(exist_ok=True)
records=[]
for side in ['F','B']:
    src=A/f'stencil/MV24_RevF1-{side}_Paste.gbr';g=gerbonara.GerberFile.open(src)
    removed=[o for o in g.objects if o.attrs.get('.C',('',))[0] in {'R16','C27'}]
    g.objects=[o for o in g.objects if o not in removed]
    assert len(removed)==(4 if side=='F' else 0)
    def signature(o):return(type(o).__name__,tuple(round(v,6) for p in o.bounding_box() for v in p),o.polarity_dark)
    before=[signature(o) for o in g.objects];p=dest/src.name;g.save(p)
    again=gerbonara.GerberFile.open(p);assert before==[signature(o) for o in again.objects]
    def pixels(layer):
        svg=str(layer.to_svg(force_bounds=((18,-132),(172,-18)))).encode();doc=fitz.open(stream=svg,filetype='svg');page=doc[0];s=3000/page.rect.width
        return page.get_pixmap(matrix=fitz.Matrix(s,s),alpha=False).samples
    assert pixels(g)==pixels(again),'Stencil geometry raster differs after export'
    q=OUT/f'Verification/manufacturing-review/{side}-paste-populated.svg';q.write_text(str(again.to_svg(force_bounds=((72,-89),(106,-57)))))
    d=fitz.open(q);s=1400/d[0].rect.width;d[0].get_pixmap(matrix=fitz.Matrix(s,s),alpha=False).save(q.with_suffix('.png'))
    records.append(dict(side=side,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),removed_aperture_flashes=len(removed),remaining_objects=len(g.objects),remaining_geometry_unchanged=True,rendered_geometry_identical=True,note='Gerbonara re-export omits X2 component attributes. DNP filtering uses the retained raw source attributes; output geometry is independently read back and rendered pixel-identically. KiCad RoundRect macro unused parameters produce a parser warning without changing geometry.'))
(dest/'variant-checks.json').write_text(json.dumps(records,indent=2)+'\n');print(records)
