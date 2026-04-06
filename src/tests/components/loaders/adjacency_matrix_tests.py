import unittest

import networkx as nx
import numpy as np

from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix


class Test(unittest.TestCase):

    def test_adjacency_matrix(self):
        graph = nx.Graph()
        graph.add_edges_from([(0, 0), (0, 1), (1, 2), (2, 0), (2, 3)])
        A = compute_adjacency_matrix(graph)

        self.assertTrue(A.ndim == 2 and A.shape[0] == A.shape[1])
        self.assertTrue(np.all((A == 0) | (A == 1)))
        self.assertTrue(np.allclose(A, A.T))
        self.assertTrue(np.all(np.diag(A) == 0))


if __name__ == "__main__":
    unittest.main()
