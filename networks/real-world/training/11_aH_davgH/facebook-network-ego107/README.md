# Facebook Ego-107 Network

| Network                                                                                                                                             | Knowledge Domain                  | Ground-Truth? | Nodes | Edges | CC  | Nodes LCC | Edges LCC | Relative Size LCC | Overlapping Ground-Truth? | K LCC  | Set   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|---------------|-------|-------|-----|-----------|-----------|-------------------|---------------------------|--------|-------|
| Facebook Ego-107 Network [[Datasource](https://snap.stanford.edu/data/egonets-Facebook.html)]                                                       | Online Social                     | Yes           | 1034  | 26749 | 1   | 1034      | 26749     | 1.0000            | Yes                       | 9      | Train |


- Pre-processing applied as needed through auxiliary Python script:
    - Conversion to an undirected graph;
    - Removal of edge weights;
    - Removal of parallel edges and self-loops.