import random

import networkx as nx
import numpy as np
from cdlib import algorithms


def slpa(graph: nx.Graph, t: int = 21, r: float = 0.1, seed: int = 0) -> tuple[list[list[int]], int]:
    """
    Compute Speaker-Listener Label Propagation Algorithm (SLPA).

    Parameters:
        graph : (nx.Graph)
            Input NetworkX graph.
        t : (int, optional)
            Number of SLPA iterations.
            Default is 21.
        r : (float, optional)
            Post-processing threshold used to remove labels with low frequency.
            Default is 0.1.
        seed : (int, optional)
            Random seed used before executing SLPA.
            Default is 0.

    Returns:
        predicted_labels : (list[list[int]])
            List of detected community labels assigned to each node.
        k_predicted : (int)
            Number of detected communities.
    """

    random.seed(seed)
    np.random.seed(seed)

    # Compute SLPA.
    clustering = algorithms.slpa(graph, t=t, r=r)

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
