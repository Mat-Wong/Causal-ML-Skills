"""Synchronize portable skill references, validate structure, and build a text-only ZIP."""
from pathlib import Path
import hashlib,json,re,zipfile
import yaml
R=Path(__file__).resolve().parents[1]
M={'causal-theory':['identification'],'causal-method-router':['methods','identification'],'cml-estimators':['methods'],'dml-estimation':['dml','methods'],'causal-code':['code-contract'],'causal-run':['runbook','identification'],'causal-heterogeneity':['heterogeneity'],'causal-audit':['audit'],'causal-report':['reporting']}
def prepare():
 for name,refs in M.items():
  skill=R/'skills'/name;entry=skill/'SKILL.md';s=entry.read_text(encoding='utf-8')
  s=re.sub(r'`../../shared/[^`]+\.md`','`references/'+refs[0]+'.md`',s,count=1)
  s=s.replace('`../../shared/sources.json`','`references/sources.json`');entry.write_text(s,encoding='utf-8')
  dst=skill/'references';dst.mkdir(exist_ok=True)
  for f in [r+'.md' for r in refs]+['sources.json']:(dst/f).write_bytes((R/'shared'/f).read_bytes())
 checks=[]
 for name in M:
  skill=R/'skills'/name;s=(skill/'SKILL.md').read_text(encoding='utf-8');front=yaml.safe_load(s.split('---',2)[1]);assert front['name']==name and front['description']
  ui=yaml.safe_load((skill/'agents/openai.yaml').read_text(encoding='utf-8'));assert 25<=len(ui['interface']['short_description'])<=64
  assert '$'+name in ui['interface']['default_prompt']
  for p in skill.rglob('*.md'):
   t=p.read_text(encoding='utf-8');assert not any(c in t for c in ['\x08','\x0c','\x0b','\t']),str(p)
  checks.append(name)
 readme=(R/'README.md').read_text(encoding='utf-8');assert not any(c in readme for c in ['\t','\x08','\x0c','\x0b'])
 files=[p for d in ['skills','shared'] for p in (R/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc']]+[R/'README.md',R/'LICENSE',R/'requirements-tested.txt']
 assert len(files)<=100
 for p in files:
  p.read_text(encoding='utf-8')
  if p.suffix=='.py':assert p.stat().st_size<20*1024
 dist=R/'dist';dist.mkdir(exist_ok=True);path=dist/'causal-ml-skills-v0.1.0.zip'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(path) as z:assert z.testzip() is None and len([n for n in z.namelist() if n.endswith('/SKILL.md')])==9
 info=dict(status='pass',skills=checks,pack_files=len(files),zip_bytes=path.stat().st_size,zip_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),portable_references=True,scripts_standalone=True)
 (R/'DISTRIBUTION_QA.json').write_text(json.dumps(info,indent=2),encoding='utf-8');print(json.dumps(info))
if __name__=='__main__':prepare()
