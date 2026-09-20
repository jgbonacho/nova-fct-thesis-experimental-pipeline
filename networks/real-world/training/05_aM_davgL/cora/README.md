# Cora

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| Cora [[Datasource](https://web.archive.org/web/20151007064508/http://linqs.cs.umd.edu/projects/projects/lbc/)]                                      | Scientific Citation               | Yes           | 2708  | 5278  | 78  | 2485      | 5069      | 0.9177            | No                        | 7      | Train |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.