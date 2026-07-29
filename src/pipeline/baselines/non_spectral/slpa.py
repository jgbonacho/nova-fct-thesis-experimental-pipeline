import random

import networkx as nx
import numpy as np
from cdlib import algorithms


def slpa(graph: nx.Graph, t: int, r: float, seed: int) -> tuple[list[list[int]], int]:
    """
    Compute the Speaker-Listener Label Propagation Algorithm (SLPA) community detection algorithm.

    Parameters:
        graph : (nx.Graph)
            Input graph.
        t : (int)
            Number of SLPA iterations.
        r : (float)
            Post-processing threshold used to remove labels with low occurrence probabilities.
        seed : (int)
            Random seed.

    Returns:
        predicted_labels : (list[list[int]])
            Predicted community labels for each node.
        k_predicted : (int)
            Number of predicted communities.
    """

    random.seed(seed)
    np.random.seed(seed)

    # Compute SLPA.
    clustering = algorithms.slpa(graph, t=t, r=r)

    return _communities_to_labels(clustering.communities, graph.number_of_nodes())


def _communities_to_labels(communities: list, n: int) -> tuple[list[list[int]], int]:
    """
    Convert the detected communities into predicted node labels.
    Nodes without assigned communities are labelled with [-1].

    Parameters:
        communities : (list)
            Detected communities.
        n : (int)
            Number of nodes.

    Returns:
        predicted_labels : (list[list[int]])
            Predicted community labels for each node.
        k_predicted : (int)
            Number of predicted communities.
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

    return predicted_labels, k_predicted
