import os
import networkx as nx


def check_and_get_gml_path(network: str, base_dir: str):
    """
    Check if the GML file for the given network already exists.

    Parameters:
        network : (str)
            The name of the network.
        base_dir : (str)
            The directory where the GML file should be located.

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


def pre_process_primary_school_day_2(
        network: str = "primary-school-day-2",
        gexf_path: str = "sp_school_day2.gexf"
):
    """
    Pre-process the SocioPatterns Primary School Day 2 network.

    Parameters:
        network : (str)
            The name of the network.
        gexf_path : (str)
            The path to the original GEXF file.

    Saves:
        A GML file with the graph and original string ground-truth labels.
    """

    gml_exists, gml_path = check_and_get_gml_path(network, ".")
    if gml_exists:
        return

    # Load the GEXF graph.
    raw_graph = nx.read_gexf(gexf_path)

    print("\nBefore pre-processing:")
    print(f"n = {raw_graph.number_of_nodes()}")
    print(f"m = {raw_graph.number_of_edges()}")
    print(f"weighted = {nx.is_weighted(raw_graph)}")
    print(f"directed = {raw_graph.is_directed()}")


    # Ensure graph is undirected.
    if raw_graph.is_directed():
        raw_graph = raw_graph.to_undirected()

    # Create a simple, unweighted graph.
    graph = nx.Graph()

    # Map original node IDs to new integer IDs.
    node_to_id = {
        node: i
        for i, node in enumerate(raw_graph.nodes())
    }

    # Add nodes with original string ground-truth labels.
    for node, data in raw_graph.nodes(data=True):
        if "classname" in data:
            gt = str(data["classname"])
        else:
            gt = "-1"

        graph.add_node(
            node_to_id[node],
            gt=gt,
            original_id=str(node)
        )

    # Add edges without weights, duration, or count.
    for u, v in raw_graph.edges():
        if u != v:
            graph.add_edge(node_to_id[u], node_to_id[v])

    print("\nAfter pre-processing:")
    print(f"n = {graph.number_of_nodes()}")
    print(f"m = {graph.number_of_edges()}")
    print(f"weighted = {nx.is_weighted(graph)}")
    print(f"directed = {graph.is_directed()}")

    # Save the processed graph as a GML file.
    nx.write_gml(graph, gml_path)


if __name__ == "__main__":
    pre_process_primary_school_day_2()