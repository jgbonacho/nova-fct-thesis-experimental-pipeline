# E-mail EU Core

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| E-mail EU Core [[Datasource](https://snap.stanford.edu/data/email-Eu-core.html/)]                                                                   | Communication                     | Yes           | 1005  | 16064 | 20  | 986       | 16064     | 0.9811            | No                        | 42     | Train |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.