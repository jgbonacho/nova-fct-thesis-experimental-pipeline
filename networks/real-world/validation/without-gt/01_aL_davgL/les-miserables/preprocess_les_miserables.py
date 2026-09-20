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


def pre_process_les_miserables(network: str = "les-miserables"):
    """
    Pre-process Les Miserables.

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
    graph = nx.read_gml(os.path.join(".", "lesmis.gml"), label="label")

    print("\nBefore pre-processing:")
    print(f"n = {graph.number_of_nodes()}")
    print(f"m = {graph.number_of_edges()}")
    print(f"weighted = {nx.is_weighted(graph)}")
    print(f"directed = {graph.is_directed()}")

    
    # Remove weights.
    unweighted_graph = graph.copy()
    for u, v in unweighted_graph.edges():
        unweighted_graph[u][v].pop("value", None)

    print("\nAfter pre-processing:")
    print(f"n = {unweighted_graph.number_of_nodes()}")
    print(f"m = {unweighted_graph.number_of_edges()}")
    print(f"weighted = {nx.is_weighted(unweighted_graph)}")
    print(f"directed = {unweighted_graph.is_directed()}")

    # Save the processed graph as a GML file.
    nx.write_gml(unweighted_graph, gml_path)


if __name__ == "__main__":
    pre_process_les_miserables()
