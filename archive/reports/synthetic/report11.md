# Report 11 - Baseline Comparison Design

## Pipeline

![Pipeline](../imgs/pipeline.svg)

## Spectral Baselines

### Considered Methods
   
- NJW+FCM

### FADDIS versus NJW+FCM

1. Select the networks:
   - LFR boundary-set networks;
   - Real-world networks.

2. Construct the affinity matrix:
   - Default affinity matrix, i.e., the adjacency matrix;
   - Alternative affinity matrices: Kulczynski, Dice, Ochiai, IP and CosIP.

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
   - For overlapping ground-truth, apply node-wise $\alpha$-cut thresholding relative to the maximum membership value.

8. Evaluate the results using:
   - Extrinsic metrics;
   - Intrinsic metrics;
   - Computational metrics.

### NJW+FCM Hyperparameters

#### NJW

- Number of clusters:

  $$
  K = K_{\text{ground-truth}}
  $$

- Scaling parameter $\sigma$ (skipped)

#### FCM

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

### Preliminary Results

- [Boundary Variation Set](../../results/synthetic/boundary_variation_set/spectral-baseline/)

## Non-Spectral Baselines

### Considered Methods

- SLPA;
- [CFinder].

### FADDIS versus SLPA

1. Select the networks:
   - LFR boundary-set networks;
   - Real-world networks.

2. Configure each method as follows:

   #### FADDIS

   - Construct the affinity matrix:
     - Default affinity matrix, i.e., the adjacency matrix;
   - Do not apply sparsification.
   - Use the LAPIN-off execution mode.
   - Set the threshold $\epsilon$.

   #### SLPA

   - Set the maximum number of iterations, $t$;
   - Set the post-processing threshold, $r$.

3. Execute:
   - FADDIS;
   - SLPA.

4. For FADDIS, apply the defuzzification rule according to the ground-truth type:
   - For non-overlapping ground-truth, apply maximum-membership assignment;
   - For overlapping ground-truth, apply node-wise $\alpha$-cut thresholding relative to the maximum membership value.

5. Evaluate the results using:
   - Extrinsic metrics;
   - Computational metrics.

### SLPA Hyperparameters

- Maximum number of iterations (default):

  $$
  t = 100
  $$

- Post-processing threshold (default):

  $$
  r = 0.45
  $$

> **Note:** SLPA is non-deterministic and is therefore executed multiple times using different random seeds. The results are reported as the mean ± standard deviation.

### Preliminary Results

- [Boundary Variation Set](../../results/synthetic/boundary_variation_set/non-spectral-baseline/)
