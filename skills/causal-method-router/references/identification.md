# Identification before estimation / 先识别，再估计

## Unit, time and target
Define one row's unit and the order of covariates, treatment and outcome.
Let D be treatment, Y(d) potential outcome, C adjustment covariates and X effect modifiers.
X can be included in C; software sometimes splits them into X and W. Keep their roles explicit.

For binary treatment:
\[
ATE=E[Y(1)-Y(0)],\quad ATT=E[Y(1)-Y(0)\mid D=1],
\quad \tau(x)=E[Y(1)-Y(0)\mid X=x].
\]
For continuous treatment define the dose contrast or derivative:
\[
\tau(d_1,d_0,x)=E[Y(d_1)-Y(d_0)\mid X=x],
\quad \partial_d E[Y(d)\mid X=x].
\]
An average structural derivative differs from a coefficient in a misspecified constant-slope model.

## Observational identification
Under consistency, conditional exchangeability (Y(0),Y(1)) independent of D given C,
and positivity 0<P(D=1|C)<1, binary contrasts are identified by adjustment.
For continuous D the density/support must permit the proposed local contrast, and
the assumed response form must be defensible. A rich learner cannot supply missing support.

Draw a temporal DAG. Adjust for common causes when justified. Conditioning on a mediator
changes a total-effect question; conditioning on a collider can introduce bias. Explain
the role of every disputed control. A same-day variable is not automatically pre-treatment.

## Instruments and designs
An instrument Z needs relevance, exclusion and suitable exogeneity. For binary IV with
monotonicity and nonzero first stage, a Wald-type ratio can identify a complier LATE.
An arbitrary proxy correlated with D is not enough. A weak first stage requires weak-IV
robust analysis; a conventional interval may be misleading.

DiD additionally requires a credible counterfactual trend and an appropriate timing design.
RDD needs local continuity and a real assignment threshold. Neither design follows from
selecting a similarly named ML class. Read the current library documentation for those designs.

## 中文解释顺序
先说“对谁、改变什么、比较什么、何时观察结果”。随后列出识别假设，最后解释模型。
潜在结果中的因果解释、估计器的一致性和程序运行成功需要分别说明。
实证中的显著性取决于信号、样本、变异与不确定性；它不能作为需要保证的运行结果。

Sources: Microsoft EconML project overview; EconML DML, DR and IV guides;
DoubleML model guide, linked in `sources.json`.
