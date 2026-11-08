# Heterogeneity that can be interpreted

1. Define the modifier before fitting. Prefer pre-treatment features for causal heterogeneity.
2. Separate effect discovery from validation (honest forest or held-out discovery/confirmation).
3. Estimate effects and intervals on supported regions; report cell/leaf sample sizes.
4. Test differences directly. One significant group and another nonsignificant group is
   insufficient evidence that the groups differ. Use paired influence functions, a valid
   joint covariance or a dependence-respecting full-pipeline resampling scheme.

For a linear CATE model theta(x)=B phi(x), specify which modifier basis phi(x) is used.
For binary D report mu_1-mu_0; for continuous D state whether `effect` means a unit contrast
or a marginal derivative. With transformed treatment bases apply the chain rule.

## GATE and policy
GATE_k=E[Y(1)-Y(0)|G=k] requires clearly defined groups. When searching many groups,
retain the complete search and use independent confirmation or simultaneous inference.
Policy learning additionally needs a welfare objective, feasibility/cost constraints and
honest evaluation. Rank samples by a fitted CATE only when that ranking is supported.

## Repeated components within the same unit
If each firm or person has several topic/component measurements but only one outcome,
keep a wide unit-level exposure model. For component q, a possible basis is
b_iq=(v_iq,d_iq,d_iq^2,v_iq*d_iq), and Y_i=sum_q b_iq' beta_q+g(C_i)+epsilon_i.
Residualize all component basis terms jointly and verify full rank and component support.
Do not duplicate Y and treat components as independent observations. A topic weight may
be a contemporaneous choice or mediator; its causal role needs separate justification.
This wide model estimates component associations/effects under its own assumptions;
it does not automatically estimate a forest CATE defined over disjoint populations.

Plot uncertainty and data support alongside the effect curve. Keep raw polynomial
coefficients, derivative estimates and subgroup contrasts separately named.
