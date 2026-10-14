"""Record source locations already inspected visually; CLI binds acceptance."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1]/'Verification/evidence'
registry=json.loads((B/'project.json').read_text())
docs={d['id']:d for d in registry['documents']}
definitions=[
 ('r6-value','R6','RT0805BRD07100KL','0805','2026-09-20','Resistance','nominal',100.,'kohm','r6-f1','100 kOhms',{'source':'Exact part summary; nominal resistance; initial tolerance and TCR reviewed separately'}),
 ('r10-value','R10','RC0805FR-078K2L','0805','2026-09-20','Resistance','nominal',8.2,'kohm','r10-f1','8.2 kOhms',{'source':'Exact part summary; nominal resistance; initial tolerance and TCR reviewed separately'}),
 ('l1-value','L1','CPRX3231L-150MC','CPRX3231L','2023-10-10','Inductance','nominal',15.,'uH','l1-f1','CPRX3231L-150MC 15.0 1.35 1.60 64.0 42.0',{'measurement':'100 kHz, 0.1 V, 25 C ambient; nominal before DC bias; +/-20 percent initial tolerance'})]
facts=[];candidates=[];obligations=[]
for fid,ref,part,package,rev,param,bound,value,unit,doc,quote,conditions in definitions:
    candidate=dict(ref=ref,part=part,package=package,revision=rev)
    fact=dict(schema_version=1,id=fid,candidate=candidate,parameter=param,category='electrical',bound=bound,value=value,unit=unit,conditions=conditions,
        source=dict(document=doc,sha256=hashlib.sha256((B/docs[doc]['path']).read_bytes()).hexdigest(),page=1,quote=quote),state='needs_review')
    # Bound to the inspected Specifications value cells / CODACA 150MC row.
    fact['source'].update(table=2,row=1,column=4 if ref=='L1' else 1)
    facts.append(fact);candidates.append(candidate)
    obligations.append(dict(id=fid,ref=ref,parameter=param,category='electrical',bound=bound,unit=unit,conditions=conditions,query=f'{part} {param} {value} {unit}'))
(B/'parameters.json').write_text(json.dumps(facts,indent=2)+'\n')
(B/'request.json').write_text(json.dumps(dict(schema_version=1,design_id='MV24_REV_F1',topology='exported',candidates=candidates,obligations=obligations),indent=2)+'\n')
