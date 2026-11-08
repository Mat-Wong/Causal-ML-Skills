# DML equations and implementation invariants

## Orthogonality and cross-fitting
Let E[psi(W;theta_0,eta_0)]=0. Neyman orthogonality requires the derivative of this
moment with respect to nuisance perturbations to vanish at eta_0. It reduces sensitivity
to small nuisance errors under regularity and product-rate conditions. It does not remove
unobserved confounding. Cross-fitting predicts each observation from models trained elsewhere.

## PLR
\[
Y=D\theta+g(C)+\epsilon,\quad E[\epsilon|D,C]=0,
\quad D=m(C)+v.
\]
Let ell(C)=E[Y|C]. The partialling-out score is
\[
\psi_i=(D_i-\hat m_i)\{Y_i-\hat\ell_i-\theta(D_i-\hat m_i)\}.
\]
ell includes the conditional treatment contribution; it is not simply g.

## Joint nonlinear basis
For two exposures A=(a,b), choose a basis before looking at significance, e.g.
Phi=(a,b,b^2,ab). This defines
\[
Y=\Phi(A)'\beta+g(C)+\epsilon.
\]
Learn E[Y|C] and each E[Phi_j|C] on the training fold; jointly solve
\[
\hat\beta=\{\sum_i\tilde\Phi_i\tilde\Phi_i'\}^{-1}
\sum_i\tilde\Phi_i\tilde Y_i.
\]
Do not square residual b or multiply residual a and b to form the basis. Their conditional
moments differ. Do not add the other deterministic basis columns to C: they can recover
the target exposure and destroy residual identification. A default scalar PLR loop with
the other treatments as covariates is not this joint estimator. Use the bundled vector runner.

The structural derivatives are beta_a+beta_ab*b and beta_b+2*beta_bb*b+beta_ab*a.
Recentring changes the coefficient's null hypothesis; a significant local derivative does
not establish that the original coefficient is significant. The basis coordinates are not
independent interventions. Evaluate contrasts along feasible exposure combinations.

## IRM / ATE
For binary D use the cross-fitted AIPW pseudo-outcome in `methods.md`.
The score is psi_i=phi_i-theta. ATT uses a different score/target; the shipped native
AIPW runner estimates ATE only. Use DoubleML's documented ATT setting for ATT.

## PLIV
\[
Y=D\theta+g(C)+\epsilon,\quad E[\epsilon|Z,C]=0.
\]
Residualize Y,D,Z on C; a partialling-out moment is
\[
\psi_i=(Z_i-\hat r_i)\{Y_i-\hat\ell_i-\theta(D_i-\hat m_i)\}.
\]
For vector instruments/treatments use an appropriate GMM/IV implementation and check rank.

## IIVM
For binary Z,D, define arm-specific g_z(C)=E[Y|Z=z,C], r_z(C)=E[D|Z=z,C],
and p(C)=P(Z=1|C). Let phi_Y and phi_D be the respective AIPW instrument contrasts.
Then theta=E[phi_Y]/E[phi_D]; its score is phi_Y-theta*phi_D.
The target is a LATE under IV assumptions, not a population ATE by default.

## Dependence and inference
Use cluster-respecting outer and inner folds. For score contributions s_i=tildePhi_i*u_i
and G=sum_i tildePhi_i tildePhi_i', the empirical covariance is G^{-1} sum_i s_i s_i' G^{-1}.
For clusters, replace s_i by within-cluster sums; state any CR1 finite-sample correction
and normal versus t(G_clusters-1) reference. Independence, cluster count, nuisance rates
and residual rank are assumptions; ordinary VIF alone cannot establish them.

Record repeated splits as a declared sensitivity set. For repeated DML use the package's
documented aggregation and split-uncertainty treatment; do not average p-values or pick
the smallest. Residual HC3 from a final least-squares regression is a labelled sensitivity,
not automatically the library's complete DML uncertainty calculation.
