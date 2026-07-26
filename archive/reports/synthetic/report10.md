# Report 10 - Spectral Baseline Comparison Design



## Table of Contents

- [Pipeline](#pipeline)
- [Considered Methods](#considered-methods)
- [FADDIS versus NJW+FCM](#faddis-versus-njwfcm)
- [NJW+FCM Hyperparameters](#njwfcm-hyperparameters)
  - [NJW](#njw)
  - [FCM](#fcm)
- [Preliminary Results](#preliminary-results)



## Pipeline

![Pipeline](../imgs/pipeline.svg)



## Considered Methods
   
- NJW+FCM



## FADDIS versus NJW+FCM

1. Select the networks:
   - LFR boundary-set networks;
   - Real-world networks with ground-truth.

2. Construct the affinity matrix:
   - Default affinity matrix, i.e., the adjacency matrix.

3. Do not apply sparsification.

4. Use the LAPIN-off execution mode.

5. Use the ground-truth number of communities, $K$:
   - As the stopping criterion for FADDIS;
   - As the number of clusters for NJW + FCM.

6. Execute:
   - FADDIS;
   - NJW + FCM.

7. Apply the defuzzification rule according to the ground-truth type:
   - For non-overlapping ground-truth, apply maximum-membership assignment;
   - For overlapping ground-truth: 
      - Apply node-wise $\alpha$-cut thresholding relative to the maximum membership value for FADDIS. This is not applicable to NJW+FCM because the memberships of each node sum to 1;
      - Apply fixed $\lambda$-thresholding.

8. Evaluate the results using:
   - Extrinsic metrics;
   - Intrinsic metrics;
   - Computational metrics.



## NJW+FCM Hyperparameters

### NJW

- Number of clusters:

  $$
  K = K_{\text{ground-truth}}
  $$

- Scaling parameter $\sigma$ (skipped)

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
  t_{\max} = 300
  $$

> **Note:** NJW + FCM is non-deterministic and is therefore executed multiple times using different random seeds. The results are reported as the mean ± standard deviation.



## Preliminary Results

- [Boundary Variation Set](../../results/synthetic/boundary_variation_set/spectral-baseline/)
