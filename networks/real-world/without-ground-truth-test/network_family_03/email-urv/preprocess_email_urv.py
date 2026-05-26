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


def _read_email_urv_edge_list(file_path: str) -> nx.Graph:
    """
    Read the Email URV network from an edge-list file.

    The expected format is:
        source target weight

    The third column is ignored because the final graph must be unweighted.

    Parameters:
        file_path : (str)
            The path to the email.txt file.

    Returns:
        graph : (nx.Graph)
            The graph read from the edge list.
    """

    graph = nx.Graph()

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()

            # Ignore empty lines.
            if not line:
                continue

            # Ignore comments.
            if line.startswith("#") or line.startswith("%") or line.startswith("//"):
                continue

            parts = line.split()

            # Each edge must have at least two columns: source and target.
            if len(parts) < 2:
                continue

            source = int(parts[0])
            target = int(parts[1])

            # Ignore self-loops directly.
            if source == target:
                continue

            graph.add_edge(source, target)

    return graph


def pre_process_email_urv(network: str = "email-urv"):
    """
    Pre-process Email URV network.

    Parameters:
        network : (str)
            The name of the network.

    Saves:
        A GML file with an undirected, unweighted simple graph without self-loops.
    """

    gml_exists, gml_path = check_and_get_gml_path(network, ".")
    if gml_exists:
        return

    # Get the graph from the edge-list file.
    graph = _read_email_urv_edge_list(os.path.join(".", "email.txt"))

    # # Save the processed graph as a GML file.
    nx.write_gml(graph, gml_path)


if __name__ == "__main__":
    pre_process_email_urv()