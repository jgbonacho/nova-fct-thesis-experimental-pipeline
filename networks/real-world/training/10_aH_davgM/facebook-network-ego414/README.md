# Facebook Ego-414 Network

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| Facebook Ego-414 Network [[Datasource](https://snap.stanford.edu/data/egonets-Facebook.html)]                                                       | Online Social                     | Yes           | 150   | 1693  | 2   | 148       | 1692      | 0.9867            | Yes                       | 7      | Train |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.