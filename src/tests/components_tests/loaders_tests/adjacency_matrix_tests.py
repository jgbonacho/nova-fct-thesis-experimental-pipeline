import unittest
from unittest.mock import patch

import networkx as nx
import numpy as np

from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix, ensure_square_matrix, \
    ensure_symmetric_matrix, ensure_binary_matrix, ensure_zero_diagonal_matrix, set_zero_diagonal_matrix


class TestAdjacencyMatrix(unittest.TestCase):

    def test_compute_adjacency_matrix(self):
        graph = nx.Graph()
        graph.add_nodes_from([3, 1, 2, 0])
        graph.add_edges_from([(0, 0), (0, 1), (1, 2), (2, 0), (2, 3)])

        A = compute_adjacency_matrix(graph)

        expected_A = np.array(
            [[0.0, 1.0, 1.0, 0.0],
             [1.0, 0.0, 1.0, 0.0],
             [1.0, 1.0, 0.0, 1.0],
             [0.0, 0.0, 1.0, 0.0]]
        )

        np.testing.assert_array_equal(A, expected_A)

    def test_compute_adjacency_matrix_does_not_modify_graph(self):
        graph = nx.Graph()
        graph.add_edges_from([(0, 0), (0, 1)])
        original_edges = list(graph.edges())

        compute_adjacency_matrix(graph)

        self.assertEqual(list(graph.edges()), original_edges)
        self.assertTrue(graph.has_edge(0, 0))

    def test_compute_adjacency_matrix_empty_graph(self):
        A = compute_adjacency_matrix(nx.Graph())

        self.assertEqual(A.shape, (0, 0))

    def test_compute_adjacency_matrix_rejects_weighted_graph(self):
        graph = nx.Graph()
        graph.add_edge(0, 1, weight=0.5)

        with self.assertRaisesRegex(ValueError, "not binary"):
            compute_adjacency_matrix(graph)

    def test_compute_adjacency_matrix_rejects_directed_graph(self):
        graph = nx.DiGraph()
        graph.add_edge(0, 1)

        with self.assertRaisesRegex(ValueError, "not symmetric"):
            compute_adjacency_matrix(graph)

    def test_ensure_square_matrix(self):
        ensure_square_matrix(np.zeros((2, 2)))

        invalid_matrices = [
            np.zeros(3),
            np.zeros((2, 3))
        ]

        for A in invalid_matrices:
            with self.subTest(shape=A.shape):
                with self.assertRaisesRegex(ValueError, "not square"):
                    ensure_square_matrix(A)

    def test_ensure_symmetric_matrix(self):
        ensure_symmetric_matrix(
            np.array(
                [[0, 1],
                 [1, 0]]
            )
        )

        with self.assertRaisesRegex(ValueError, "not symmetric"):
            ensure_symmetric_matrix(
                np.array(
                    [[0, 1],
                     [0, 0]]
                )
            )

    def test_ensure_binary_matrix(self):
        ensure_binary_matrix(
            np.array(
                [[0, 1],
                 [1, 0]]
            )
        )

        invalid_matrices = [
            np.array(
                [[0, 2],
                 [1, 0]]
            ),
            np.array(
                [[0, 0.5],
                 [0.5, 0]]
            )
        ]

        for A in invalid_matrices:
            with self.subTest(A=A):
                with self.assertRaisesRegex(ValueError, "not binary"):
                    ensure_binary_matrix(A)

    def test_ensure_zero_diagonal_matrix(self):
        ensure_zero_diagonal_matrix(
            np.array(
                [[0, 1],
                 [1, 0]]
            )
        )

        with self.assertRaisesRegex(ValueError, "diagonal is not zero"):
            ensure_zero_diagonal_matrix(
                np.array(
                    [[1, 0],
                     [0, 0]]
                )
            )

    def test_set_zero_diagonal_matrix(self):
        A = np.array(
            [[1.0, 1.0],
             [1.0, 2.0]]
        )

        with patch("builtins.print") as mocked_print:
            result = set_zero_diagonal_matrix(A)

        self.assertIsNone(result)
        np.testing.assert_array_equal(
            A,
            np.array(
                [[0.0, 1.0],
                 [1.0, 0.0]]
            )
        )
        mocked_print.assert_called_once_with("[INFO] Setting adjacency matrix diagonal to zero.")

    def test_set_zero_diagonal_matrix_with_zero_diagonal(self):
        A = np.array(
            [[0.0, 1.0],
             [1.0, 0.0]]
        )
        expected_A = A.copy()

        with patch("builtins.print") as mocked_print:
            set_zero_diagonal_matrix(A)

        np.testing.assert_array_equal(A, expected_A)
        mocked_print.assert_not_called()


if __name__ == "__main__":
    unittest.main()
