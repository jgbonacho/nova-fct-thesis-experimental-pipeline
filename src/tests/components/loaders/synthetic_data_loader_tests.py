import os
import unittest

from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix
from pipeline.components.loaders.synthetic_data_loader import load_lfr_benchmark_network


class Test(unittest.TestCase):

    def test_load_lfr_network_with_non_overlapping_ground_truth(self):
        dir_name = "network1"
        filename = "n50mu0.1on0om0inst1"
        graph, ground_truth_labels, k = load_lfr_benchmark_network(
            dir_path=os.path.join(os.path.dirname(__file__), dir_name),
            filename=filename,
            overlapping_ground_truth=False
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

    def test_load_lfr_network_with_overlapping_ground_truth(self):
        dir_name = "network2"
        filename = "n50mu0.1on5om2inst1"
        graph, ground_truth_labels, k = load_lfr_benchmark_network(
            dir_path=os.path.join(os.path.dirname(__file__), dir_name),
            filename=filename,
            overlapping_ground_truth=True
        )

        print(sorted(graph.nodes(data=True)))
        print(ground_truth_labels)
        print(k)

        A = compute_adjacency_matrix(graph)
        with open(os.path.join(os.path.dirname(__file__), dir_name, f"A_{filename}.csv"), "w") as f:
            for row in A:
                f.write(",".join(map(str, row)) + "\n")

        self.assertEqual(len(ground_truth_labels), graph.number_of_nodes())
        self.assertEqual(len({label for labels in ground_truth_labels for label in labels}), k)


if __name__ == "__main__":
    unittest.main()
