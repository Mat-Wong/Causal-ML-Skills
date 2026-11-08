# Evidence-based causal audit

## Identification
- Is the target ATE, ATT, LATE, CATE or a continuous dose contrast?
- Are consistency/interference assumptions plausible for the observational unit?
- Which measured common causes justify adjustment? Any mediator, collider or post-outcome control?
- For IV, document first-stage support, exclusion/exogeneity and monotonicity where needed.

## Measurement and sample
- Validate roles and timestamps against raw records and current data-release pointers.
- Do not let identifiers, row counts, outcome-derived variables or leakage proxies enter
  a learner by automatic all-numeric selection. Year/industry are substantive covariates
  only when the design explicitly includes them.
- Keep missing treatment/outcome visible. Covariate imputation belongs inside training folds.
- Report the sample flow; do not select exclusions from estimated effects or p-values.

## Estimation
- All out-of-fold predictions must come from training samples excluding the target unit/group.
- Tuning, scaling, encoding, imputation and feature selection must follow the same boundary.
- Check nuisance calibration/loss and propensity tails. Report clipping/trimming and how
  it changes assumptions/target population; it is not an automatic cure for absent overlap.
- Verify rank and smallest eigenvalues of the residual treatment-basis matrix.
- Confirm cluster definitions in both cross-fitting and covariance. Few clusters require
  extra care; a package's iid bootstrap does not supply cluster inference.

## Inference and sensitivity
- Match the interval to the target, estimator, dependence and installed version.
- Preserve a complete fixed specification/seed ledger. Discovery remains exploratory until
  confirmed independently; use simultaneous inference when reporting a searched family.
- Negative controls, placebo outcomes and sensitivity to hidden confounding can diagnose
  weaknesses but do not prove exchangeability. Reverse an encoding only with a clear mapping.
- DML is orthogonal to nuisance error locally under conditions; it is not immune to
  measurement error, weak identification or wrong structural response assumptions.

## Computational tests
Recover known effects on synthetic DGPs; test null and weak-signal cases too. Check grouped
fold disjointness, algebraic polynomial construction, numerical covariance and deterministic
reproducibility. A successful smoke test only supports the cases actually run.
