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


def _read_net_as_edge_list(file_path: str) -> nx.Graph:
    """
    Read a .net file as an edge list.

    This parser supports simple edge-list .net files and also skips possible Pajek-like header sections such as *Vertices and *Edges.

    Parameters:
        file_path : (str)
            The path to the .net file.

    Returns:
        graph : (nx.Graph)
            The graph read from the edge list.
    """

    graph = nx.Graph()
    reading_edges = True
    inside_vertices_section = False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()

            # Ignore empty lines.
            if not line:
                continue

            # Ignore comments.
            if line.startswith("#") or line.startswith("%") or line.startswith("//"):
                continue

            lower_line = line.lower()

            # Skip Pajek vertex section if it exists.
            if lower_line.startswith("*vertices"):
                inside_vertices_section = True
                reading_edges = False
                continue

            # Start reading edges after Pajek edge/arcs section if it exists.
            if lower_line.startswith("*edges") or lower_line.startswith("*arcs"):
                inside_vertices_section = False
                reading_edges = True
                continue

            # Ignore vertex-definition lines.
            if inside_vertices_section and not reading_edges:
                continue

            parts = line.replace(",", " ").split()

            # Each edge must have at least two columns: source and target.
            if len(parts) < 2:
                continue

            source = parts[0].strip('"')
            target = parts[1].strip('"')

            # Ignore self-loops directly.
            if source == target:
                continue

            graph.add_edge(source, target)

    return graph


def pre_process_jazz_musicians(network: str = "jazz-musicians"):
    """
    Pre-process Jazz musicians network.

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
    graph = _read_net_as_edge_list(os.path.join(".", "jazz.net"))

    # Save the processed graph as a GML file.
    nx.write_gml(graph, gml_path)


if __name__ == "__main__":
    pre_process_jazz_musicians()