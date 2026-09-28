import unittest
from dataclasses import fields
from unittest.mock import patch

import networkx as nx
import numpy as np

from pipeline.components.evaluation_metrics.intrinsic import intrinsic_metrics as metrics_module
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import IntrinsicMetrics


class TestIntrinsicMetrics(unittest.TestCase):

    def test_compute_non_overlapping_intrinsic_metrics(self):
        graph = nx.path_graph(4)
        A = nx.to_numpy_array(graph)
        U = np.array(
            [
                [1.0, 0.0],
                [1.0, 0.0],
                [0.0, 1.0],
                [0.0, 1.0]
            ]
        )

        metrics = metrics_module.compute_intrinsic_metrics(
            graph=graph,
            A=A,
            U=U,
            predicted_labels=[0, 0, 1, 1],
            overlapping=False
        )

        self.assertIsInstance(metrics, IntrinsicMetrics)
        self.assertAlmostEqual(metrics.modularity, 1.0 / 6.0)
        self.assertAlmostEqual(metrics.conductance, 1.0 / 3.0)
        self.assertIsNone(metrics.fuzzy_modularity)
        self.assertIsNone(metrics.conductance_bn)

    def test_compute_overlapping_intrinsic_metrics(self):
        graph = nx.path_graph(4)
        A = nx.to_numpy_array(graph)
        U = np.array(
            [
                [1.0, 0.0],
                [1.0, 0.0],
                [0.0, 1.0],
                [0.0, 1.0]
            ]
        )

        metrics = metrics_module.compute_intrinsic_metrics(
            graph=graph,
            A=A,
            U=U,
            predicted_labels=[[0], [0], [1], [1]],
            overlapping=True
        )

        self.assertIsNone(metrics.modularity)
        self.assertIsNone(metrics.conductance)
        self.assertAlmostEqual(metrics.fuzzy_modularity, 1.0 / 6.0)
        self.assertAlmostEqual(metrics.conductance_bn, 0.25)

    def test_compute_modularity(self):
        graph = nx.complete_graph(3)
        communities = {
            0: [0, 1],
            1: [2]
        }

        score = metrics_module._compute_modularity(
            graph,
            communities
        )

        self.assertAlmostEqual(score, -2.0 / 9.0)

    def test_compute_conductance_returns_minimum_community_score(self):
        graph = nx.path_graph(5)
        communities = {
            0: [0, 1],
            1: [2],
            2: [3, 4]
        }

        score = metrics_module._compute_conductance(
            graph,
            communities
        )

        expected = min(
            nx.conductance(graph, community)
            for community in communities.values()
        )
        self.assertAlmostEqual(score, expected)

    def test_compute_conductance_for_single_community(self):
        score = metrics_module._compute_conductance(
            nx.path_graph(3),
            {0: [0, 1, 2]}
        )

        self.assertEqual(score, 1.0)

    def test_compute_fuzzy_modularity_for_graph_without_edges(self):
        A = np.zeros((3, 3), dtype=np.float64)
        U = np.array(
            [
                [1.0, 0.0],
                [0.5, 0.5],
                [0.0, 1.0]
            ]
        )

        score = metrics_module._compute_fuzzy_modularity(A, U)

        self.assertEqual(score, 0.0)

    def test_compute_fuzzy_modularity_matches_direct_formula(self):
        graph = nx.path_graph(4)
        A = nx.to_numpy_array(graph)
        U = np.array(
            [
                [1.0, 0.0],
                [0.8, 0.2],
                [0.2, 0.8],
                [0.0, 1.0]
            ]
        )

        degrees = A.sum(axis=1)
        twice_edges = degrees.sum()
        expected = (
                           (
                                   A - np.outer(degrees, degrees) / twice_edges
                           )
                           * (U @ U.T)
                   ).sum() / twice_edges

        score = metrics_module._compute_fuzzy_modularity(A, U)

        self.assertAlmostEqual(score, expected)

    def test_compute_boundary_node_conductance(self):
        graph = nx.path_graph(4)
        A = nx.to_numpy_array(graph)
        communities = {
            0: [0, 1],
            1: [2, 3]
        }

        score = metrics_module._compute_conductance_of_boundary_nodes(
            A,
            communities
        )

        self.assertAlmostEqual(score, 0.25)

    def test_compute_boundary_node_conductance_for_single_community(self):
        graph = nx.path_graph(3)
        A = nx.to_numpy_array(graph)

        score = metrics_module._compute_conductance_of_boundary_nodes(
            A,
            {0: [0, 1, 2]}
        )

        self.assertEqual(score, 1.0)

    def test_build_non_overlapping_communities_from_sorted_nodes(self):
        graph = nx.Graph()
        graph.add_nodes_from([20, 10, 30])
        graph.add_edges_from([(10, 20), (20, 30)])

        communities = metrics_module._build_communities_from_labels(
            graph=graph,
            labels=[1, 0, 1],
            overlapping=False
        )

        self.assertEqual(
            communities,
            {
                1: [10, 30],
                0: [20]
            }
        )

    def test_build_overlapping_communities(self):
        graph = nx.path_graph(3)

        communities = metrics_module._build_communities_from_labels(
            graph=graph,
            labels=[[0, 1], [1], [0, 2]],
            overlapping=True
        )

        self.assertEqual(
            communities,
            {
                0: [0, 2],
                1: [0, 1],
                2: [2]
            }
        )

    def test_intrinsic_metrics_defaults_and_metadata(self):
        metrics = IntrinsicMetrics()

        self.assertIsNone(metrics.modularity)
        self.assertIsNone(metrics.conductance)
        self.assertIsNone(metrics.fuzzy_modularity)
        self.assertIsNone(metrics.conductance_bn)
        self.assertEqual(
            [
                dataclass_field.metadata["label"]
                for dataclass_field in fields(IntrinsicMetrics)
            ],
            [
                "Modularity",
                "Conductance",
                "Fuzzy-Modularity",
                "Conductance-BN"
            ]
        )

    def test_compute_intrinsic_metrics_means_and_stds(self):
        graph = nx.path_graph(3)
        A = nx.to_numpy_array(graph)

        U_results = [
            np.array(
                [[0.8, 0.2],
                 [0.5, 0.5],
                 [0.2, 0.8]]
            ),
            np.array(
                [[0.7, 0.3],
                 [0.4, 0.6],
                 [0.1, 0.9]]
            ),
            np.array(
                [[0.9, 0.1],
                 [0.6, 0.4],
                 [0.3, 0.7]]
            )
        ]
        predicted_labels_results = [
            [[0], [0, 1], [1]],
            [[0], [1], [1]],
            [[0], [0], [1]]
        ]

        execution_results = [
            IntrinsicMetrics(
                modularity=0.0,
                conductance=0.25,
                fuzzy_modularity=None,
                conductance_bn=0.0
            ),
            IntrinsicMetrics(
                modularity=0.5,
                conductance=None,
                fuzzy_modularity=None,
                conductance_bn=0.5
            ),
            IntrinsicMetrics(
                modularity=1.0,
                conductance=float("nan"),
                fuzzy_modularity=float("inf"),
                conductance_bn=1.0
            )
        ]

        with patch.object(
                metrics_module,
                "compute_intrinsic_metrics",
                side_effect=execution_results
        ) as mocked_compute_intrinsic_metrics:
            metrics = metrics_module.compute_intrinsic_metrics_means_and_stds(
                graph=graph,
                A=A,
                U_results=U_results,
                predicted_labels_results=predicted_labels_results,
                overlapping=True
            )

        self.assertEqual(
            mocked_compute_intrinsic_metrics.call_count,
            3
        )

        for execution_index, mocked_call in enumerate(
                mocked_compute_intrinsic_metrics.call_args_list
        ):
            call_kwargs = mocked_call.kwargs

            self.assertIs(call_kwargs["graph"], graph)
            np.testing.assert_array_equal(
                call_kwargs["A"],
                A
            )
            np.testing.assert_array_equal(
                call_kwargs["U"],
                U_results[execution_index]
            )
            self.assertEqual(
                call_kwargs["predicted_labels"],
                predicted_labels_results[execution_index]
            )
            self.assertTrue(call_kwargs["overlapping"])

        self.assertEqual(
            metrics.modularity,
            "0.5 ± 0.5"
        )
        self.assertEqual(
            metrics.conductance,
            "0.25 ± 0.0"
        )
        self.assertIsNone(metrics.fuzzy_modularity)
        self.assertEqual(
            metrics.conductance_bn,
            "0.5 ± 0.5"
        )


if __name__ == "__main__":
    unittest.main()
