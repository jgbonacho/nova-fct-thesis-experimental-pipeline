import os

import networkx as nx
from pipeline.scripts.utils.networks_dataclasses import NetworkConfig


def load_network_from_gml(dir_path: str, network_config: NetworkConfig) -> tuple[nx.Graph, list, int]:
    """
     Load a real-world network from a .gml file, preprocess it, and extract ground-truth labels.

     Parameters:
        dir_path : (str)
            The directory path where the network files are located.
        network_config : (NetworkConfig)
            The configuration of the network to load.

     Returns:
         graph : (nx.Graph)
             The preprocessed graph.
         ground_truth : (list[list[int]], size n | list[int], size n)
             List of ground-truth labels.
         k : (int)
                Number of communities.
    """

    # Load graph from GML file.
    graph = nx.read_gml(
        os.path.join(dir_path, network_config.name, f"{network_config.gml_filename}.gml"),
        label="id"
    )

    # Ensure graph properties.
    _ensure_graph_properties(graph)

    # Extract largest connected component.
    if not nx.is_connected(graph):
        largest_cc = max(nx.connected_components(graph), key=len)
        graph = graph.subgraph(largest_cc).copy()
        print(f"[INFO] Nodes LCC = {graph.number_of_nodes()}; Edges LCC = {graph.number_of_edges()}")

    # Extract ground-truth labels.
    ground_truth_labels, k = None, None
    original_nodes = sorted(graph.nodes())
    if network_config.ground_truth:
        if not network_config.overlapping_ground_truth:
            id_to_label = nx.get_node_attributes(graph, network_config.ground_truth_attr)
            unique_label_values = sorted(set(id_to_label.values()))
            label_value_to_idx = {label: idx for idx, label in enumerate(unique_label_values)}

            # NOTE: Nodes without the ground-truth attribute are labeled as -1.
            ground_truth_labels = [
                label_value_to_idx[id_to_label[node]] if node in id_to_label else -1 for node in original_nodes
            ]
            k = len(unique_label_values)

            print(f"[INFO] K = {k}; Labels-to-IDs = {label_value_to_idx}")
        else:
            id_to_raw_labels = nx.get_node_attributes(graph, network_config.ground_truth_attr)
            id_to_labels = {}
            unique_label_values = set()
            for node_id in original_nodes:
                raw_labels = id_to_raw_labels[node_id]
                if raw_labels != "":
                    labels = [_parse_label(label) for label in raw_labels.split(";")]
                    id_to_labels[node_id] = labels
                    unique_label_values.update(labels)
            unique_label_values = sorted(unique_label_values)
            label_value_to_idx = {label: idx for idx, label in enumerate(unique_label_values)}

            ground_truth_labels = [
                # NOTE: Nodes without the ground-truth attribute are labeled as [-1].
                [label_value_to_idx[label] for label in id_to_labels[node_id]] if node_id in id_to_labels else [-1]
                for node_id in original_nodes
            ]
            k = len(unique_label_values)

            print(f"[INFO] K = {k}; Labels-to-IDs = {label_value_to_idx}")

    # Relabel nodes to ensure they are labeled from 0 to n-1.
    mapping = {node: idx for idx, node in enumerate(original_nodes)}
    graph = nx.relabel_nodes(graph, mapping)

    # Check whether all nodes have ground-truth labels.
    _check_nodes_without_communities(ground_truth_labels, network_config)

    return graph, ground_truth_labels, k


def _ensure_graph_properties(graph: nx.Graph):
    """
    Validate that a graph satisfies the required structural properties.

    Parameters:
        graph : (nx.Graph)
            Graph to validate.

    Returns:
        None

    Exceptions:
        ValueError : If the graph contains parallel edges, is directed, is weighted, or contains self-loops.
    """

    # Ensure graph is simple, i.e., it has no parallel edges.
    if graph.is_multigraph():
        raise ValueError("[ERROR] Only simple graphs are supported. Parallel edges are not allowed.")

    # Ensure graph is undirected.
    if graph.is_directed():
        raise ValueError("[ERROR] Only undirected graphs are supported.")

    # Ensure graph is unweighted.
    if nx.get_edge_attributes(graph, "weight") or nx.get_edge_attributes(graph, "value"):
        raise ValueError("[ERROR] Only unweighted graphs are supported.")

    # Ensure graph has no self-loops.
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError(f"[ERROR] Only graphs without self-loops are supported.")

    print(
        f"[INFO] Nodes = {graph.number_of_nodes()}; "
        f"Edges = {graph.number_of_edges()}; "
        f"CCs = {nx.number_connected_components(graph)}"
    )


def _parse_label(label: str):
    """
    Parse a ground-truth label.

    Parameters:
        label : (str)
            The label to parse.

    Returns:
        label : (int | str)
            The label converted to int if possible, otherwise kept as string.
    """

    try:
        return int(label)
    except ValueError:
        return label


def _check_nodes_without_communities(ground_truth_labels: list, network_config: NetworkConfig):
    """
    Check and print the number of nodes without ground-truth community labels.

    Parameters:
        ground_truth_labels : (list | None)
            Ground-truth community labels for each node.
        network_config : (NetworkConfig)
            Configuration of the real-world network.

    Returns:
        None
    """

    if ground_truth_labels is not None:
        if not network_config.overlapping_ground_truth:
            missing_labels = ground_truth_labels.count(-1)
        else:
            missing_labels = ground_truth_labels.count([-1])
        if missing_labels > 0:
            print(f"[INFO] Nodes without ground-truth labels = {missing_labels}")
