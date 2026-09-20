# Dolphins

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| Dolphins [[Datasource](https://websites.umich.edu/~mejn/netdata/)]                                                                                  | Geographic                        | No            | 62    | 159   | 1   | 62        | 159       | 1.0000            | -                         | -      | Test  |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.