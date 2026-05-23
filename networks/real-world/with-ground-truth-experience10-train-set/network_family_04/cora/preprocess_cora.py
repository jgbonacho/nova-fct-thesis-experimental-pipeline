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


def pre_process_cora(
        network: str = "cora",
        content_path: str = "cora.content",
        cites_path: str = "cora.cites"
):
    """
    Pre-process the Cora citation network.

    Parameters:
        network : (str)
            The name of the network.
        content_path : (str)
            The path to the original .content file.
        cites_path : (str)
            The path to the original .cites file.

    Saves:
        A GML file with the graph and original string ground-truth labels.
    """

    gml_exists, gml_path = check_and_get_gml_path(network, ".")
    if gml_exists:
        return

    # Read the .content file.
    paper_ids = []
    paper_to_gt = {}

    with open(content_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) < 2:
                continue

            paper_id = parts[0]
            gt = parts[-1]

            paper_ids.append(paper_id)
            paper_to_gt[paper_id] = gt

    # Map original paper IDs to integer node IDs.
    paper_to_id = {
        paper_id: i
        for i, paper_id in enumerate(paper_ids)
    }

    # Create a simple, undirected, unweighted graph.
    graph = nx.Graph()

    # Add nodes with original string ground-truth labels.
    for paper_id in paper_ids:
        graph.add_node(
            paper_to_id[paper_id],
            gt=str(paper_to_gt[paper_id]),
            original_id=str(paper_id)
        )

    missing_edges = 0
    self_loops = 0

    # Read the .cites file and add citation edges.
    with open(cites_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) < 2:
                continue

            source_paper = parts[0]
            target_paper = parts[1]

            # Ignore edges with papers not present in the .content file.
            if source_paper not in paper_to_id or target_paper not in paper_to_id:
                missing_edges += 1
                continue

            source_id = paper_to_id[source_paper]
            target_id = paper_to_id[target_paper]

            # Ignore self-loops.
            if source_id == target_id:
                self_loops += 1
                continue

            graph.add_edge(source_id, target_id)

    # Save the processed graph as a GML file.
    nx.write_gml(graph, gml_path)


if __name__ == "__main__":
    pre_process_cora()