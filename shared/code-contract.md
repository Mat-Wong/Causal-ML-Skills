# Executable code contract

Three standalone Python scripts are supplied in `skills/causal-code/scripts/`:
- `run_orthogonal.py`: native joint-basis PLR and binary ATE AIPW, with grouped folds,
  fold-local imputation, out-of-fold prediction and score/cluster covariance.
- `run_library.py`: official EconML and DoubleML adapters, with treatment and inference
  restrictions enforced by the installed package version.
- `make_demo.py`: deterministic synthetic data and config generator.

Each script is self-contained. A text-only delivery client can materialize a script unchanged
into a temporary file, then pass explicit config/data/output paths. Resolve each delivered
file to an actual local path before using it in an analysis.

The GitHub distribution records a tested dependency set in `requirements-tested.txt`.
Create a project-local virtual environment; keep the user's existing environments intact.
Read JSON config as data, never execute Python expressions supplied as basis definitions.
Use numeric columns in the runnable examples. Encode categoricals explicitly in a
training-fold pipeline when adapting to new data. Declare any sample exclusion.

For library API changes, inspect the installed signature and the matching official docs.
Keep data-role distinctions: EconML X=effect modifiers, W=other adjustment covariates,
T=treatment, Z=instrument. DoubleML X normally means adjustment covariates.

Confidence intervals are estimator specific. Generic S/T/X learners and arbitrary final
learners may not support inference. Never turn prediction dispersion into a treatment-effect
SE. Grouped folds plus iid library intervals must be labelled as such, or intervals omitted
until compatible cluster inference is implemented.
