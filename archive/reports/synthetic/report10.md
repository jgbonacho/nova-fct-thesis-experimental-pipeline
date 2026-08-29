# Report 10 - Spectral Baseline Comparison Design and Results



## Table of Contents

- [Pipeline](#pipeline)
- [Considered Methods](#considered-methods)
- [FADDIS versus NJW+FCM](#faddis-versus-njwfcm)
- [FADDIS Hyperparameters](#faddis-hyperparameters)
- [NJW+FCM Hyperparameters](#njwfcm-hyperparameters)
  - [NJW](#njw)
  - [FCM](#fcm)
- [Results](#results)
  - [Boundary Variation Set](#boundary-variation-set)
  - [Membership Variation Set](#membership-variation-set)
  - [Overlap Variation Set](#overlap-variation-set)



## Pipeline

![Pipeline](../imgs/pipeline.svg)



## Considered Methods
   
- NJW+FCM



## FADDIS versus NJW+FCM

1. Select the networks:
   - LFR boundary-set networks.

2. Construct the affinity matrix:
   - Default affinity matrix, i.e., the adjacency matrix;
   - Alternative best-performing affinity design IP ($\beta=0$).

3. Do not apply sparsification.

4. Use the LAPIN-off execution mode.

5. Use the ground-truth number of communities, $K$:
   - As the stopping criterion for FADDIS;
   - As the number of clusters for NJW+FCM.

6. Execute:
   - FADDIS;
   - NJW + FCM.

7. Apply the defuzzification rule according to the ground-truth type:
   - For overlapping ground-truth: 
      - Apply node-wise $\alpha$-cut thresholding relative to the maximum membership value, with $\gamma$ hyperparameter, for FADDIS. This is not theoretically and empirical applicable to NJW+FCM because the memberships of each node sum to 1;
      - Apply fixed $\psi$-thresholding, with maximum-membership assignment fallback, for NJW+FCM.

8. Evaluate the results using:
   - Extrinsic metrics (ONMI, Omega);
   - Intrinsic metrics (Fuzzy-Modularity, Conductance-BN);
   - Computational metrics (Runtime (1 (A) -> 7 (Defuzzification)) with multiple runs).

> **Note:** NJW + FCM is non-deterministic and is therefore executed multiple times using different random seeds. The results are reported as the mean ± standard deviation.



## FADDIS Hyperparameters

- Stopping criterion:

  $$
  K = K_{\text{ground-truth}}
  $$

- Defuzzification hyperparameter $\gamma$ (best observed from LFR experiments):

  $$
  \gamma = 0.8
  $$



## NJW+FCM Hyperparameters

### NJW

- Number of clusters:

  $$
  K = K_{\text{ground-truth}}
  $$

- Scaling parameter $\sigma$ (skipped)

- Defuzzification threshold $\psi$ (reference value):

  $$
  \psi = 0.1
  $$

### FCM

- Fuzziness parameter (default):

  $$
  m = 2.0
  $$

- Convergence tolerance (default):

  $$
  e = 10^{-5}
  $$

- Maximum number of iterations (default):

  $$
  t_{\max} = 100
  $$

- Seeds:

$$
   [0, 1, 2]
$$



## Results

### Boundary Variation Set

- [Results](../../results/synthetic/boundary_variation_set/spectral-baseline/results_2026-08-23_22-59-23-685832/mu_spectral_comparison_results.csv)
- [Summary](../../results/synthetic/boundary_variation_set/spectral-baseline/results_2026-08-23_22-59-23-685832/mu_spectral_comparison_summary.csv)

![Plots](../../results/synthetic/boundary_variation_set/spectral-baseline/results_2026-08-23_22-59-23-685832/mu_spectral_algorithms.png)

### Membership Variation Set

- [Results](../../results/synthetic/membership_variation_set/spectral-baseline/results_2026-08-24_01-42-24-752338/om_spectral_comparison_results.csv)
- [Summary](../../results/synthetic/membership_variation_set/spectral-baseline/results_2026-08-24_01-42-24-752338/om_spectral_comparison_summary.csv)

![Plots](../../results/synthetic/membership_variation_set/spectral-baseline/results_2026-08-24_01-42-24-752338/om_spectral_algorithms.png)

### Overlap Variation Set

- [Results](../../results/synthetic/overlap_variation_set/spectral-baseline/results_2026-08-24_08-08-27-013832/on_spectral_comparison_results.csv)
- [Summary](../../results/synthetic/overlap_variation_set/spectral-baseline/results_2026-08-24_08-08-27-013832/on_spectral_comparison_summary.csv)

![Plots](../../results/synthetic/overlap_variation_set/spectral-baseline/results_2026-08-24_08-08-27-013832/on_spectral_algorithms.png)
