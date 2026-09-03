import os
import networkx as nx


def check_and_get_gml_path(network: str, base_dir: str):
    """
    Check if the GML file for the given network already exists.

    Parameters:
        network : (str)
            The name of the network.
        base_dir : (str)
            The base directory where the GML file should be located.

    Returns:
        exists : (bool)
            True if the GML file exists, False otherwise.
        gml_path : (str)
            The path to the GML file.
    """

    gml_path = os.path.join(base_dir, f"{network}.gml")
    if os.path.exists(gml_path):
        print(f"[INFO] {network}.gml already exists. Skipping generation.")
        return True, gml_path
    else:
        return False, gml_path


def pre_process_email_eu_core(network: str = "email-eu-core"):
    """
    Pre-process Email EU core.

    Parameters:
        network : (str)
            The name of the network.

    Saves:
        A GML file with the graph and ground truth labels.
    """

    gml_exists, gml_path = check_and_get_gml_path(network, ".")
    if gml_exists:
        return

    # Get the graph.
    edge_file = os.path.join(".", "email-Eu-core.txt")
    label_file = os.path.join(".", "email-Eu-core-department-labels.txt")
    graph = nx.read_edgelist(edge_file, nodetype=int, create_using=nx.DiGraph())

    print("\nBefore pre-processing:")
    print(f"n = {graph.number_of_nodes()}")
    print(f"m = {graph.number_of_edges()}")
    print(f"weighted = {nx.is_weighted(graph)}")
    print(f"directed = {graph.is_directed()}")

    # Ensure graph is undirected.
    graph = graph.to_undirected()

    # Remove self-loop edges.
    graph.remove_edges_from(list(nx.selfloop_edges(graph)))

    # Add ground-truth.
    labels = {}
    with open(label_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            u, dept = map(int, line.split())
            labels[u] = int(dept)
            if u not in graph:
                graph.add_node(u)
    value_attr = {n: labels[n] for n in graph.nodes()}
    nx.set_node_attributes(graph, value_attr, name="value")

    print("\nAfter pre-processing:")
    print(f"n = {graph.number_of_nodes()}")
    print(f"m = {graph.number_of_edges()}")
    print(f"weighted = {nx.is_weighted(graph)}")
    print(f"directed = {graph.is_directed()}")

    # Save the processed graph as a GML file.
    nx.write_gml(graph, gml_path)


if __name__ == "__main__":
    pre_process_email_eu_core()
