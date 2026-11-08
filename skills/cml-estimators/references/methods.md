# Estimator map / 方法地图

## Routing table
| Setting and estimand | Candidate | Main restrictions | Inference decision |
|---|---|---|---|
| Continuous exposure, constant partial slope | PLR / LinearDML | Partial-linear response and sufficient residual variation | Orthogonal score covariance |
| Binary treatment, ATE/ATT | IRM / AIPW | Exchangeability and overlap | Cross-fitted influence function |
| Discrete treatment, flexible CATE | S/T/X learners | Response modeling and support | Arbitrary base learners do not automatically give valid intervals |
| Binary/multicategory CATE | DRLearner / LinearDRLearner | Outcome and propensity nuisance functions; rate conditions | Use estimator-specific inference |
| Structured CATE, continuous or discrete D | DML / R-learner | Residualization and effect model | Match final-stage inference |
| Unknown nonlinear heterogeneity | CausalForestDML / GRF | Honesty, support, sample size, nuisance quality | Estimator-specific forest intervals |
| Local nuisance estimation | DMLOrthoForest / DROrthoForest | Local overlap and smoothness | More expensive; verify local support |
| Continuous IV partial slope | PLIV / OrthoIV / DMLIV | Valid strong instrument and structural assumptions | IV score and first-stage diagnostics |
| Binary instrument and treatment | IIVM / DRIV family | Exogeneity, exclusion, monotonicity, compliance support | LATE or explicitly defined IV target |

## S, T and X learners
S fits one response model mu(x,d), with tau(x)=mu(x,1)-mu(x,0).
T fits mu_1(x) and mu_0(x) separately, then subtracts. It can struggle in small arms.
X first fits both response surfaces, then imputes effects:
\[
D^1=Y-\hat\mu_0(X),\quad D^0=\hat\mu_1(X)-Y,
\quad \hat\tau(x)=\hat e(x)\hat\tau_0(x)+(1-\hat e(x))\hat\tau_1(x).
\]
These are discrete-treatment learners. Do not silently median-split a continuous exposure.

## R learner and orthogonal DML
With m(C)=E[Y|C] and e(C)=E[D|C], the residual loss is
\[
\min_\tau \sum_i\{Y_i-\hat m(C_i)-(D_i-\hat e(C_i))\tau(X_i)\}^2.
\]
The outcome residual uses controls, not observed treatment. Cross-fitting is required.
R-learner is a framework; `_RLearner` is a private EconML base class, not a public CLI target.

## Doubly robust learning
For binary treatment, the AIPW/DR pseudo-outcome is
\[
\phi_i=\hat\mu_1(C_i)-\hat\mu_0(C_i)
+\frac{D_i(Y_i-\hat\mu_1(C_i))}{\hat e(C_i)}
-\frac{(1-D_i)(Y_i-\hat\mu_0(C_i))}{1-\hat e(C_i)}.
\]
ATE is its mean; regressing a cross-fitted pseudo-outcome on X targets CATE under conditions.
“Doubly robust” refers to nuisance robustness; it does not remove hidden confounding.
For inference with learned nuisances, the required error product/rates must still be checked.

## Forest schools
GRF solves a local moment equation sum_i alpha_i(x) psi_i(theta(x))=0.
CausalForestDML uses globally cross-fitted nuisances and an honest effect forest.
Orthogonal forests also estimate local nuisances. A predictive random forest of Y alone
does not become a causal forest. Feature importance describes the fitted model; it does
not identify a variable's causal contribution. State the fitted forest's treatment scale.

## IV schools
OrthoIV residualizes outcome, treatment and instrument. DMLIV uses a treatment prediction
with the instrument and another without it to construct the identifying variation.
DRIV adds an orthogonal IV pseudo-outcome/effect correction. Weak identification and
instrument validity remain substantive problems. DeepIV is an additional deep-learning
family with separate dependencies and architecture choices; it is not implemented by the
bundled runner, and requires an explicit design and environment before use.

Sources: official EconML meta-learner, DML, DR, forest and IV API pages;
DoubleML model guide. See `sources.json` for exact links and access dates.
