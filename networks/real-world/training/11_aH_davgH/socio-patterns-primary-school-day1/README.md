# SocioPatterns Primary School day 1

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| SocioPatterns Primary School day 1 [[Datasource](https://sociopatterns.org/datasets/primary-school-cumulative-networks/)]                           | Human Contact                     | Yes           | 236   | 5899  | 1   | 236       | 5899      | 1.0000            | No                        | 11     | Train |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.