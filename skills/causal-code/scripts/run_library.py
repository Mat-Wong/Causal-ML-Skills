"""Standalone, explicit-role adapters to pinned official EconML / DoubleML APIs."""
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ.setdefault(key,'1')
from pathlib import Path
import argparse,json,hashlib,importlib.metadata,sys
import numpy as np,pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold,StratifiedKFold

def dump(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def fit(c,f):
 backend=c['backend'];model=c['model'];cols=c['controls'];T=c['treatment'];Y=c['outcome'];Z=c.get('instrument');seed=int(c.get('seed',42));folds=int(c.get('folds',3));n=len(f)
 if c.get('cluster_col'):raise ValueError('This library adapter exposes iid inference only; use native PLR/AIPW for supported one-way score covariance or implement library-compatible cluster inference explicitly')
 if len(set(cols))!=len(cols) or set(cols)&{T,Y,Z}:raise ValueError('Adjustment roles overlap target, outcome or instrument')
 required=cols+[T,Y]+([Z] if Z else [])
 if not all(pd.api.types.is_numeric_dtype(f[k]) for k in required):raise ValueError('Provide numeric columns or adapt a training-fold categorical pipeline')
 if not np.isfinite(f[required].to_numpy(float)).all():raise ValueError('This adapter requires complete numeric inputs; adapt fold-local imputation for missing covariates')
 if c.get('id_col') and f[c['id_col']].duplicated().any():raise ValueError('Duplicate declared unit')
 reg=lambda:make_pipeline(SimpleImputer(),RandomForestRegressor(n_estimators=64,max_depth=6,min_samples_leaf=8,n_jobs=1,random_state=seed))
 clf=lambda:make_pipeline(SimpleImputer(),RandomForestClassifier(n_estimators=64,max_depth=6,min_samples_leaf=8,n_jobs=1,random_state=seed))
 y=f[Y].to_numpy(float);t=f[T].to_numpy(float);binary=set(np.unique(t))=={0.,1.};instrument=f[Z].to_numpy(float) if Z else None
 if backend=='doubleml':
  import doubleml as dml
  if model not in ['plr','irm','pliv','iivm']:raise ValueError('Supported DoubleML models: plr, irm, pliv, iivm')
  if model in ['irm','iivm'] and not binary:raise ValueError('This IRM/IIVM adapter needs binary 0/1 treatment')
  if model in ['pliv','iivm'] and Z is None:raise ValueError('IV model requires instrument and a defensible IV design')
  if model=='iivm' and set(np.unique(instrument))!={0.,1.}:raise ValueError('IIVM needs a binary 0/1 instrument')
  data=dml.DoubleMLData(f,y_col=Y,d_cols=T,x_cols=cols,z_cols=Z)
  np.random.seed(seed)
  if model=='plr':est=dml.DoubleMLPLR(data,ml_l=reg(),ml_m=reg(),n_folds=folds)
  elif model=='irm':est=dml.DoubleMLIRM(data,ml_g=reg(),ml_m=clf(),n_folds=folds)
  elif model=='pliv':est=dml.DoubleMLPLIV(data,ml_l=reg(),ml_m=reg(),ml_r=reg(),n_folds=folds)
  else:est=dml.DoubleMLIIVM(data,ml_g=reg(),ml_m=clf(),ml_r=clf(),n_folds=folds)
  est.fit();smry=est.summary.reset_index().rename(columns={'index':'term'});ci=np.asarray(est.confint())
  rows=[dict(term=str(smry.iloc[j]['term']),beta=float(est.coef[j]),SE=float(est.se[j]),p=float(est.pval[j]),CI_low=float(ci[j,0]),CI_high=float(ci[j,1])) for j in range(len(est.coef))]
  fold_id=np.empty(n,int)
  for k,(_,te) in enumerate(est.smpls[0]):fold_id[te]=k
  return dict(N=n,backend=backend,model=model,estimates=rows,inference='official DoubleML iid orthogonal-score asymptotic inference',causal_assumptions_verified=False),pd.DataFrame({'fold':fold_id})
 if backend!='econml':raise ValueError('backend must be doubleml or econml')
 mods=c.get('effect_modifiers',[])
 if not set(mods).issubset(cols):raise ValueError('Effect modifiers must be declared adjustment columns in this adapter')
 X=f[mods].to_numpy(float) if mods else None;others=[v for v in cols if v not in mods];W=f[others].to_numpy(float) if others else None
 sf=StratifiedKFold(folds,shuffle=True,random_state=seed) if binary else KFold(folds,shuffle=True,random_state=seed);cv=list(sf.split(f,t if binary else None));meta=model in ['slearner','tlearner','xlearner']
 if model in ['slearner','tlearner','xlearner','linear-dr'] and not binary:raise ValueError('Discrete learner adapter needs binary 0/1 treatment')
 if meta:
  from econml.metalearners import SLearner,TLearner,XLearner
  est=SLearner(overall_model=reg()) if model=='slearner' else TLearner(models=reg()) if model=='tlearner' else XLearner(models=reg(),propensity_model=clf())
  X=f[cols].to_numpy(float);est.fit(y,t,X=X);uncertainty=False
 elif model=='linear-dml':
  from econml.dml import LinearDML
  est=LinearDML(model_y=reg(),model_t=clf() if binary else reg(),discrete_treatment=binary,cv=cv,random_state=seed);est.fit(y,t,X=X,W=W);uncertainty=True
 elif model=='linear-dr':
  from econml.dr import LinearDRLearner
  est=LinearDRLearner(model_propensity=clf(),model_regression=reg(),cv=cv,random_state=seed);est.fit(y,t,X=X,W=W);uncertainty=True
 elif model=='causal-forest':
  from econml.dml import CausalForestDML
  if X is None:raise ValueError('Causal forest requires explicit pre-treatment effect modifiers')
  est=CausalForestDML(model_y=reg(),model_t=clf() if binary else reg(),discrete_treatment=binary,n_estimators=64,min_samples_leaf=10,cv=cv,random_state=seed,n_jobs=1);est.fit(y,t,X=X,W=W);uncertainty=True
 elif model in ['orthoiv','dmliv']:
  if Z is None:raise ValueError('IV learner needs an instrument and identifying assumptions')
  if binary:raise ValueError('This IV adapter uses continuous treatment; choose IIVM for binary IV compliance')
  from econml.iv.dml import OrthoIV,DMLIV
  est=OrthoIV(model_y_xw=reg(),model_t_xw=reg(),model_z_xw=reg(),cv=cv,random_state=seed) if model=='orthoiv' else DMLIV(model_y_xw=reg(),model_t_xw=reg(),model_t_xwz=reg(),model_final=LinearRegression(fit_intercept=False),cv=cv,random_state=seed)
  est.fit(y,t,Z=instrument,X=X,W=W);uncertainty=model=='orthoiv'
 else:raise ValueError('Unsupported model; see documented implemented adapters')
 t0=float(c.get('contrast_t0',0));t1=float(c.get('contrast_t1',1));eff=np.asarray(est.effect(X,T0=t0,T1=t1)).reshape(-1);pred=pd.DataFrame({'effect':eff})
 if uncertainty:
  lo,hi=est.effect_interval(X,T0=t0,T1=t1,alpha=.05);pred['CI_low']=np.asarray(lo).reshape(-1);pred['CI_high']=np.asarray(hi).reshape(-1)
 return dict(N=n,backend=backend,model=model,contrast=[t0,t1],effect_prediction_rows=len(eff),mean_predicted_effect=float(eff.mean()),inference='official estimator pointwise iid intervals; no mean-effect p-value supplied' if uncertainty else 'point estimates only; no supported interval configuration in this adapter',causal_assumptions_verified=False),pred

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--out',required=True);a=p.parse_args();cp=Path(a.config).resolve();c=json.loads(cp.read_text(encoding='utf-8'));src=Path(c['data']);src=src if src.is_absolute() else cp.parent/src;out=Path(a.out)
 if out.exists() and any(out.iterdir()):raise FileExistsError('Use a new empty output directory')
 out.mkdir(parents=True,exist_ok=True);dump(out/'manifest.json',dict(config=c,input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),python=sys.version,versions={x:importlib.metadata.version(x) for x in ['econml','doubleml','scikit-learn','numpy']}));dump(out/'STATUS.json',{'status':'running'})
 try:
  result,pred=fit(c,pd.read_csv(src));dump(out/'result.json',result);pred.to_csv(out/'predictions.csv',index=False);dump(out/'STATUS.json',{'status':'complete'});print(json.dumps(result,ensure_ascii=False))
 except Exception as exc:dump(out/'STATUS.json',{'status':'failed','error':str(exc)});raise
if __name__=='__main__':main()
