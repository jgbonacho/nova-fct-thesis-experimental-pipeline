import unittest
from types import SimpleNamespace
from unittest.mock import patch

import networkx as nx

import pipeline.baselines.non_spectral.cfinder as cfinder_module
from pipeline.baselines.non_spectral.cfinder import _communities_to_labels, cfinder


class TestCFinder(unittest.TestCase):

    def test_communities_to_labels(self):
        graph = nx.path_graph(5)
        communities = [
            [0, 1, 2],
            [2, 3]
        ]

        predicted_labels, k_predicted = _communities_to_labels(
            communities=communities,
            graph=graph
        )

        self.assertEqual(
            predicted_labels,
            [[0], [0], [0, 1], [1], [1]]
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
            communities=[["0", "2", "5", "-1"]],
            graph=graph
        )

        self.assertEqual(
            predicted_labels,
            [[0], [0], [0], [0]]
        )
        self.assertEqual(k_predicted, 1)

    def test_cfinder_calls_kclique_and_converts_communities(self):
        graph = nx.path_graph(5)

        with patch.object(
                cfinder_module.algorithms,
                "kclique",
                return_value=SimpleNamespace(
                    communities=[[0, 1, 2], [2, 3]]
                )
        ) as mocked_kclique:
            predicted_labels, k_predicted = cfinder(
                graph=graph,
                clique_size=3
            )

        mocked_kclique.assert_called_once_with(
            graph,
            k=3
        )
        self.assertEqual(
            predicted_labels,
            [[0], [0], [0, 1], [1], [1]]
        )
        self.assertEqual(k_predicted, 2)


if __name__ == "__main__":
    unittest.main()
