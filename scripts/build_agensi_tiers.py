"""Build three explicit, nested product tiers from the same verified source tree."""
from pathlib import Path
import hashlib, json, zipfile
from prepare_distribution import prepare

R = Path(__file__).resolve().parents[1]
TIERS = {
    'starter': dict(price=0, title='Causal ML Starter: Method Selector',
                    skills=['causal-method-router']),
    'essentials': dict(price=2.99, title='Causal ML Essentials: 6 Skills',
                       skills=['causal-theory','causal-method-router','cml-estimators',
                               'dml-estimation','causal-code','causal-run']),
    'complete': dict(price=3.99, title='Causal ML Complete: 9 Skills',
                    skills=sorted(p.name for p in (R/'skills').iterdir() if p.is_dir())),
}

def build():
    prepare()
    out = R/'dist'; out.mkdir(exist_ok=True)
    manifest = {}
    for tier, info in TIERS.items():
        members = {}
        for name in info['skills']:
            for p in (R/'skills'/name).rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
                    members[p.relative_to(R).as_posix()] = p.read_bytes()
        for name in ['LICENSE','requirements-tested.txt']:
            members[name] = (R/name).read_bytes()
        if tier != 'starter':
            members['VALIDATION.json'] = (R/'VALIDATION.json').read_bytes()
        body = '# '+info['title']+'\n\n'
        body += 'Causal machine learning research skills for SKILL.md-compatible agents.\n\n'
        body += '## Included modules\n\n'+''.join('- `'+s+'`\n' for s in info['skills'])
        body += '\n## Use\n\nLoad the selected SKILL.md and its local references. '
        body += 'For execution, use the included standalone Python scripts and install the pinned dependencies.\n'
        if tier == 'starter':
            body += '\nThis tier provides method selection and identification references; executable estimation scripts are in Essentials and Complete.\n'
        if tier == 'essentials':
            body += '\nFor heterogeneity, dedicated auditing and reporting modules, choose Complete.\n'
        body += '\n## Source and licence\n\nOriginal community synthesis grounded in Microsoft EconML and DoubleML documentation. '
        body += 'MIT source: https://github.com/Mat-Wong/Causal-ML-Skills . '
        body += 'Agensi provides a packaged distribution of the public source. '
        body += 'Method handoffs in individual skills are optional; only the modules listed above are bundled.\n'
        members['README.md'] = body.encode('utf-8')
        assert len(members) <= 100
        path = out/('causal-ml-'+tier+'-v0.1.0.zip')
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(members.items()):
                data.decode('utf-8')
                z.writestr(name,data)
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            assert len([n for n in z.namelist() if n.endswith('/SKILL.md')]) == len(info['skills'])
            for name, data in members.items():
                assert z.read(name) == data
        manifest[tier] = dict(info, files=len(members), bytes=path.stat().st_size,
                              zip=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    assert set(TIERS['starter']['skills']) < set(TIERS['essentials']['skills']) < set(TIERS['complete']['skills'])
    (R/'AGENSI_TIERS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__ == '__main__': build()
