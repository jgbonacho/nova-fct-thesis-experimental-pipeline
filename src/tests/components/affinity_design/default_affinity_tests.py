import unittest

import numpy as np

from pipeline.components.affinity_design.default_affinity import default_affinity


class Test(unittest.TestCase):

    @staticmethod
    def get_adjacency_matrix():
        return np.array([[0, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 0]])

    def test_default_affinity(self):
        A = self.get_adjacency_matrix()
        A_default_affinity = default_affinity(A)

        self.assertTrue(np.allclose(A, A_default_affinity))
        self.assertTrue(np.allclose(A_default_affinity, A_default_affinity.T))
        self.assertTrue(np.all(np.diag(A_default_affinity) == 0))


if __name__ == "__main__":
    unittest.main()
