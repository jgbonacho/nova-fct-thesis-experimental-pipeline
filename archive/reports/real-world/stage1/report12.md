# Report 8 - Experiments on real-world networks (Part I)



## Table of Contents

- [Experience 0 (Baseline)](#experience-0-baseline)
- [Experience 1 (All networks in the same family)](#experience-1-all-networks-in-the-same-family)
- [Experience 2 (Networks grouped by ground-truth type)](#experience-2-networks-grouped-by-ground-truth-type)
- [Experience 3 (Networks grouped by ground-truth type and K range)](#experience-3-networks-grouped-by-ground-truth-type-and-k-range)
- [Experience 4 (Networks grouped by ground-truth type and the proportion of communities relative to the number of nodes)](#experience-4-networks-grouped-by-ground-truth-type-and-the-proportion-of-communities-relative-to-the-number-of-nodes)
- [Experience 5 (Networks grouped by ground-truth type and average degree)](#experience-5-networks-grouped-by-ground-truth-type-and-average-degree)
- [Experience 6 (One network per family)](#experience-6-one-network-per-family)
- [Discussion](#discussion)



## Experience 0 (Baseline)

[Open Folder](../results/real-world/baseline/)

- **Observations**:
    - Zachary Karate Club: LAPIN-off or LAPIN-on
    - **US Political Blogs: LAPIN-off (critical)**
    - Books about US Politics: LAPIN-on (critical)
    - American College Football: LAPIN-off
    - E-mail EU Core: LAPIN-on (critical)
    - Facebook Ego-414 Network: LAPIN-on
    - Facebook Ego-107 Network: LAPIN-on 
    - Facebook Ego-698 Network: LAPIN-on
    - Facebook Ego-3980 Network: LAPIN-on
    - Facebook Ego-348 Network: LAPIN-on
    - Facebook Ego-686 Network: LAPIN-on
    - Facebook Ego-1684 Network: LAPIN-on
    - Facebook Ego-0 Network: LAPIN-on
    - Facebook Ego-3437 Network: LAPIN-on
    - Facebook Ego-1912 Network: LAPIN-on



## Experience 1 (All networks in the same family)

- [LAPIN-off + Extraction of K desired clusters](../../results/real-world/experience1/results_2026-05-13_23-52-22-951933/)
- [LAPIN-off + Extraction of clusters until the end](../../results/real-world/experience1/results_2026-05-13_23-59-16-802069/)
- [LAPIN-on + Extraction of K desired clusters](../../results/real-world/experience1/results_2026-05-14_00-10-12-245299/)
- [LAPIN-on + Extraction of clusters until the end](../../results/real-world/experience1/results_2026-05-14_00-18-47-225354/)



## Experience 2 (Networks grouped by ground-truth type)

- [LAPIN-off + Extraction of K desired clusters](../../results/real-world/experience2/results_2026-05-14_10-39-26-010867/)
- [LAPIN-off + Extraction of clusters until the end](../../results/real-world/experience2/results_2026-05-14_10-45-38-104210/)
- [LAPIN-on + Extraction of K desired clusters](../../results/real-world/experience2/results_2026-05-14_10-56-02-985059/)
- [LAPIN-on + Extraction of clusters until the end](../../results/real-world/experience2/results_2026-05-14_11-04-15-844508/)



## Experience 3 (Networks grouped by ground-truth type and K range)

- [LAPIN-off + Extraction of K desired clusters](../../results/real-world/experience3/results_2026-05-14_11-18-43-724134/)
- [LAPIN-off + Extraction of clusters until the end](../../results/real-world/experience3/results_2026-05-14_11-23-46-815439/)
- [LAPIN-on + Extraction of K desired clusters](../../results/real-world/experience3/results_2026-05-14_11-33-29-613869/)
- [LAPIN-on + Extraction of clusters until the end](../../results/real-world/experience3/results_2026-05-14_11-39-51-255386/)



## Experience 4 (Networks grouped by ground-truth type and the proportion of communities relative to the number of nodes)

- [LAPIN-off + Extraction of K desired clusters](../../results/real-world/experience4/results_2026-05-14_11-52-11-686062/)
- [LAPIN-off + Extraction of clusters until the end](../../results/real-world/experience4/results_2026-05-14_11-58-40-374031/)
- [LAPIN-on + Extraction of K desired clusters](../../results/real-world/experience4/results_2026-05-14_12-08-32-563204/)
- [LAPIN-on + Extraction of clusters until the end](../../results/real-world/experience4/results_2026-05-14_12-18-20-912820/)



## Experience 5 (Networks grouped by ground-truth type and average degree)

- [LAPIN-off + Extraction of K desired clusters](../../results/real-world/experience5/results_2026-05-14_12-32-25-330204/)
- [LAPIN-off + Extraction of clusters until the end](../../results/real-world/experience5/results_2026-05-14_12-41-51-363988/)
- [LAPIN-on + Extraction of K desired clusters](../../results/real-world/experience5/results_2026-05-14_12-52-28-621268/)
- [LAPIN-on + Extraction of clusters until the end](../../results/real-world/experience5/results_2026-05-14_13-02-32-182253/)



## Experience 6 (One network per family)

- [LAPIN-off + Extraction of K desired clusters](../../results/real-world/experience6/results_2026-05-14_13-17-59-894947/)
- [LAPIN-off + Extraction of clusters until the end](../../results/real-world/experience6/results_2026-05-14_13-27-26-954044/)
- [LAPIN-on + Extraction of K desired clusters](../../results/real-world/experience6/results_2026-05-14_14-42-09-654746/)
- [LAPIN-on + Extraction of clusters until the end](../../results/real-world/experience6/results_2026-05-14_14-50-59-277172/)



## Discussion

- **Observations**
  - Overall, configurations with **"Extraction of clusters until the end"**, both LAPIN-on and LAPIN-off, largely fail to estimate the number of communities;
  - Overall, configurations with **"Extraction of K desired clusters"**, both LAPIN-on and LAPIN-off, tend to produce similar results;
  - Overall, none of the configurations is able to correctly estimate the number of communities, with a tendency to overestimate it, even when using one network per family.
