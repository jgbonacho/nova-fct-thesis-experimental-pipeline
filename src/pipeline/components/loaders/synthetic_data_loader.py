import os

import networkx as nx


def load_lfr_benchmark_network(
        dir_path: str,
        filename: str,
        overlapping_ground_truth: bool = True
) -> tuple[nx.Graph, list, int]:
    """
     Load a LFR benchmark network, preprocess it, and extract ground-truth labels.

     Parameters:
            dir_path : (str)
                The directory path where the network files are located.
            filename : (str)
                The name of the network files .nse and .nmc (without extension).
            overlapping_ground_truth : (bool, optional)
                Whether nodes can belong to multiple communities in the ground-truth labels.
                Default is True.

     Returns:
         graph : (nx.Graph)
             The preprocessed graph.
         ground_truth : (list[list[int]], size n | list[int], size n)
             List of ground-truth labels.
         k : (int)
                Number of communities.
    """

    # Load an undirected, unweighted simple graph without self-loops.
    graph = _read_edges_nse(os.path.join(dir_path, f"{filename}.nse"))
    memberships = _read_memberships_nmc(os.path.join(dir_path, f"{filename}.nmc"), overlapping_ground_truth)

    # Extract largest connected component.
    if not nx.is_connected(graph):
        largest_cc = max(nx.connected_components(graph), key=len)
        graph = graph.subgraph(largest_cc).copy()
        print(f"[INFO] Extracted LCC with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")

    # Extract ground-truth labels.
    original_nodes = sorted(graph.nodes())
    if not overlapping_ground_truth:
        ground_truth_labels = [memberships[node_id] - 1 for node_id in original_nodes]
        k = len(set(ground_truth_labels))
    else:
        ground_truth_labels = [[label - 1 for label in memberships[node_id]] for node_id in original_nodes]
        k = len({label for labels in ground_truth_labels for label in labels})

    # Relabel nodes to ensure they are labeled from 0 to n-1.
    mapping = {node: idx for idx, node in enumerate(original_nodes)}
    graph = nx.relabel_nodes(graph, mapping)

    # Check whether all nodes have ground-truth labels.
    if graph.number_of_nodes() != len(ground_truth_labels):
        number_of_nodes_without_ground_truth = graph.number_of_nodes() - len(ground_truth_labels)
        print(f"[INFO] There are {number_of_nodes_without_ground_truth} nodes without ground-truth labels.")

    return graph, ground_truth_labels, k


def _read_edges_nse(nse_path: str) -> nx.Graph:
    """
    Read edges from an NSE file and construct an undirected, unweighted simple graph without self-loops.

    Parameters:
        nse_path : (str)
            Path to the NSE file.

    Returns:
        graph : (nx.Graph)
            The constructed undirected, unweighted simple graph without self-loops.
    """

    graph = nx.Graph()
    with open(nse_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            u, v = int(parts[0]), int(parts[1])
            if u == v:
                continue
            graph.add_edge(u, v)

    return graph.to_undirected()


def _read_memberships_nmc(nmc_path: str, overlapping_ground_truth: bool) -> dict:
    """
    Read node memberships from an NMC file.

    Parameters:
        nmc_path : (str)
            Path to the NMC file.
        overlapping_ground_truth : (bool)
            Whether nodes can belong to multiple communities in the ground-truth labels.

    Returns:
        node_to_ground_truth_labels : (dict[int, int] | dict[int, list[int]])
            Mapping from node to its ground-truth labels.
    """

    node_to_ground_truth_labels = {}
    with open(nmc_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            node = int(parts[0])
            labels = [int(l) for l in parts[1:]]
            node_to_ground_truth_labels[node] = labels if overlapping_ground_truth else labels[0]

    return node_to_ground_truth_labels
