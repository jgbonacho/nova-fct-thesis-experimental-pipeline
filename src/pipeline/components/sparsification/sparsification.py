from dataclasses import dataclass, field

import networkx as nx
import numpy as np

from pipeline.components.loaders.adjacency_matrix import ensure_square_matrix, ensure_binary_matrix, \
    ensure_symmetric_matrix, ensure_zero_diagonal_matrix


@dataclass
class SparsificationInfo:
    """
    Dataclass for sparsification information.

    Attributes:
        theta : (float | str)
            Sparsification threshold. If sparsification is skipped, this is "-".
        target_average_degree : (float | str)
            Target average degree used by sparsification. If sparsification is skipped, this is "-".
        actual_average_degree : (float)
            Actual average degree after sparsification.
        diff_n : (str)
            A string representing the original number of nodes and the sparsified number of nodes,
            formatted as "N | N_s".
    """

    theta: float = field(metadata={"label": "Theta"})
    target_average_degree: float = field(metadata={"label": "Target Avg Degree"})
    actual_average_degree: float = field(metadata={"label": "Actual Avg Degree"})
    diff_n: str = field(metadata={"label": "N | Sparsified N"})


def apply_global_threshold_sparsification(
        W: np.ndarray,
        ground_truth_labels: list,
        affinity_design_label: str,
        target_average_degree: float = 20.0,
        keep_lcc: bool = True,
) -> tuple[np.ndarray, np.ndarray, nx.Graph, list, int, SparsificationInfo]:
    """
    Sparsify an affinity matrix by retaining the strongest weighted edges needed to obtain an approximate target average degree.
    If enabled, only the largest connected component of the sparsified graph is retained.

    Parameters:
        W : (np.ndarray, shape[n,n])
            Symmetric affinity/similarity matrix.
        ground_truth_labels : (list[int] | list[list[int]] | None, length n)
            Ground-truth labels associated with the original node ordering. If None, no label filtering is applied.
        affinity_design_label : (str)
            The affinity design label.
        target_average_degree : (float, optional)
            Target average degree to approximate after sparsification.
            Default is 20.0.
        keep_lcc : (bool, optional)
            Whether to retain only the largest connected component after sparsification.
            Default is True.

    Returns:
        Ws : (np.ndarray, shape[n_s,n_s])
            Sparsified weighted affinity matrix.
        As : (np.ndarray, shape[n_s,n_s])
            Binary support adjacency matrix induced by Ws.
        graph_s : (nx.Graph)
            Graph induced by As, with nodes relabelled from 0 to n_s-1.
        ground_truth_labels_s : (list[int] | list[list[int]] | None, length n_s)
            Filtered ground-truth labels, if provided.
        k_s : (int | None)
            Number of communities in the filtered ground truth, if available.
        info : (SparsificationInfo)
            Sparsification metadata, including the threshold value, target and actual average degree,
            and the difference between the original number of nodes and the sparsified number of nodes.

    Exceptions:
        ValueError : If W is not square, is not symmetric, has fewer than two nodes,
            has no positive off-diagonal affinities, or if target_average_degree is not positive.
    """

    W = np.asarray(W, dtype=float)
    W = W.copy()
    n = W.shape[0]

    # Skip sparsification for the default affinity, i.e., the binary adjacency matrix.
    if affinity_design_label == "Default":
        Ws = W
        As = (Ws > 0).astype(float)
        graph_s = nx.from_numpy_array(As)
        k_s = _count_ground_truth_communities(ground_truth_labels)
        m_s = graph_s.number_of_edges()
        n_s = graph_s.number_of_nodes()
        actual_average_degree = (2.0 * m_s / n_s) if n_s > 0 else 0.0
        info = SparsificationInfo(
            theta="-",
            target_average_degree="-",
            actual_average_degree=actual_average_degree,
            diff_n=f"{n} | {n_s}",
        )
        return Ws, As, graph_s, ground_truth_labels, k_s, info

    upper_i, upper_j = np.triu_indices(n, k=1)
    upper_values = W[upper_i, upper_j]

    positive_edge_positions = np.flatnonzero(upper_values > 0)
    if positive_edge_positions.size == 0:
        raise ValueError("[ERROR] W has no positive off-diagonal affinities.")

    target_edges = int(round(n * target_average_degree / 2.0))
    target_edges = max(1, min(target_edges, positive_edge_positions.size))

    positive_values = upper_values[positive_edge_positions]

    if target_edges < positive_values.size:
        selected_local = np.argpartition(positive_values, -target_edges)[-target_edges:]
    else:
        selected_local = np.arange(positive_values.size)

    selected_positions = positive_edge_positions[selected_local]
    theta = float(positive_values[selected_local].min())

    Ws = np.zeros_like(W, dtype=float)
    rows = upper_i[selected_positions]
    cols = upper_j[selected_positions]
    Ws[rows, cols] = W[rows, cols]
    Ws[cols, rows] = W[rows, cols]

    support = (Ws > 0).astype(int)
    graph_s = nx.from_numpy_array(support)

    if keep_lcc and not nx.is_connected(graph_s):
        lcc_nodes = sorted(max(nx.connected_components(graph_s), key=len))

        Ws = Ws[np.ix_(lcc_nodes, lcc_nodes)]
        support = support[np.ix_(lcc_nodes, lcc_nodes)]

        graph_s = nx.from_numpy_array(support)

        if ground_truth_labels is not None:
            ground_truth_labels = [ground_truth_labels[i] for i in lcc_nodes]

    As = support.astype(float)

    k_s = _count_ground_truth_communities(ground_truth_labels)

    m_s = graph_s.number_of_edges()
    n_s = graph_s.number_of_nodes()
    actual_average_degree = (2.0 * m_s / n_s) if n_s > 0 else 0.0

    if n_s < 2 or m_s == 0:
        raise ValueError("[ERROR] Sparsified LCC is empty or has no edges.")

    info = SparsificationInfo(
        theta=theta,
        target_average_degree=target_average_degree,
        actual_average_degree=actual_average_degree,
        diff_n=f"{n} | {n_s}",
    )

    ensure_square_matrix(As)
    ensure_binary_matrix(As)
    ensure_symmetric_matrix(As)
    ensure_zero_diagonal_matrix(As)

    ensure_square_matrix(W)
    ensure_symmetric_matrix(W)
    ensure_zero_diagonal_matrix(W)

    return Ws, As, graph_s, ground_truth_labels, k_s, info


def _count_ground_truth_communities(labels: list) -> int:
    """
    Count the number of valid communities in the ground-truth labels.

    Parameters:
        labels : (list[int] | list[list[int]] | None)
            Ground-truth labels. If None, no ground truth is available.

    Returns:
        k : (int | None)
            Number of distinct valid communities. Returns None when labels is None.
    """

    if labels is None:
        return None

    if len(labels) == 0:
        return 0

    if isinstance(labels[0], list):
        return len({
            c
            for node_labels in labels
            for c in node_labels
            if c != -1
        })

    return len({label for label in labels if label != -1})
