import os
import re
import json

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


def pre_process_facebook_ego_network(ego_id: int):
    """
    Pre-process Facebook Ego Network.

    Parameters:
        network : (str)
            The name of the network.
        ego_id : (int)
            The id of the ego network.

    Saves:
        A GML file with the graph and ground truth labels.
    """
    
    gml_exists, gml_path = check_and_get_gml_path(f"facebook-network-ego{EGO_NETWORK}", ".")
    if gml_exists:
        return

    # Get the graph.
    graph = nx.read_edgelist(os.path.join(".", f"{ego_id}.edges"), nodetype=int, create_using=nx.Graph())

    # Add ground-truth.
    circles = {}
    with open(os.path.join(".", f"{ego_id}.circles"), "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            match = re.match(r"^([^:\s]+)[:\s]+(.*)$", line)
            if not match:
                continue

            circle_name = match.group(1)
            node_ids_str = match.group(2)
            circle_id = int(circle_name.removeprefix("circle"))
            node_ids = [
                int(node_id)
                for node_id in re.split(r"\s+", node_ids_str.strip())
                if node_id
            ]

            circles[circle_id] = set(node_ids)

    for node in graph.nodes():
        ground_truth_labels = [
            circle_id
            for circle_id, node_set in circles.items()
            if node in node_set
        ]

        graph.nodes[node]["circles"] = ";".join(map(str, ground_truth_labels))

    # Save the processed graph as a GML file.
    nx.write_gml(graph, gml_path)


if __name__ == "__main__":
    EGO_NETWORK=348
    pre_process_facebook_ego_network(EGO_NETWORK)
