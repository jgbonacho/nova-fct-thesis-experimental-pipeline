# Co-authorships in Network Science

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| Co-authorships in Network Science [[Datasource](https://websites.umich.edu/~mejn/netdata/)]                                                         | Co-authorship                     | No            | 1589  | 2742  | 396 | 379       | 914       | 0.2385            | -                         | -      | Test  |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.