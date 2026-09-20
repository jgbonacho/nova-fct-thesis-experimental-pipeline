# Facebook Ego-0 Network

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| Facebook Ego-0 Network [[Datasource](https://snap.stanford.edu/data/egonets-Facebook.html)]                                                         | Online Social                     | Yes           | 333   | 2519  | 5   | 324       | 2514      | 0.9730            | Yes                       | 22     | Train |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.