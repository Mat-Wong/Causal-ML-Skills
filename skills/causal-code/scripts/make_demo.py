"""Generate only synthetic data; no network or project-data access."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--n',type=int,default=1800);p.add_argument('--seed',type=int,default=71);a=p.parse_args();out=Path(a.out)
 if out.exists() and any(out.iterdir()):raise FileExistsError('Use a new demo directory')
 out.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(a.seed);n=a.n;X=rng.normal(size=(n,4));v=.4*X[:,0]+rng.normal(size=n);d=.5*X[:,1]+rng.normal(size=n)
 binary=rng.binomial(1,1/(1+np.exp(-.5*X[:,0]+.3*X[:,1])));zb=rng.binomial(1,.5,size=n);z=rng.normal(size=n);u=rng.normal(size=n)
 div=.8*z+.4*X[:,0]+u+rng.normal(size=n)*.3;db=(.9*zb+.3*X[:,0]+u+rng.normal(size=n)>.5).astype(int)
 frame=pd.DataFrame(X,columns=['x0','x1','x2','x3']);g=.5*X[:,0]-.3*X[:,1]+.2*X[:,2]**2
 frame['unit']=np.arange(n);frame['cluster']=np.arange(n)//6;frame['v']=v;frame['d']=d;frame['binary']=binary;frame['z']=z;frame['zb']=zb;frame['div']=div;frame['db']=db
 frame['y_joint']=.6*v-.5*d+.35*d*d+.25*v*d+g+rng.normal(size=n)*.5
 frame['y_ate']=1.5*binary+g+rng.normal(size=n)*.5
 frame['y_plr']=1.2*d+g+rng.normal(size=n)*.5
 frame['y_iv']=1.3*div+g+.7*u+rng.normal(size=n)*.5
 frame['y_iivm']=1.4*db+g+.7*u+rng.normal(size=n)*.5
 frame.to_csv(out/'synthetic.csv',index=False)
 common=dict(data='synthetic.csv',controls=['x0','x1','x2','x3'],id_col='unit',folds=3,seed=19,learner='ridge')
 configs={
 'joint':dict(common,method='plr',outcome='y_joint',treatments=['v','d'],basis=[dict(name=k,powers=ps) for k,ps in [('v',{'v':1}),('d',{'d':1}),('d_squared',{'d':2}),('v_x_d',{'v':1,'d':1})]]),
 'ate':dict(common,method='aipw',outcome='y_ate',treatments=['binary']),
 'library_plr':dict(common,backend='doubleml',model='plr',outcome='y_plr',treatment='d'),
 'library_irm':dict(common,backend='doubleml',model='irm',outcome='y_ate',treatment='binary'),
 'library_pliv':dict(common,backend='doubleml',model='pliv',outcome='y_iv',treatment='div',instrument='z'),
 'library_iivm':dict(common,backend='doubleml',model='iivm',outcome='y_iivm',treatment='db',instrument='zb')}
 for name,c in configs.items():(out/(name+'.json')).write_text(json.dumps(c,indent=2),encoding='utf-8')
 (out/'truth.json').write_text(json.dumps(dict(joint=[.6,-.5,.35,.25],ATE=1.5,PLR=1.2,PLIV=1.3,IIVM=1.4,seed=a.seed),indent=2),encoding='utf-8');print(out)
if __name__=='__main__':main()
