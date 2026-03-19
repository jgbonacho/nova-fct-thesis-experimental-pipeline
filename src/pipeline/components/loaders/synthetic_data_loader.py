import os

import networkx as nx


def load_lfr_benchmark_network(dir_path, filename, overlapping_ground_truth=True):
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
         graph : (networkx.Graph)
             The preprocessed graph.
         ground_truth : (list[list[int]], size n) or (list[int], size n)
             List of ground-truth labels.
         k : (int)
                Number of communities.
    """

    # Load graph.
    graph_raw = _read_edges_nse(os.path.join(dir_path, f"{filename}.nse"))
    memberships = _read_memberships_nmc(os.path.join(dir_path, f"{filename}.nmc"), overlapping_ground_truth)

    # Ensure graph is undirected.
    if graph_raw.is_directed():
        raise ValueError("[ERROR] Only undirected graphs are supported.")
    graph = graph_raw.to_undirected()

    # Ensure graph is unweighted.
    if nx.get_edge_attributes(graph, "weight") or nx.get_edge_attributes(graph, "value"):
        raise ValueError("[ERROR] Only unweighted graphs are supported.")

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

    return graph, ground_truth_labels, k


def _read_edges_nse(nse_path):
    """
    Read edges from an NSE file and construct a graph.

    Parameters:
        nse_path : (str)
            Path to the NSE file.

    Returns:
        graph : (networkx.Graph)
            The constructed undirected graph.
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

    return graph


def _read_memberships_nmc(nmc_path, overlapping_ground_truth):
    """
    Read node memberships from an NMC file.

    Parameters:
        nmc_path : (str)
            Path to the NMC file.
        overlapping_ground_truth : (bool)
            Whether nodes can belong to multiple communities in the ground-truth labels.

    Returns:
        node_to_ground_truth_labels : (dict)
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
