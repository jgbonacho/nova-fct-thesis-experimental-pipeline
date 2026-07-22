import networkx as nx
from cdlib import algorithms


def cfinder(graph: nx.Graph, clique_size: int = 3) -> tuple[list[list[int]], int]:
    """
    Compute CFinder.

    Parameters:
        graph : (nx.Graph)
            Input NetworkX graph.
        clique_size : (int, optional)
            Size of the cliques used by the clique percolation method.
            This parameter does not represent the number of communities.
            Default is 3.

    Returns:
        predicted_labels : (list[list[int]])
            List of detected community labels assigned to each node.
        k_predicted : (int)
            Number of detected communities.
    """

    # Compute CFinder.
    clustering = algorithms.kclique(graph, k=clique_size)

    return _communities_to_labels(clustering.communities, graph.number_of_nodes())


def _communities_to_labels(communities: list, n: int) -> tuple[list[list[int]], int]:
    """
    Convert a list of overlapping communities to node labels.

    Parameters:
        communities : (list)
            List of communities, where each community contains node ids.
        n : (int)
            Number of nodes in the original graph.

    Returns:
        predicted_labels : (list[list[int]])
            List of detected community labels assigned to each node.
        k_predicted : (int)
            Number of detected communities.
    """

    predicted_labels = [[-1] for _ in range(n)]

    for label, community in enumerate(communities):
        for node in community:
            node = int(node)
            if 0 <= node < n:
                if predicted_labels[node] == [-1]:
                    predicted_labels[node] = []
                predicted_labels[node].append(label)

    k_predicted = len(communities)

    if any(labels == [-1] for labels in predicted_labels):
        k_predicted += 1

    return predicted_labels, k_predicted
