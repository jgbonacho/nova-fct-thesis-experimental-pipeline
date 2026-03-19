import unittest

import numpy as np

from pipeline.components.affinity_design.neighborhood_based_similarities.weighted_inner_product_similarities import \
    compute_ip, compute_cosip


class Test(unittest.TestCase):

    @staticmethod
    def get_adjacency_matrix():
        return np.array([[0, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 0]])

    def test_ip(self):
        A = self.get_adjacency_matrix()

        for beta in [0.0, 0.5, 1.0]:
            W_IP = compute_ip(A, beta=beta)
            self.assertTrue(np.allclose(W_IP, W_IP.T))
            self.assertTrue(np.all(np.diag(W_IP) == 0))

    def test_cosip(self):
        A = self.get_adjacency_matrix()

        for beta in [0.0, 0.5, 1.0]:
            W_CosIP = compute_ip(A, beta=beta)
            self.assertTrue(np.allclose(W_CosIP, W_CosIP.T), "W_CosIP is not symmetric")
            self.assertTrue(np.all(np.diag(W_CosIP) == 0), "W_CosIP does not have a zero diagonal.")

    def test_ip_invalid_beta(self):
        A = self.get_adjacency_matrix()
        self.assertRaises(ValueError, compute_ip, A, beta=-0.5)
        self.assertRaises(ValueError, compute_ip, A, beta=1.5)

    def test_cosip_invalid_beta(self):
        A = self.get_adjacency_matrix()
        self.assertRaises(ValueError, compute_cosip, A, beta=-0.5)
        self.assertRaises(ValueError, compute_cosip, A, beta=1.5)


if __name__ == "__main__":
    unittest.main()
