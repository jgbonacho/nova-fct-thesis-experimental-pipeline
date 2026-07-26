# Report 11 - Non-Spectral Baseline Comparison Design



## Table of Contents

- [Pipeline](#pipeline)
- [Considered Methods](#considered-methods)
- [FADDIS versus SLPA versus CFinder](#faddis-versus-slpa-versus-cfinder)
  - [FADDIS](#faddis)
  - [SLPA](#slpa)
  - [CFinder](#cfinder)
- [SLPA Hyperparameters](#slpa-hyperparameters)
- [CFinder Hyperparameters](#cfinder-hyperparameters)
- [Preliminary Results](#preliminary-results)



## Pipeline

![Pipeline](../imgs/pipeline.svg)



## Considered Methods

- SLPA;
- CFinder.



## FADDIS versus SLPA versus CFinder

1. Select the networks:
   - LFR boundary-set networks;
   - Real-world networks with ground-truth.

2. Configure each method as follows:

   ### FADDIS

   - Construct the affinity matrix:
     - Default affinity matrix, i.e., the adjacency matrix;
   - Do not apply sparsification.
   - Use the LAPIN-off execution mode.
   - Set the threshold $\epsilon$.

   ### SLPA

   - Set the maximum number of iterations, $t$;
   - Set the post-processing threshold, $r$.

   ### CFinder

   - Set the size of the cliques, $k$.

3. Execute:
   - FADDIS;
   - SLPA;
   - CFinder

4. For FADDIS, apply the defuzzification rule according to the ground-truth type:
   - For non-overlapping ground-truth, apply maximum-membership assignment;
   - For overlapping ground-truth, apply node-wise $\alpha$-cut thresholding relative to the maximum membership value.

5. Evaluate the results using:
   - Extrinsic metrics;
   - Computational metrics.



## SLPA Hyperparameters

- Maximum number of iterations (default):

  $$
  t = 100
  $$

- Post-processing threshold (default):

  $$
  r = 0.45
  $$



## CFinder Hyperparameters

- Size of the cliques (default):

  $$
  k = 5
  $$

> **Note:** SLPA and CFinder are non-deterministic and are therefore executed multiple times using different random seeds. The results are reported as the mean ± standard deviation.



## Preliminary Results

- [Boundary Variation Set](../../results/synthetic/boundary_variation_set/non-spectral-baseline/)
