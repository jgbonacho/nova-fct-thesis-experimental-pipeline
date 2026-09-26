import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

import networkx as nx
from pipeline.components.loaders.synthetic_data_loader import load_lfr_benchmark_network, _read_edges_nse, \
    _read_memberships_nmc


class TestSyntheticDataLoader(unittest.TestCase):

    @staticmethod
    def _write_file(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

    def test_load_lfr_network_with_non_overlapping_ground_truth(self):
        dir_name = "test_family1"
        filename = "n50mu0.1on0om0inst1"

        graph, ground_truth_labels, k = load_lfr_benchmark_network(
            dir_path=os.path.join(os.path.dirname(__file__), dir_name),
            filename=filename,
            overlapping_ground_truth=False
        )

        self.assertEqual(sorted(graph.nodes()), list(range(graph.number_of_nodes())))
        self.assertTrue(nx.is_connected(graph))
        self.assertFalse(graph.is_directed())
        self.assertEqual(list(nx.selfloop_edges(graph)), [])
        self.assertEqual(len(ground_truth_labels), graph.number_of_nodes())
        self.assertTrue(all(isinstance(label, int) for label in ground_truth_labels))
        self.assertEqual(len(set(ground_truth_labels)), k)

    def test_load_lfr_network_with_overlapping_ground_truth(self):
        dir_name = "test_family2"
        filename = "n50mu0.1on5om2inst1"

        graph, ground_truth_labels, k = load_lfr_benchmark_network(
            dir_path=os.path.join(os.path.dirname(__file__), dir_name),
            filename=filename,
            overlapping_ground_truth=True
        )

        self.assertEqual(sorted(graph.nodes()), list(range(graph.number_of_nodes())))
        self.assertTrue(nx.is_connected(graph))
        self.assertFalse(graph.is_directed())
        self.assertEqual(list(nx.selfloop_edges(graph)), [])
        self.assertEqual(len(ground_truth_labels), graph.number_of_nodes())
        self.assertTrue(all(isinstance(labels, list) for labels in ground_truth_labels))
        self.assertEqual(len({label for labels in ground_truth_labels for label in labels}), k)

    def test_read_edges_nse(self):
        with TemporaryDirectory() as temporary_dir:
            nse_path = os.path.join(temporary_dir, "network.nse")
            self._write_file(
                nse_path,
                "# Comment\n"
                "\n"
                "1 1\n"
                "1 2\n"
                "2 1\n"
                "2 3\n"
                "3 2\n"
                "4 5\n"
            )

            graph = _read_edges_nse(nse_path)

        self.assertIsInstance(graph, nx.Graph)
        self.assertFalse(graph.is_directed())
        self.assertEqual(set(graph.edges()), {(1, 2), (2, 3), (4, 5)})
        self.assertEqual(list(nx.selfloop_edges(graph)), [])

    def test_read_memberships_nmc_with_non_overlapping_ground_truth(self):
        with TemporaryDirectory() as temporary_dir:
            nmc_path = os.path.join(temporary_dir, "network.nmc")
            self._write_file(
                nmc_path,
                "# Comment\n"
                "\n"
                "1 2\n"
                "2 3 4\n"
            )

            memberships = _read_memberships_nmc(
                nmc_path=nmc_path,
                overlapping_ground_truth=False
            )

        self.assertEqual(memberships, {1: 2, 2: 3})

    def test_read_memberships_nmc_with_overlapping_ground_truth(self):
        with TemporaryDirectory() as temporary_dir:
            nmc_path = os.path.join(temporary_dir, "network.nmc")
            self._write_file(
                nmc_path,
                "# Comment\n"
                "\n"
                "1 2\n"
                "2 3 4\n"
            )

            memberships = _read_memberships_nmc(
                nmc_path=nmc_path,
                overlapping_ground_truth=True
            )

        self.assertEqual(memberships, {1: [2], 2: [3, 4]})

    def test_load_lfr_network_relabels_nodes_and_labels(self):
        with TemporaryDirectory() as temporary_dir:
            filename = "network"
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nse"),
                "10 20\n"
                "20 30\n"
                "30 10\n"
            )
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nmc"),
                "10 1\n"
                "20 2\n"
                "30 2\n"
            )

            graph, ground_truth_labels, k = load_lfr_benchmark_network(
                dir_path=temporary_dir,
                filename=filename,
                overlapping_ground_truth=False
            )

        self.assertEqual(sorted(graph.nodes()), [0, 1, 2])
        self.assertEqual(set(graph.edges()), {(0, 1), (0, 2), (1, 2)})
        self.assertEqual(ground_truth_labels, [0, 1, 1])
        self.assertEqual(k, 2)

    def test_load_lfr_network_with_overlapping_labels(self):
        with TemporaryDirectory() as temporary_dir:
            filename = "network"
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nse"),
                "10 20\n"
                "20 30\n"
            )
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nmc"),
                "10 1 2\n"
                "20 2\n"
                "30 3 2\n"
            )

            graph, ground_truth_labels, k = load_lfr_benchmark_network(
                dir_path=temporary_dir,
                filename=filename,
                overlapping_ground_truth=True
            )

        self.assertEqual(sorted(graph.nodes()), [0, 1, 2])
        self.assertEqual(set(graph.edges()), {(0, 1), (1, 2)})
        self.assertEqual(ground_truth_labels, [[0, 1], [1], [2, 1]])
        self.assertEqual(k, 3)

    @patch("builtins.print")
    def test_load_lfr_network_extracts_largest_connected_component(self, mocked_print):
        with TemporaryDirectory() as temporary_dir:
            filename = "network"
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nse"),
                "1 2\n"
                "2 3\n"
                "10 11\n"
            )
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nmc"),
                "1 1\n"
                "2 1\n"
                "3 2\n"
                "10 3\n"
                "11 3\n"
            )

            graph, ground_truth_labels, k = load_lfr_benchmark_network(
                dir_path=temporary_dir,
                filename=filename,
                overlapping_ground_truth=False
            )

        self.assertEqual(sorted(graph.nodes()), [0, 1, 2])
        self.assertEqual(set(graph.edges()), {(0, 1), (1, 2)})
        self.assertEqual(ground_truth_labels, [0, 0, 1])
        self.assertEqual(k, 2)
        mocked_print.assert_called_once_with("[INFO] Nodes LCC = 3; Edges LCC = 2")

    def test_load_lfr_network_requires_membership_for_every_graph_node(self):
        with TemporaryDirectory() as temporary_dir:
            filename = "network"
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nse"),
                "1 2\n"
            )
            self._write_file(
                os.path.join(temporary_dir, f"{filename}.nmc"),
                "1 1\n"
            )

            with self.assertRaises(KeyError):
                load_lfr_benchmark_network(
                    dir_path=temporary_dir,
                    filename=filename,
                    overlapping_ground_truth=False
                )


if __name__ == "__main__":
    unittest.main()
