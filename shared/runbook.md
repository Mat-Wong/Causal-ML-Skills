# Runbook / 运行流程

1. Resolve the user's estimand and covariate roles. Read `identification.md` and the chosen
   method section only. Save a config including sample rule, basis, folds, seed and inference.
2. Work in a new output directory. Check disk and resource budget; inspect existing run
   status before restarting. Do not download data or install packages globally by implication.
3. Validate data: numeric finite outcome/treatment, unique unit key when supplied,
   explicit treatment type, binary arm support, covariate roles and dependence groups.
4. Fit preprocessing and nuisance models inside the training fold. A dependency/group key
   belongs to the splitter, not automatically to the covariate matrix. Derived treatment
   terms are constructed before nuisance estimation and separately residualized.
5. Inspect out-of-fold losses, overlap, residual variation/rank and condition number.
   Prediction accuracy alone is not proof of causal identification.
6. Estimate the predeclared target and appropriate uncertainty. Keep every planned run.
   Sensitivity learners/seeds are separate labelled analyses, not a significance search.
7. Deliver config, input hash, package versions, fold assignments, nuisance predictions,
   coefficients/effects, intervals, diagnostics, inference label and run status.
8. Use `causal-audit` before making a causal claim and `causal-report` for interpretation.

## Local quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\python; macOS/Linux: .venv/bin/python
python -m pip install -r requirements-tested.txt
python skills/causal-code/scripts/make_demo.py --out demo
python skills/causal-code/scripts/run_orthogonal.py --config demo/joint.json --out results/joint
python skills/causal-code/scripts/run_orthogonal.py --config demo/ate.json --out results/ate
python skills/causal-code/scripts/run_library.py --config demo/library_plr.json --out results/doubleml
```
Activate the environment or replace `python` with its full path. Output directories are
write-once; use a new directory for changed runs. A failed run is recorded as failed.
Support and coverage restrictions are part of the result, not reasons to fill treatment
values silently. The runner exposes its actual covariance; it does not promise significance.
