# Report 10 - LFR experiments: Selection of the Best Variant/Affinity Design

- *Old rule*:

  - Highest Mean ONMI; Highest Mean Omega; Lowest Mean Relative Error $\frac{|K'-K|}{K}$

- *New rule*:

$$
\mathcal{A}_i
=
\left\{
d \in D_i :
\overline{\operatorname{ONMI}}(d)
\geq
\overline{\operatorname{ONMI}}_{\max}
-
\delta_{\operatorname{ONMI}},
\;
\overline{\Omega}(d)
\geq
\overline{\Omega}_{\max}
-
\delta_{\Omega},
\;
\overline{E_K}(d)
\leq
\overline{E_K}_{\min}
+
\delta_{E_K}
\right\}
$$

$$
d_i^{*}
=
\underset{d \in \mathcal{A}_i}{\arg\min}
\;
\overline{T}(d)
$$

where:

$$
E_K
=
\frac{|K'-K|}{K}
$$

- **Acceptable**:
  - **Acceptable ONMI** (high mean ONMI):
    - $\overline{\operatorname{ONMI}}(d) \geq \overline{\operatorname{ONMI}}_{\max}-\delta_{\operatorname{ONMI}}$
      - $\overline{\operatorname{ONMI}}_{\max}=\max(\overline{\operatorname{ONMI}}(d))$
      - $\delta_{\operatorname{ONMI}}=$ `PARETO_TOLERANCE_FRACTION_ONMI` $\times \left(\overline{\operatorname{ONMI}}_{\max}-\overline{\operatorname{ONMI}}_{\min}\right)$
      - `PARETO_TOLERANCE_FRACTION_ONMI = 0.1`
  - **Acceptable Omega** (high mean Omega):
    - $\overline{\Omega}(d) \geq \overline{\Omega}_{\max}-\delta_{\Omega}$
      - $\overline{\Omega}_{\max}=\max(\overline{\Omega}(d))$
      - $\delta_{\Omega}=$ `PARETO_TOLERANCE_FRACTION_OMEGA` $\times \left(\overline{\Omega}_{\max}-\overline{\Omega}_{\min}\right)$
      - `PARETO_TOLERANCE_FRACTION_OMEGA = 0.1`
  - **Acceptable Relative Error of $K$** (low mean relative error):
    - $\overline{E_K}(d) \leq \overline{E_K}_{\min}+\delta_{E_K}$
      - $\overline{E_K}_{\min}=\min(\overline{E_K}(d))$
      - $\delta_{E_K}=$ `PARETO_TOLERANCE_FRACTION_KERR` $\times \left(\overline{E_K}_{\max}-\overline{E_K}_{\min}\right)$
      - `PARETO_TOLERANCE_FRACTION_KERR = 0.5`

- **Pareto-based Filtering and Runtime Parsimony**
  - *Select*: Runtime-based Parsimony Principle over Acceptables

  - *Fallback*: Highest Mean ONMI; Highest Mean Omega; Lowest Mean Relative Error $\frac{|K'-K|}{K}$
