---
name: cml-estimators
description: "Explain and compare S/T/X/R/DR learners, causal forests, orthogonal forests and IV learners. Map each to assumptions, losses, available inference and official APIs."
---

# CML流派与公式 / cml-estimators

Use this module for the capability in the description. Match the user's language.
Read the relevant sections of `references/methods.md`; the skill includes its own required references for standalone installation.

## Work contract

1. State the observational unit, outcome, treatment, adjustment variables, effect modifiers,
   target population and estimand. Preserve an already agreed specification.
2. Explain the chosen equation and every symbol. Declare identification assumptions
   separately from prediction quality and computational success.
3. Use the linked reference to choose an estimator, write code, run or audit as requested.
   Load only references needed for this task. `references/sources.json` maps official sources.
4. Return the concrete requested artifact or explanation, including assumptions,
   uncertainty and limitations appropriate to the design. Report null findings too.

## Important decisions

- Specify discrete contrasts or continuous derivatives explicitly. Polynomial coefficients,
  average derivatives and coefficients after recentering answer different hypotheses.
- Choose learners and tuning using training-only predictive losses. Cross-fit every learned
  preprocessing step. Record declared seeds and all planned runs; do not select a run by p-value.
- For dependent data, make folds respect the dependence unit and use compatible inference.
  Grouped folds alone do not make a library's confidence intervals cluster robust.
- A successful fit does not establish unconfoundedness, exclusion or overlap. Interpret
  results as adjusted associations while causal identification remains unsupported.

## Module handoffs

For identification questions use `causal-theory`; estimator choice uses `causal-method-router`.
After design agreement, `causal-code` implements and `causal-run` executes.
`causal-audit` checks evidence; `causal-report` explains verified output.
These handoffs are optional capabilities, not permission to spawn agents or change scope.
