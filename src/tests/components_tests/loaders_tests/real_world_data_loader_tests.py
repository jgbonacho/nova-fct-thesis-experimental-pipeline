import os
import unittest
from unittest.mock import patch

import networkx as nx
from pipeline.components.loaders import real_world_data_loader as loader_module
from pipeline.scripts.utils.networks_dataclasses import NetworkConfig


class TestRealWorldDataLoader(unittest.TestCase):

    def test_load_real_world_network_with_non_overlapping_ground_truth(self):
        graph, ground_truth_labels, k = loader_module.load_network_from_gml(
            dir_path=os.path.dirname(__file__),
            network_config=NetworkConfig(
                name="zachary-karate-club",
                gml_filename="zachary-karate-club",
                ground_truth=True,
                overlapping_ground_truth=False,
                ground_truth_attr="club"
            )
        )

        valid_labels = {label for label in ground_truth_labels if label != -1}

        self.assertEqual(sorted(graph.nodes()), list(range(graph.number_of_nodes())))
        self.assertTrue(nx.is_connected(graph))
        self.assertFalse(graph.is_directed())
        self.assertFalse(graph.is_multigraph())
        self.assertEqual(nx.number_of_selfloops(graph), 0)
        self.assertEqual(len(ground_truth_labels), graph.number_of_nodes())
        self.assertEqual(len(valid_labels), k)

    def test_load_real_world_network_with_overlapping_ground_truth(self):
        graph, ground_truth_labels, k = loader_module.load_network_from_gml(
            dir_path=os.path.dirname(__file__),
            network_config=NetworkConfig(
                name="facebook-network-ego698",
                gml_filename="facebook-network-ego698",
                ground_truth=True,
                overlapping_ground_truth=True,
                ground_truth_attr="circles"
            )
        )

        valid_labels = {
            label
            for labels in ground_truth_labels
            for label in labels
            if label != -1
        }

        self.assertEqual(sorted(graph.nodes()), list(range(graph.number_of_nodes())))
        self.assertTrue(nx.is_connected(graph))
        self.assertFalse(graph.is_directed())
        self.assertFalse(graph.is_multigraph())
        self.assertEqual(nx.number_of_selfloops(graph), 0)
        self.assertEqual(len(ground_truth_labels), graph.number_of_nodes())
        self.assertTrue(all(isinstance(labels, list) for labels in ground_truth_labels))
        self.assertEqual(len(valid_labels), k)

    @patch.object(loader_module.nx, "read_gml")
    def test_load_network_without_ground_truth(self, mocked_read_gml):
        mocked_read_gml.return_value = nx.Graph([(10, 20), (20, 30)])

        graph, ground_truth_labels, k = loader_module.load_network_from_gml(
            dir_path="base-directory",
            network_config=NetworkConfig(
                name="network",
                gml_filename="network-file",
                ground_truth=False,
                overlapping_ground_truth=None,
                ground_truth_attr=None
            )
        )

        mocked_read_gml.assert_called_once_with(
            os.path.join(
                "base-directory",
                "network",
                "network-file.gml"
            ),
            label="id"
        )
        self.assertEqual(sorted(graph.nodes()), [0, 1, 2])
        self.assertEqual(set(graph.edges()), {(0, 1), (1, 2)})
        self.assertIsNone(ground_truth_labels)
        self.assertIsNone(k)

    @patch.object(loader_module.nx, "read_gml")
    @patch("builtins.print")
    def test_extracts_largest_connected_component_and_non_overlapping_labels(
            self,
            mocked_print,
            mocked_read_gml
    ):
        graph = nx.Graph()
        graph.add_nodes_from(
            [
                (10, {"community": "B"}),
                (20, {"community": "A"}),
                (30, {}),
                (100, {"community": "C"}),
                (110, {"community": "C"})
            ]
        )
        graph.add_edges_from(
            [
                (10, 20),
                (20, 30),
                (100, 110)
            ]
        )
        mocked_read_gml.return_value = graph

        loaded_graph, ground_truth_labels, k = loader_module.load_network_from_gml(
            dir_path="base-directory",
            network_config=NetworkConfig(
                name="network",
                gml_filename="network",
                ground_truth=True,
                overlapping_ground_truth=False,
                ground_truth_attr="community"
            )
        )

        self.assertEqual(sorted(loaded_graph.nodes()), [0, 1, 2])
        self.assertEqual(set(loaded_graph.edges()), {(0, 1), (1, 2)})
        self.assertEqual(ground_truth_labels, [1, 0, -1])
        self.assertEqual(k, 2)
        mocked_print.assert_any_call("[INFO] Nodes LCC = 3; Edges LCC = 2")
        mocked_print.assert_any_call("[INFO] Nodes without ground-truth labels = 1")

    @patch.object(loader_module.nx, "read_gml")
    def test_extracts_overlapping_ground_truth_labels(self, mocked_read_gml):
        graph = nx.Graph()
        graph.add_nodes_from(
            [
                (10, {"circles": "3;1"}),
                (20, {"circles": "3"}),
                (30, {"circles": ""})
            ]
        )
        graph.add_edges_from([(10, 20), (20, 30)])
        mocked_read_gml.return_value = graph

        loaded_graph, ground_truth_labels, k = loader_module.load_network_from_gml(
            dir_path="base-directory",
            network_config=NetworkConfig(
                name="network",
                gml_filename="network",
                ground_truth=True,
                overlapping_ground_truth=True,
                ground_truth_attr="circles"
            )
        )

        self.assertEqual(sorted(loaded_graph.nodes()), [0, 1, 2])
        self.assertEqual(ground_truth_labels, [[1, 0], [1], [-1]])
        self.assertEqual(k, 2)

    def test_ensure_graph_properties_accepts_valid_graph(self):
        graph = nx.Graph([(0, 1), (1, 2)])

        with patch("builtins.print") as mocked_print:
            result = loader_module._ensure_graph_properties(graph)

        self.assertIsNone(result)
        mocked_print.assert_called_once_with(
            "[INFO] Nodes = 3; Edges = 2; CCs = 1"
        )

    def test_ensure_graph_properties_rejects_invalid_graphs(self):
        multigraph = nx.MultiGraph()
        multigraph.add_edges_from([(0, 1), (0, 1)])

        directed_graph = nx.DiGraph([(0, 1)])

        weighted_graph = nx.Graph()
        weighted_graph.add_edge(0, 1, weight=0.5)

        value_weighted_graph = nx.Graph()
        value_weighted_graph.add_edge(0, 1, value=2)

        self_loop_graph = nx.Graph()
        self_loop_graph.add_edge(0, 0)

        invalid_cases = [
            (multigraph, "Parallel edges"),
            (directed_graph, "undirected"),
            (weighted_graph, "unweighted"),
            (value_weighted_graph, "unweighted"),
            (self_loop_graph, "without self-loops")
        ]

        for graph, expected_message in invalid_cases:
            with self.subTest(expected_message=expected_message):
                with self.assertRaisesRegex(ValueError, expected_message):
                    loader_module._ensure_graph_properties(graph)

    def test_parse_label(self):
        self.assertEqual(loader_module._parse_label("12"), 12)
        self.assertEqual(loader_module._parse_label("-3"), -3)
        self.assertEqual(loader_module._parse_label("community-a"), "community-a")

    def test_check_nodes_without_communities(self):
        non_overlapping_config = NetworkConfig(
            name="network",
            gml_filename="network",
            ground_truth=True,
            overlapping_ground_truth=False,
            ground_truth_attr="community"
        )
        overlapping_config = NetworkConfig(
            name="network",
            gml_filename="network",
            ground_truth=True,
            overlapping_ground_truth=True,
            ground_truth_attr="circles"
        )

        with patch("builtins.print") as mocked_print:
            loader_module._check_nodes_without_communities(
                [0, -1, 1, -1],
                non_overlapping_config
            )
            loader_module._check_nodes_without_communities(
                [[0], [-1], [1, 2]],
                overlapping_config
            )
            loader_module._check_nodes_without_communities(
                None,
                non_overlapping_config
            )

        self.assertEqual(mocked_print.call_count, 2)
        mocked_print.assert_any_call(
            "[INFO] Nodes without ground-truth labels = 2"
        )
        mocked_print.assert_any_call(
            "[INFO] Nodes without ground-truth labels = 1"
        )


if __name__ == "__main__":
    unittest.main()
