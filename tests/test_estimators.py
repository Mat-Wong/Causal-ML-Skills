from pathlib import Path
import importlib.util,json,subprocess,sys
import numpy as np,pandas as pd,pytest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
 p=ROOT/'skills/causal-code/scripts'/(name+'.py');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=load('run_orthogonal');library=load('run_library')

@pytest.fixture(scope='module')
def demo(tmp_path_factory):
 p=tmp_path_factory.mktemp('demo');p=p/'data'
 subprocess.run([sys.executable,str(ROOT/'skills/causal-code/scripts/make_demo.py'),'--out',str(p),'--n','1400'],check=True,capture_output=True)
 return p,pd.read_csv(p/'synthetic.csv')

def cfg(demo,name):return json.loads((demo[0]/(name+'.json')).read_text())

def test_joint_known_coefficients(demo):
 c=cfg(demo,'joint');r,o=native.fit(c,demo[1]);b=np.array([x['beta'] for x in r['estimates']]);assert np.max(abs(b-[.6,-.5,.35,.25]))<.12
 assert len(o)==1400 and len(set(o.fold))==3

def test_ate_known_effect(demo):
 r,o=native.fit(cfg(demo,'ate'),demo[1]);assert abs(r['estimates'][0]['beta']-1.5)<.12;assert r['diagnostics']['clipped_count']==0

def test_group_split_and_cluster_covariance(demo):
 c=cfg(demo,'joint');c['cluster_col']='cluster';r,o=native.fit(c,demo[1]);assert 'cluster CR1' in r['inference']
 assert pd.DataFrame({'g':demo[1].cluster,'fold':o.fold}).groupby('g').fold.nunique().max()==1

def test_binary_group_split(demo):
 c=cfg(demo,'ate');c['cluster_col']='cluster';r,o=native.fit(c,demo[1]);assert r['clusters']>100

def test_determinism(demo):
 c=cfg(demo,'joint');r,a=native.fit(c,demo[1]);s,b=native.fit(c,demo[1]);assert r==s;pd.testing.assert_frame_equal(a,b)

@pytest.mark.parametrize('bad',['role','unit','missing_t','missing_y','rank','constant','nonbinary','group'])
def test_fail_closed(demo,bad):
 c=cfg(demo,'ate' if bad=='nonbinary' else 'joint');f=demo[1].copy()
 if bad=='role':c['controls'].append('d')
 if bad=='unit':f.loc[1,'unit']=f.loc[0,'unit']
 if bad=='missing_t':f.loc[0,'d']=np.nan
 if bad=='missing_y':f.loc[0,c['outcome']]=np.nan
 if bad=='rank':c['basis'].append({'name':'duplicate_v','powers':{'v':1}})
 if bad=='constant':f['d']=0.
 if bad=='nonbinary':f.loc[0,'binary']=.5
 if bad=='group':c['cluster_col']='cluster';f['cluster']=0
 with pytest.raises(ValueError):native.fit(c,f)

def test_covariate_missing_allowed(demo):
 f=demo[1].copy();f.loc[::11,'x0']=np.nan;r,o=native.fit(cfg(demo,'joint'),f);assert r['N']==len(f)

@pytest.mark.parametrize('learner',['rf','hgb'])
def test_native_alternative_learners(demo,learner):
 c=cfg(demo,'joint');c['learner']=learner;r,p=native.fit(c,demo[1].iloc[:350].copy());assert np.isfinite([x['beta'] for x in r['estimates']]).all()

def test_hc3_numeric_independence():
 import statsmodels.api as sm
 rng=np.random.default_rng(9);A=rng.normal(size=(200,3));y=A@np.array([.2,-.1,.4])+rng.normal(size=200)*(1+abs(A[:,0]));b=np.linalg.lstsq(A,y,rcond=None)[0]
 c,df,label,_=native.covariance(A,y-A@b,kind='secondstage-hc3');ref=sm.OLS(y,A).fit().get_robustcov_results(cov_type='HC3').cov_params();assert np.allclose(c,ref,atol=1e-12)

@pytest.mark.parametrize('model',['plr','irm','pliv','iivm'])
def test_official_doubleml(demo,model):
 r,p=library.fit(cfg(demo,'library_'+model),demo[1]);assert r['N']==1400;assert np.isfinite([r['estimates'][0][k] for k in ['beta','SE','p']]).all()
 truth={'plr':1.2,'irm':1.5,'pliv':1.3,'iivm':1.4}[model];assert abs(r['estimates'][0]['beta']-truth)<.5

@pytest.mark.parametrize('model',['slearner','tlearner','xlearner','linear-dml','linear-dr','causal-forest','orthoiv','dmliv'])
def test_official_econml(demo,model):
 c=dict(cfg(demo,'library_plr'),backend='econml',model=model,effect_modifiers=['x0'])
 if model in ['slearner','tlearner','xlearner','linear-dr']:c.update(outcome='y_ate',treatment='binary')
 if model in ['orthoiv','dmliv']:c.update(outcome='y_iv',treatment='div',instrument='z')
 r,p=library.fit(c,demo[1].iloc[:700].copy());assert r['N']==700 and np.isfinite(p.effect).all()
 if 'CI_low' in p:assert np.all(p.CI_low<=p.CI_high)

def test_library_group_inference_restriction(demo):
 c=cfg(demo,'library_plr');c['cluster_col']='cluster'
 with pytest.raises(ValueError,match='iid inference'):library.fit(c,demo[1])

@pytest.mark.parametrize('runner,conf',[('run_orthogonal','joint'),('run_orthogonal','ate'),('run_library','library_plr')])
def test_standalone_cli(tmp_path,demo,runner,conf):
 # Copy script outside repository to emulate text-only temporary-file delivery.
 script=tmp_path/(runner+'.py');script.write_bytes((ROOT/'skills/causal-code/scripts'/(runner+'.py')).read_bytes());cp=cfg(demo,conf);cp['data']=str(demo[0]/'synthetic.csv');cfgpath=tmp_path/'config.json';cfgpath.write_text(json.dumps(cp));out=tmp_path/'results'
 r=subprocess.run([sys.executable,str(script),'--config',str(cfgpath),'--out',str(out)],capture_output=True,text=True)
 assert r.returncode==0,r.stderr;assert json.loads((out/'STATUS.json').read_text())['status']=='complete'
 again=subprocess.run([sys.executable,str(script),'--config',str(cfgpath),'--out',str(out)],capture_output=True,text=True);assert again.returncode!=0
