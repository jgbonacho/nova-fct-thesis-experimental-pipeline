import unittest
from types import SimpleNamespace
from unittest.mock import patch

import networkx as nx

import pipeline.baselines.non_spectral.slpa as slpa_module
from pipeline.baselines.non_spectral.slpa import _communities_to_labels, slpa


class TestSLPA(unittest.TestCase):

    def test_communities_to_labels(self):
        graph = nx.path_graph(5)
        communities = [
            [0, 1, 2],
            [1, 3]
        ]

        predicted_labels, k_predicted = _communities_to_labels(
            communities=communities,
            graph=graph
        )

        self.assertEqual(
            predicted_labels,
            [[0], [0, 1], [0], [1], [1]]
        )
        self.assertEqual(k_predicted, 2)

    def test_empty_communities(self):
        graph = nx.empty_graph(0)

        predicted_labels, k_predicted = _communities_to_labels(
            communities=[],
            graph=graph
        )

        self.assertEqual(predicted_labels, [])
        self.assertEqual(k_predicted, 0)

    def test_nodes_without_communities_are_assigned_by_neighbors(self):
        graph = nx.Graph()
        graph.add_nodes_from(range(6))
        graph.add_edges_from([
            (0, 4),
            (1, 4),
            (2, 5),
            (3, 5)
        ])

        predicted_labels, k_predicted = _communities_to_labels(
            communities=[[0, 1], [2, 3]],
            graph=graph
        )

        self.assertEqual(
            predicted_labels,
            [[0], [0], [1], [1], [0], [1]]
        )
        self.assertEqual(k_predicted, 2)

    def test_invalid_node_identifiers_are_ignored(self):
        graph = nx.path_graph(4)

        predicted_labels, k_predicted = _communities_to_labels(
            communities=[["1", "3", "8", "-2"]],
            graph=graph
        )

        self.assertEqual(
            predicted_labels,
            [[0], [0], [0], [0]]
        )
        self.assertEqual(k_predicted, 1)

    def test_slpa_sets_seeds_calls_algorithm_and_converts_communities(self):
        graph = nx.path_graph(5)

        with (
            patch.object(slpa_module.random, "seed") as mocked_random_seed,
            patch.object(slpa_module.np.random, "seed") as mocked_numpy_seed,
            patch.object(
                slpa_module.algorithms,
                "slpa",
                return_value=SimpleNamespace(
                    communities=[[0, 1, 2], [2, 3]]
                )
            ) as mocked_slpa
        ):
            predicted_labels, k_predicted = slpa(
                graph=graph,
                t=100,
                r=0.45,
                seed=7
            )

        mocked_random_seed.assert_called_once_with(7)
        mocked_numpy_seed.assert_called_once_with(7)
        mocked_slpa.assert_called_once_with(
            graph,
            t=100,
            r=0.45
        )
        self.assertEqual(
            predicted_labels,
            [[0], [0], [0, 1], [1], [1]]
        )
        self.assertEqual(k_predicted, 2)


if __name__ == "__main__":
    unittest.main()
