import networkx as nx
import numpy as np

from networkx import conductance
from networkx.algorithms.community import modularity
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import IntrinsicMetrics


def compute_intrinsic_metrics(
        graph: nx.Graph,
        A: np.ndarray,
        U: np.ndarray,
        predicted_labels: list[int] | list[list[int]],
        overlapping: bool = True
) -> IntrinsicMetrics:
    """
    Compute intrinsic metrics.

    Parameters:
        graph : (nx.Graph)
            The graph.
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.
        U : (np.ndarray | np.matrix, shape[n,k])
            Fuzzy memberships per node per community.
        predicted_labels : (list[int], length n | list[list[int]], length n)
            Predicted labels.
        overlapping : (bool, optional)
            Whether the predicted labels are overlapping.
            Default is True.

    Returns:
        evaluation_scores : (IntrinsicMetrics)
            Intrinsic metrics.
    """

    communities = _build_communities_from_labels(graph, predicted_labels, overlapping)
    if not overlapping:
        evaluation_scores = IntrinsicMetrics(
            modularity=_compute_modularity(graph, communities),
            conductance=_compute_conductance(graph, communities),
        )
    else:
        evaluation_scores = IntrinsicMetrics(
            fuzzy_modularity=_compute_fuzzy_modularity(A, np.asarray(U)),
            conductance_bn=_compute_conductance_of_boundary_nodes(A, communities),
        )

    return evaluation_scores


def _compute_modularity(graph: nx.Graph, communities: dict[int, list[int]]) -> float:
    """
    Compute the Modularity score.
    Modularity ranges from _ to _ (typically 0.3-0.7). The higher, the better.

    Parameters:
        graph : (nx.Graph)
            The graph.
        communities : (dict[int, list[int]])
            Dictionary where keys are community labels and values are lists of nodes in that community.

    Returns:
        modularity_score : (float)
            Modularity Q score.
    """

    return modularity(graph, communities.values())


def _compute_conductance(graph: nx.Graph, communities: dict[int, list[int]]) -> float:
    """
    Compute the Conductance score.
    Conductance ranges from _ to _. The lower, the better.

    Parameters:
        graph : (nx.Graph)
            The graph.
        communities : (dict[int, list[int]])
            Dictionary where keys are community labels and values are lists of nodes in that community.

    Returns:
        conductance_score : (float)
            Conductance score (the minimum conductance across all communities).
    """

    if len(communities) == 1:
        return 1.0  # Large value for single community case.

    phis = []
    for S in communities.values():
        phi = conductance(graph, S)
        phis.append(phi)

    return float(np.min(phis))


def _compute_fuzzy_modularity(A: np.ndarray, U: np.ndarray) -> float:
    """
    Compute the Fuzzy Modularity score.

    Formula: Q_fuzzy = 1/2m * Σvw (Avw - kv*kw/2m) (Σk ukv*ukw),
    where Avw is the (v,w)-th element of the adjacency matrix,
    kv = Σw Avw is the degree of node v,
    m = 1/2 * Σvw Avw is the total number of edges in the graph and
    ukv is the membership degree of node v in community k.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.
        U : (np.ndarray, shape [k,n])
            Fuzzy membership per node per community.

    Returns:
        fuzzy_modularity_score : (float)
            Fuzzy Modularity score.
    """

    k = A.sum(axis=1)  # kv
    m2 = k.sum()  # 2m

    if m2 == 0:
        return 0.0

    P = np.outer(k, k) / m2  # kv kw / (2m)
    S = U @ U.T  # Σk ukv*ukw

    return ((A - P) * S).sum() / m2


def _compute_conductance_of_boundary_nodes(A: np.ndarray, communities: dict[int, list[int]]) -> float:
    """
     Compute the Conductance of Boundary Nodes score.

     Formula: ψ(C) = (1/k_in(C)) * Σ_{i in C} (k_in(i) * k_out(i) / k(i)),
     where k_in(C) = Σ_{i in C} k_in(i) is the total internal degree of community C,
     k_in(i) is the number of edges from node i to other nodes in C,
     k_out(i) is the number of edges from node i to nodes outside C and
     k(i) is the degree of node i.

    Parameters:
        A : (np.ndarray, shape[n,n])
            Adjacency matrix.
        communities : (dict[int, list[int]])
            Dictionary where keys are community labels and values are lists of nodes in that community.

    Returns:
        conductance_bn_score : (float)
            Conductance of Boundary Nodes score (the minimum conductance across all communities).
    """

    if len(communities) == 1:
        return 1.0

    degrees = A.sum(axis=1)

    psis = []
    for C in communities.values():
        C_idx = np.asarray(C, dtype=int)

        k_in_C = 0.0
        sum_terms = 0.0
        for i in C_idx:
            ki = degrees[i]
            k_in_i = A[i, C_idx].sum()
            k_out_i = ki - k_in_i

            k_in_C += k_in_i
            sum_terms += (k_in_i * k_out_i) / ki

        psi = (sum_terms / k_in_C) if k_in_C > 0 else 0.0
        psis.append(psi)

    return float(np.min(psis))


def _build_communities_from_labels(
        graph: nx.Graph,
        labels: list[int] | list[list[int]],
        overlapping: bool
) -> dict[int, list[int]]:
    """
    Build communities from labels.

    Parameters:
        graph : (nx.Graph)
            The graph.
        labels : (list[int], length n | list[list[int]], length n)
            Labels to build communities from.
        overlapping : (bool)
            Whether the labels are overlapping.

    Returns:
        communities : (dict[int, list[int]])
            Dictionary where keys are community labels and values are lists of nodes in that community.
    """

    communities_to_nodes = {}
    if not overlapping:
        for node_id, community in zip(list(sorted(graph.nodes())), labels):
            communities_to_nodes.setdefault(int(community), []).append(node_id)
    else:
        for node_id, communities in zip(sorted(graph.nodes()), labels):
            for community in communities:
                communities_to_nodes.setdefault(int(community), []).append(node_id)

    return communities_to_nodes
