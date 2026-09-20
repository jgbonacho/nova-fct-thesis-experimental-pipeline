# American College Football

| Network                                                                                                                                    | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| American College Football [[Datasource](https://websites.umich.edu/~mejn/netdata/)]                                                        | Sports                            | Yes           | 115   | 613   | 1   | 115       | 613       | 1.0000            | No                        | 12     | Train |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.