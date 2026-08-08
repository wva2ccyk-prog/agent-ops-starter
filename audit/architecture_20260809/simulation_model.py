from __future__ import annotations
import csv, itertools, json, statistics
from pathlib import Path

OUT=Path(__file__).resolve().parent / 'generated'
OUT.mkdir(parents=True, exist_ok=True)
CURRENT={'agents':1273,'resolver':884,'principles':2707,'state':509,'memory':391,'handoff':950}
PROJECTS=[1,3,5,10,20]
DOCS=[5,10,20,30,50,100]

CANDIDATES=[
 {'id':'S0_CURRENT','always':1273,'normal_bootstrap':1273,'resolver':884,'checker_delta_loc':0,'concept_delta':0,'default_files':6,'risk':1.0,'note':'Current Starter.'},
 {'id':'S1_REPAIR_ONLY','always':1273,'normal_bootstrap':1273,'resolver':884,'checker_delta_loc':0,'concept_delta':0,'default_files':6,'risk':0.8,'note':'Documentation/checker wording repair only.'},
 {'id':'S2_OPTIONAL_SCOPED_ESCAPE','always':1273,'normal_bootstrap':1273,'resolver':884,'checker_delta_loc':35,'concept_delta':0,'default_files':6,'risk':0.7,'note':'Current default; optional sharding only after scale trigger.'},
 {'id':'S3_OPTIONAL_MULTI_PROJECT','always':1273,'normal_bootstrap':1273,'resolver':884,'checker_delta_loc':20,'concept_delta':0,'default_files':6,'risk':0.8,'note':'Example-only multi-project pattern.'},
 {'id':'S4_CHECKER_IMPROVEMENT','always':1273,'normal_bootstrap':1273,'resolver':884,'checker_delta_loc':25,'concept_delta':0,'default_files':6,'risk':0.5,'note':'Hard-fail active orphan docs and print exact candidates.'},
 {'id':'S5_PRODUCTION_DERIVED','always':1700,'normal_bootstrap':2700,'resolver':1800,'checker_delta_loc':180,'concept_delta':3,'default_files':10,'risk':0.5,'note':'Adds project registry, quick refs, and lane contracts.'},
 {'id':'S6_CLEAN_SHEET_2_FILE','always':1782,'normal_bootstrap':1782,'resolver':0,'checker_delta_loc':-120,'concept_delta':-1,'default_files':2,'risk':1.6,'note':'Merge router and state; loses conditional retrieval separation.'},
]

def single_resolver(projects:int, docs:int)->int:
    return 359 + projects*docs*105

def scoped_top(projects:int)->int:
    return 400 + projects*130

def scoped_local(docs:int)->int:
    return 250 + docs*105

rows=[]
for p,d in itertools.product(PROJECTS,DOCS):
    single=single_resolver(p,d)
    scoped=scoped_top(p)+scoped_local(d)
    rows.append({
      'projects':p,'active_docs_per_project':d,
      'single_resolver_bytes':single,
      'optional_scoped_route_bytes':scoped,
      'scoped_byte_delta':scoped-single,
      'scoped_savings_pct':round(100*(single-scoped)/single,1),
      'winner':'single' if single<=scoped else 'scoped',
      'note':'synthetic row-size model anchored to current 884-byte five-row resolver',
    })

with (OUT/'starter_scaling_sweep.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (OUT/'starter_tournament.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(CANDIDATES[0]));w.writeheader();w.writerows(CANDIDATES)

break_even=[]
for p in PROJECTS:
    winning=[r for r in rows if r['projects']==p and r['winner']=='scoped']
    break_even.append({'projects':p,'first_docs_per_project_where_scoped_wins':winning[0]['active_docs_per_project'] if winning else None})
summary={
 'current':CURRENT,
 'ordinary_task_bytes':1273,
 'resume_bytes':1782,
 'maintenance_bytes':3980,
 'route_lookup_bytes_before_target':2157,
 'recommended_candidate':'S4_CHECKER_IMPROVEMENT',
 'reason':'No read-path tax; aligns deterministic enforcement with the documented active-corpus contract.',
 'break_even':break_even,
 'classification':{'scoped_resolver':'OPTIONAL ESCAPE HATCH','multi_project_pattern':'EXAMPLE ONLY','production_governance':'REJECT'},
}
(OUT/'starter_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
