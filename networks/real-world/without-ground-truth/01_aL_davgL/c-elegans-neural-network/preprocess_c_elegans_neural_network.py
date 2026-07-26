import os
from pathlib import Path
import re
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


def add_multigraph_header_if_needed(gml_path: str) -> str:
    """
    Add the multigraph header to a GML file.

    Parameters:
        gml_path : (str)
            The path to the original GML file.

    Returns:
        multigraph_path : (str)
            The path to the GML file with the multigraph header.
    """

    path = Path(gml_path)
    text = path.read_text(encoding="latin-1")

    fixed_text = re.sub(
        r"(?m)^(\s*graph\s*\[\s*)$",
        r"\1\n  multigraph 1",
        text,
        count=1
    )

    multigraph_path = path.with_name(path.stem + "_multigraph.gml")
    multigraph_path.write_text(fixed_text, encoding="latin-1")

    return str(multigraph_path)


def pre_process_c_elegans_neural_network(network: str = "c-elegans-neural-network"):
    """
    Pre-process c elegans neural network.

    Parameters:
        network : (str)
            The name of the network.

    Saves:
        A GML file with an undirected, unweighted simple graph without self-loops.
    """

    gml_exists, gml_path = check_and_get_gml_path(network, ".")
    if gml_exists:
        return
    
    # Get the graph.
    multigraph_path = add_multigraph_header_if_needed(os.path.join(".", "celegansneural.gml"))
    graph_raw = nx.read_gml(multigraph_path, label="id")

    # Preserve original node information before saving again.
    for _, data in graph_raw.nodes(data=True):
        if "label" in data:
            data["original_label"] = data["label"]

    # Remove duplicated and parallel edges.
    graph = nx.Graph()
    graph.add_nodes_from(graph_raw.nodes(data=True))
    graph.add_edges_from(graph_raw.edges())

    # Save the processed graph as a GML file.
    nx.write_gml(graph, gml_path)


if __name__ == "__main__":
    pre_process_c_elegans_neural_network()