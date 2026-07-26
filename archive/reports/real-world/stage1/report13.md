# Report 9 - Experiments on real-world networks (Part II)



## Table of Contents

- [Experience 7 (One network per family)](#experience-7-one-network-per-family)
    - [LAPIN-off Median Normalized Contributions](#lapin-off-median-normalized-contributions)
    - [LAPIN-on Median Normalized Contributions](#lapin-on-median-normalized-contributions)
    - [LAPIN-off Median K Boundary Normalized Contributions](#lapin-off-median-k-boundary-normalized-contributions)
    - [LAPIN-off Median K Boundary Raw Contributions](#lapin-off-median-k-boundary-raw-contributions)
    - [LAPIN-on Median K Boundary Normalized Contributions](#lapin-on-median-k-boundary-normalized-contributions)
    - [LAPIN-on Median K Boundary Raw Contributions](#lapin-on-median-k-boundary-raw-contributions)
- [Experience 8 (Networks grouped by ground-truth type, K, degree assortativity and average degree)](#experience-8-networks-grouped-by-ground-truth-type-k-degree-assortativity-and-average-degree)
    - [LAPIN-off Median Normalized Contributions](#lapin-off-median-normalized-contributions-1)
    - [LAPIN-on Median Normalized Contributions](#lapin-on-median-normalized-contributions-1)
    - [LAPIN-off Median K Boundary Normalized Contributions](#lapin-off-median-k-boundary-normalized-contributions-1)
    - [LAPIN-off Median K Boundary Raw Contributions](#lapin-off-median-k-boundary-raw-contributions-1)
    - [LAPIN-on Median K Boundary Normalized Contributions](#lapin-on-median-k-boundary-normalized-contributions-1)
    - [LAPIN-on Median K Boundary Raw Contributions](#lapin-on-median-k-boundary-raw-contributions-1)
- [Discussion](#discussion)


## Experience 7 (One network per family)

### LAPIN-off Median Normalized Contributions

[Open Folder](../../results/real-world/experience7/results_2026-05-18_08-57-04-357791)

### LAPIN-on Median Normalized Contributions

[Open Folder](../../results/real-world/experience7/results_2026-05-18_09-14-56-020795)

### LAPIN-off Median K Boundary Normalized Contributions

[Open Folder](../../results/real-world/experience7/results_2026-05-18_09-05-00-419889)

### LAPIN-off Median K Boundary Raw Contributions

[Open Folder](../../results/real-world/experience7/results_2026-05-18_09-34-47-258253)

### LAPIN-on Median K Boundary Normalized Contributions

[Open Folder](../../results/real-world/experience7/results_2026-05-18_09-20-51-445538)

### LAPIN-on Median K Boundary Raw Contributions

[Open Folder](../../results/real-world/experience7/results_2026-05-18_09-42-04-813215)

![](../../results/real-world/experience7/results_2026-05-18_09-42-04-813215/non_overlapping_networks.png)

![](../../results/real-world/experience7/results_2026-05-18_09-42-04-813215/overlapping_networks.png)



## Experience 8 (Networks grouped by ground-truth type, K, degree assortativity and average degree)

### LAPIN-off Median Normalized Contributions

[Open Folder](../../results/real-world/experience8/results_2026-05-18_16-06-16-595831)

### LAPIN-on Median Normalized Contributions

[Open Folder](../../results/real-world/experience8/results_2026-05-18_18-22-28-308135)

### LAPIN-off Median K Boundary Normalized Contributions

[Open Folder](../../results/real-world/experience8/results_2026-05-18_16-18-42-834794)

### LAPIN-off Median K Boundary Raw Contributions

[Open Folder](../../results/real-world/experience8/results_2026-05-18_18-48-07-522086)

### LAPIN-on Median K Boundary Normalized Contributions

[Open Folder](../../results/real-world/experience8/results_2026-05-18_18-35-06-093050)

### LAPIN-on Median K Boundary Raw Contributions

[Open Folder](../../results/real-world/experience8/results_2026-05-18_18-59-49-412756)

![](../../results/real-world/experience8/results_2026-05-18_18-59-49-412756/non_overlapping_networks.png)

![](../../results/real-world/experience8/results_2026-05-18_18-59-49-412756/overlapping_networks.png)



## Discussion

- **Observations**
  - Experience 7:
    - Overall, **"LAPIN-off Median Normalized Contributions"** and **"LAPIN-on Median Normalized Contributions"** have very similar performance. In many networks, both configurations fail to estimate the number of communities correctly;
    - Overall, the configuration with **"Median K-Boundary Normalized Contributions"** largely fails to estimate the number of communities. The denormalization used in the configuration with **"Median K-Boundary Raw Contributions"** seems to mitigate this issue;
    - Overall, **"LAPIN-off Median K-Boundary Raw Contributions"** has poor performance in several networks, especially when the corresponding family does not have a calibrated threshold;
    - Overall, **"LAPIN-on Median K-Boundary Raw Contributions"** seems to be the best configuration, with good performance on both non-overlapping and overlapping networks. The only family without a threshold estimation is `network_family_11`. The critical network is `us-political-blogs`, where LAPIN-on strongly degrades the performance. However, this configuration may still have generalization issues because the number of networks is small.
  - Experience 8:
    - As expected, combining networks into families introduces some deviation in the estimated number of communities.
