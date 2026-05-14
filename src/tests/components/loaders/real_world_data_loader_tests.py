import os
import unittest

from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix
from pipeline.components.loaders.real_world_data_loader import load_network_from_gml
from pipeline.scripts.utils.networks_dataclasses import NetworkConfig


class Test(unittest.TestCase):

    def test_load_real_world_network_with_non_overlapping_ground_truth(self):
        dir_name = "zachary-karate-club"
        filename = "zachary-karate-club"

        graph, ground_truth_labels, k = load_network_from_gml(
            dir_path=os.path.join(os.path.dirname(__file__)),
            network_config=NetworkConfig(
                name="zachary-karate-club",
                gml_filename="zachary-karate-club",
                ground_truth=True,
                overlapping_ground_truth=False,
                ground_truth_attr="club"
            )
        )

        print(sorted(graph.nodes(data=True)))
        print(ground_truth_labels)
        print(k)

        A = compute_adjacency_matrix(graph)
        with open(os.path.join(os.path.dirname(__file__), dir_name, f"A_{filename}.csv"), "w") as f:
            for row in A:
                f.write(",".join(map(str, row)) + "\n")

        self.assertEqual(len(ground_truth_labels), graph.number_of_nodes())
        self.assertEqual(len(set(ground_truth_labels)), k)

    def test_load_real_world_network_with_overlapping_ground_truth(self):
        dir_name = "facebook-network-ego698"
        filename = "facebook-network-ego698"

        graph, ground_truth_labels, k = load_network_from_gml(
            dir_path=os.path.join(os.path.dirname(__file__)),
            network_config=NetworkConfig(
                name="facebook-network-ego698",
                gml_filename="facebook-network-ego698",
                ground_truth=True,
                overlapping_ground_truth=True,
                ground_truth_attr="circles"
            )
        )

        print(sorted(graph.nodes(data=True)))
        print(ground_truth_labels)
        print(k)

        A = compute_adjacency_matrix(graph)
        with open(os.path.join(os.path.dirname(__file__), dir_name, f"A_{filename}.csv"), "w") as f:
            for row in A:
                f.write(",".join(map(str, row)) + "\n")

        self.assertEqual(len(ground_truth_labels), graph.number_of_nodes())
        # -1 because the label '-1' represents no-community.
        self.assertEqual(len({label for labels in ground_truth_labels for label in labels}) - 1, k)


if __name__ == "__main__":
    unittest.main()
