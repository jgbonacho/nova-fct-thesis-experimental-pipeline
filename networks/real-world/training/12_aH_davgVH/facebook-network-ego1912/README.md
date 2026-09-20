# Facebook Ego-1912 Network

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| Facebook Ego-1912 Network [[Datasource](https://snap.stanford.edu/data/egonets-Facebook.html)]                                                      | Online Social                     | Yes           | 747   | 30025 | 2   | 744       | 30023     | 0.9960            | Yes                       | 45     | Train |

- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.