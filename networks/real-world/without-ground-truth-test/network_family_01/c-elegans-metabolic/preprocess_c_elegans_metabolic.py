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


def pre_process_celegans_metabolic(network: str = "c-elegans-metabolic"):
    """
    Pre-process C. elegans metabolic network.

    Parameters:
        network : (str)
            The name of the network.

    Saves:
        A GML file with an undirected, unweighted simple graph without self-loops.
    """

    gml_exists, gml_path = check_and_get_gml_path(network, ".")
    if gml_exists:
        return

    # Get the graph from Pajek .net format.
    graph = nx.read_pajek(os.path.join(".", "celegans_metabolic.net"))

    # Ensure graph is simple, i.e., remove possible parallel edges.
    graph = nx.Graph(graph)

    # Remove self-loops.
    graph.remove_edges_from(nx.selfloop_edges(graph))

    # Remove weights.
    unweighted_graph = graph.copy()
    for u, v in unweighted_graph.edges():
        unweighted_graph[u][v].pop("weight", None)

    # Save the processed graph as a GML file.
    nx.write_gml(unweighted_graph, gml_path)


if __name__ == "__main__":
    pre_process_celegans_metabolic()