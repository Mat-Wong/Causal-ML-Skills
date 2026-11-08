# Reporting without changing the research question

Lead with the estimate and its uncertainty, then state what supports its interpretation.
For each result give N, target, treatment scale, adjustment set, learner, folds/repetitions,
covariance type, estimate, SE, confidence interval and p-value when inference supports it.
If no valid SE exists, report the estimate without manufacturing a p-value.

Separate:
- Raw structural coefficients, e.g. beta_b in Y=beta_a*a+beta_b*b+beta_bb*b^2+beta_ab*a*b+g(C).
- Local derivative beta_b+2*beta_bb*b+beta_ab*a at a declared supported reference.
- Average derivative over a stated population and weights.
- A direct group contrast and an omnibus joint test.

Example language: “Under the stated adjustment and response assumptions, the estimated
effect of moving D from d0 to d1 is ... (95% CI ...).” If identification is unresolved,
use “adjusted association.” Avoid describing a score as a psychological construct without
separate measurement evidence. A nonsignificant estimate does not prove zero effect.

For heterogeneity, show effect curves/groups with uncertainty and support counts. Test
the contrast directly; do not infer a difference from one p<.05 and another p>.05.
Disclose exploratory choices, planned sensitivity runs, deviations and failed diagnostics.
Trace each reported numerical result to a saved machine-readable artifact.
