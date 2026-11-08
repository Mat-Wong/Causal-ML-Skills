# Causal ML Skills · 因果机器学习技能包

**从识别假设、公式和方法选择，到可运行代码、异质性分析与结果核验。**

An agent skill suite for causal research with Codex, Claude Code and other
SKILL.md-compatible agents. Independent community synthesis grounded in the
[Microsoft EconML documentation](https://www.microsoft.com/en-us/research/project/econml/)
and [DoubleML documentation](https://docs.doubleml.org/stable/index.html).

![Skills](https://img.shields.io/badge/skills-9-blue)
![Tests](https://img.shields.io/badge/tests-33%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Language](https://img.shields.io/badge/language-English%20%2B%20中文-orange)

## 9个可以分别调用的技能

| Skill | 用途 |
|---|---|
| `causal-theory` | 潜在结果、DAG、识别条件与效应定义 |
| `causal-method-router` | 根据研究问题和数据选择方法 |
| `cml-estimators` | S/T/X/R/DR、因果森林、正交森林、IV方法 |
| `dml-estimation` | PLR、IRM、PLIV、IIVM与联合非线性基函数 |
| `causal-code` | Python代码、合成数据和官方库适配 |
| `causal-run` | 分折、预处理、运行与可复现交付 |
| `causal-heterogeneity` | CATE、GATE、局部导数与差异检验 |
| `causal-audit` | 重叠性、坏控制、泄漏、聚类和敏感性 |
| `causal-report` | 按证据解释系数、区间与研究结论 |

## 方法与公式

**DML / R-learner**

$$Y-E[Y\mid C]=\theta(X)\{D-E[D\mid C]\}+\epsilon$$

**联合平方与交互**

$$\Phi=(a,b,b^2,ab),\quad Y=\Phi^\top\beta+g(C)+\epsilon$$

每个基函数分别交叉拟合，最后联合估计。平方残差与残差的平方含义不同。

**DR / AIPW**：结合结果模型与倾向得分，估计ATE或CATE。

**Causal Forest / GRF**：通过局部正交矩估计效应异质性。

**IV Learners**：区分PLIV、IIVM、OrthoIV、DMLIV和DRIV的目标与假设。

详细推导按需载入，避免每次把整份教程塞进上下文。

## 安装与使用

### Codex
将所需的 `skills/<name>` 文件夹连同其内部references、scripts安装到个人skills目录。
每个skill都包含自己需要的参考资料。也可以直接让Codex读取仓库中的某个SKILL.md。

```text
使用 /path/to/Causal-ML-Skills/skills/dml-estimation/SKILL.md，
解释我的模型应该用哪一种正交分数，然后实现并核验。
```

### Claude Code
```text
/plugin marketplace add Mat-Wong/Causal-ML-Skills
/plugin install causal-ml-skills@mat-wong-causal-ml
```

## 跑通合成数据
```bash
python -m venv .venv
# 激活虚拟环境，再执行：
pip install -r requirements-tested.txt
python skills/causal-code/scripts/make_demo.py --out demo
python skills/causal-code/scripts/run_orthogonal.py --config demo/joint.json --out results/joint
python skills/causal-code/scripts/run_orthogonal.py --config demo/ate.json --out results/ate
python skills/causal-code/scripts/run_library.py --config demo/library_plr.json --out results/doubleml
python -m pytest tests -q
```

运行记录保存输入SHA、配置、版本、分折、预测和完整结果。具体已测范围以
[VALIDATION.json](VALIDATION.json)为准；方法讲解范围与可执行接口分别列明。

## 已核验的代码范围

| 路径 | 实际测试的估计器 |
|---|---|
| 内置正交估计 | 联合基函数PLR、二元处理ATE AIPW |
| DoubleML | PLR、IRM、PLIV、IIVM |
| EconML | S/T/X、LinearDML、LinearDRLearner、CausalForestDML、OrthoIV、DMLIV |

33项测试覆盖合成数据效应恢复、数值协方差对照、分折隔离、异常处理和独立脚本执行。
正交森林、DRIV、DeepIV有方法说明，运行时仍需另行实现与核验。
库适配器按各估计器实际能力提供推断，详细边界见验证记录。

## 使用示例
“先帮我判断哪些变量适合做控制，再选择DML模型。”

“保留原始平方项和交互项，分别正交化，报告完整系数与区间。”

“估计异质性后，直接检验组间差异，并检查重叠性和样本支持。”

## Sources and licence
来源与访问日期见[shared/sources.json](shared/sources.json)。本项目使用MIT许可证；
理论说明和代码为社区整理实现，API以所链接的官方文档为准。
