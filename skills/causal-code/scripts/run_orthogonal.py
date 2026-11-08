"""Standalone joint-basis PLR / binary ATE AIPW. Config is JSON data, never code."""
import os
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ.setdefault(key,'1')
from pathlib import Path
import argparse,hashlib,json,sys,importlib.metadata
import numpy as np,pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import PolynomialFeatures,StandardScaler
from sklearn.linear_model import Ridge,LogisticRegression
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier,HistGradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import KFold,StratifiedKFold,GroupKFold,StratifiedGroupKFold

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def basis(frame,terms,treatments):
 out=[];names=[]
 for term in terms:
  name=term['name'];powers=term['powers'];value=np.ones(len(frame))
  if name in names or not powers:raise ValueError('Basis names must be unique and powers nonempty')
  for col,power in powers.items():
   if col not in treatments or isinstance(power,bool) or not isinstance(power,int) or power<1:raise ValueError('Basis powers must be positive integers of declared treatments')
   value*=frame[col].to_numpy(float)**power
  out.append(value);names.append(name)
 A=np.column_stack(out)
 if not np.isfinite(A).all():raise ValueError('Nonfinite basis; do not impute exposures')
 return A,names

def learner(kind,seed):
 if kind=='ridge':return make_pipeline(SimpleImputer(add_indicator=True),PolynomialFeatures(2,include_bias=False),StandardScaler(),Ridge(alpha=1.))
 if kind=='rf':return make_pipeline(SimpleImputer(add_indicator=True),RandomForestRegressor(n_estimators=120,min_samples_leaf=8,max_features=1.,n_jobs=1,random_state=seed))
 if kind=='hgb':return make_pipeline(SimpleImputer(add_indicator=True),MultiOutputRegressor(HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=15,l2_regularization=1.,random_state=seed)))
 raise ValueError('Unknown learner')

def splits(n,folds,seed,groups=None,binary=None):
 if not 2<=folds<=n:raise ValueError('Invalid fold count')
 dummy=np.zeros((n,1))
 if groups is not None:
  if len(np.unique(groups))<folds:raise ValueError('Fewer dependence groups than folds')
  sp=GroupKFold(folds,shuffle=True,random_state=seed) if binary is None else StratifiedGroupKFold(folds,shuffle=True,random_state=seed)
  pairs=list(sp.split(dummy,binary,groups))
 else:
  sp=KFold(folds,shuffle=True,random_state=seed) if binary is None else StratifiedKFold(folds,shuffle=True,random_state=seed)
  pairs=list(sp.split(dummy,binary))
 seen=np.zeros(n,int)
 for tr,te in pairs:
  if len(set(tr)&set(te)):raise AssertionError('Observation leakage')
  if groups is not None and set(groups[tr])&set(groups[te]):raise AssertionError('Group leakage')
  if binary is not None and len(np.unique(binary[tr]))!=2:raise ValueError('Training fold lacks a treatment arm')
  seen[te]+=1
 if not np.all(seen==1):raise AssertionError('Each row needs exactly one out-of-fold prediction')
 return pairs

def covariance(A,residual,groups=None,kind='score-hc0'):
 n,p=A.shape
 if np.linalg.matrix_rank(A)!=p:raise ValueError('Residual basis is rank deficient')
 bread=np.linalg.inv(A.T@A);score=A*residual[:,None]
 if groups is not None:
  labels,ix=np.unique(groups,return_inverse=True);G=len(labels)
  if G<2:raise ValueError('At least two clusters required')
  S=np.zeros((G,p));np.add.at(S,ix,score)
  cov=bread@S.T@S@bread*G/(G-1)*(n-1)/(n-p)
  return cov,G-1,'orthogonal-score cluster CR1; t(G-1) sensitivity',G
 if kind=='score-hc0':return bread@score.T@score@bread,np.inf,'orthogonal-score HC0; asymptotic normal',None
 if kind=='secondstage-hc3':
  h=np.einsum('ij,jk,ik->i',A,bread,A)
  if np.any(h>=1-1e-10):raise ValueError('HC3 undefined at unit leverage')
  S=score/(1-h)[:,None]
  return bread@S.T@S@bread,n-p,'final-stage residual HC3 sensitivity; t(n-p)',None
 raise ValueError('Unknown covariance')

def fit(config,frame):
 method=config['method'];Y=config['outcome'];controls=config['controls'];treatments=config['treatments'];n=len(frame)
 if len(set(controls))!=len(controls) or set(controls)&(set(treatments)|{Y}):raise ValueError('Treatment/outcome cannot also be adjustment columns')
 if not controls:raise ValueError('Specify adjustment columns; an unadjusted estimator needs an explicit separate design')
 if len(set(treatments))!=len(treatments) or Y in treatments:raise ValueError('Invalid treatment roles')
 for col in [Y]+treatments+controls:
  if col not in frame:raise ValueError('Missing column: '+col)
  if not pd.api.types.is_numeric_dtype(frame[col]):raise ValueError('This runner requires numeric columns: '+col)
 if frame[[Y]+treatments].isna().any().any() or not np.isfinite(frame[[Y]+treatments].to_numpy(float)).all():raise ValueError('Outcome and treatment must be observed and finite; no silent sample deletion')
 if np.isinf(frame[controls].to_numpy(float)).any():raise ValueError('Infinite adjustment value')
 if config.get('id_col') and frame[config['id_col']].duplicated().any():raise ValueError('Duplicate declared observational unit')
 cluster=config.get('cluster_col');groups=None
 if cluster:
  if frame[cluster].isna().any():raise ValueError('Missing dependence group')
  groups=frame[cluster].astype(str).to_numpy()
  if cluster in controls:raise ValueError('Dependence IDs must be encoded/justified separately from adjustment columns')
 C=frame[controls].to_numpy(float);y=frame[Y].to_numpy(float);seed=int(config.get('seed',42));k=int(config.get('folds',5));binary=None
 if method=='aipw':
  if len(treatments)!=1:raise ValueError('AIPW runner supports one binary exposure')
  binary=frame[treatments[0]].to_numpy(float)
  if set(np.unique(binary))!={0.,1.}:raise ValueError('AIPW needs treatment encoded 0/1')
 elif method!='plr':raise ValueError('Use method plr or aipw')
 folds=splits(n,k,seed,groups,binary);fold_id=np.empty(n,int);diag=[];base=learner(config.get('learner','ridge'),seed)
 if method=='plr':
  terms=config.get('basis',[{'name':t,'powers':{t:1}} for t in treatments]);D,names=basis(frame,terms,treatments)
  py=np.full(n,np.nan);pm=np.full_like(D,np.nan)
  for f,(tr,te) in enumerate(folds):
   fold_id[te]=f
   lm=clone(base);lm.fit(C[tr],y[tr,None]);py[te]=np.asarray(lm.predict(C[te])).reshape(-1)
   mm=clone(base);mm.fit(C[tr],D[tr]);pm[te]=np.asarray(mm.predict(C[te])).reshape(len(te),len(names))
   diag.append(dict(fold=f,train=len(tr),test=len(te),group_leakage=False))
  ry=y-py;rd=D-pm
  if n<=rd.shape[1] or np.linalg.matrix_rank(rd)!=rd.shape[1]:raise ValueError('Insufficient residual identification')
  beta=np.linalg.lstsq(rd,ry,rcond=None)[0];res=ry-rd@beta
  cov,df,inference,G=covariance(rd,res,groups,config.get('covariance','score-hc0'))
  se=np.sqrt(np.diag(cov));p=2*stats.norm.sf(abs(beta/se)) if np.isinf(df) else 2*stats.t.sf(abs(beta/se),df)
  crit=stats.norm.ppf(.975) if np.isinf(df) else stats.t.ppf(.975,df)
  center=rd-rd.mean(0);gram=center.T@center
  vif=np.diag(gram)*np.diag(np.linalg.inv(gram)) if np.linalg.matrix_rank(center)==len(names) else np.full(len(names),np.nan)
  rows=[dict(term=t,beta=float(b),SE=float(s),p=float(pp),CI_low=float(b-crit*s),CI_high=float(b+crit*s),residual_VIF=float(v) if np.isfinite(v) else None) for t,b,s,pp,v in zip(names,beta,se,p,vif)]
  pred=pd.DataFrame({'fold':fold_id,'y':y,'y_oof':py})
  for j,t in enumerate(names):pred[t+'__raw']=D[:,j];pred[t+'__oof']=pm[:,j];pred[t+'__residual']=rd[:,j]
  details=dict(outcome_OOF_RMSE=float(np.sqrt(np.mean(ry**2))),basis_OOF_RMSE=np.sqrt(np.mean(rd**2,axis=0)).tolist(),residual_condition_number=float(np.linalg.cond(rd)),covariance=cov.tolist())
 else:
  d=binary;mu=np.full((n,2),np.nan);prop=np.full(n,np.nan)
  classifier=make_pipeline(SimpleImputer(add_indicator=True),StandardScaler(),LogisticRegression(max_iter=1000))
  for f,(tr,te) in enumerate(folds):
   fold_id[te]=f;cl=clone(classifier);cl.fit(C[tr],d[tr]);prop[te]=cl.predict_proba(C[te])[:,1]
   for arm in [0,1]:
    ta=tr[d[tr]==arm];lm=clone(base);lm.fit(C[ta],y[ta,None]);mu[te,arm]=np.asarray(lm.predict(C[te])).reshape(-1)
   diag.append(dict(fold=f,train=len(tr),test=len(te),group_leakage=False))
  eps=float(config.get('propensity_clip',.01))
  if not 0<eps<.5:raise ValueError('propensity_clip must be in (0,.5)')
  pe=np.clip(prop,eps,1-eps);pseudo=mu[:,1]-mu[:,0]+d*(y-mu[:,1])/pe-(1-d)*(y-mu[:,0])/(1-pe)
  beta=np.array([pseudo.mean()]);cov,df,inference,G=covariance(np.ones((n,1)),pseudo-beta[0],groups)
  se=float(np.sqrt(cov[0,0]));p=float(2*stats.norm.sf(abs(beta[0]/se))) if np.isinf(df) else float(2*stats.t.sf(abs(beta[0]/se),df));crit=stats.norm.ppf(.975) if np.isinf(df) else stats.t.ppf(.975,df)
  rows=[dict(term='ATE',beta=float(beta[0]),SE=se,p=p,CI_low=float(beta[0]-crit*se),CI_high=float(beta[0]+crit*se))]
  pred=pd.DataFrame(dict(fold=fold_id,y=y,d=d,propensity_oof=prop,propensity_used=pe,mu0_oof=mu[:,0],mu1_oof=mu[:,1],pseudo_outcome=pseudo))
  details=dict(propensity_min=float(prop.min()),propensity_max=float(prop.max()),clipped_count=int(np.sum(prop!=pe)),clipping_threshold=eps,clipping_limit='Clipping can bias the target; inspect positivity and support before interpreting ATE.')
 return dict(method=method,N=n,estimates=rows,inference=inference,clusters=G,folds=diag,diagnostics=details,causal_assumptions_verified=False),pred

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
 cfgpath=Path(args.config).resolve();config=json.loads(cfgpath.read_text(encoding='utf-8'));data=Path(config['data']);data=data if data.is_absolute() else cfgpath.parent/data
 out=Path(args.out)
 if out.exists() and any(out.iterdir()):raise FileExistsError('Use a new empty run directory')
 out.mkdir(parents=True,exist_ok=True)
 freeze=dict(config=config,input_sha256=digest(data),config_sha256=digest(cfgpath),script_sha256=digest(__file__),python=sys.version,versions={x:importlib.metadata.version(x) for x in ['numpy','pandas','scipy','scikit-learn']})
 dump(out/'manifest.json',freeze);dump(out/'STATUS.json',{'status':'running'})
 try:
  frame=pd.read_csv(data);result,pred=fit(config,frame);pred.to_csv(out/'out_of_fold.csv',index=False);dump(out/'result.json',result);pd.DataFrame(result['estimates']).to_csv(out/'estimates.csv',index=False)
  dump(out/'STATUS.json',{'status':'complete','N':len(frame)});print(json.dumps({'status':'complete','N':len(frame),'estimates':result['estimates']},ensure_ascii=False))
 except Exception as exc:dump(out/'STATUS.json',{'status':'failed','error':str(exc)});raise

if __name__=='__main__':main()
