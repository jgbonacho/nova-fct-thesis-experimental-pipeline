import unittest

import networkx as nx

from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics import compute_extrinsic_metrics


class Test(unittest.TestCase):

    def test_extrinsic_metrics_for_non_overlapping_ground_truth(self):
        results = compute_extrinsic_metrics(
            graph=None,
            ground_truth_labels=[0, 0, 1, 1],
            predicted_labels=[1, 1, 2, 2],
            k=2,
            k_predicted=2,
            overlapping=False
        )

        self.assertEqual(results.diff_of_k, "2 | 2")
        self.assertEqual(results.relative_error_of_k, 0.0)
        self.assertEqual(results.ami, 1.0)
        self.assertEqual(results.f_measure, 1.0)
        self.assertEqual(results.ari, 1.0)
        self.assertEqual(results.fmi, 1.0)
        self.assertEqual(results.nmi, 1.0)
        self.assertEqual(results.vi, 0.0)

    def test_extrinsic_metrics_for_overlapping_ground_truth(self):
        graph = nx.Graph()
        graph.add_node(0)
        graph.add_node(1)
        graph.add_node(2)
        graph.add_node(3)

        results = compute_extrinsic_metrics(
            graph=graph,
            ground_truth_labels=[[0], [0, 1], [1], [1]],
            predicted_labels=[[1], [1, 2], [2], [2]],
            k=2,
            k_predicted=2,
            overlapping=True
        )

        self.assertEqual(results.diff_of_k, "2 | 2")
        self.assertEqual(results.relative_error_of_k, 0.0)
        self.assertEqual(results.onmi, 1.0)
        self.assertEqual(results.omega, 1.0)


if __name__ == "__main__":
    unittest.main()
