import unittest

import numpy as np

from pipeline.components.affinity_design.neighborhood_based_similarities.binary_set_similarities import compute_kul, \
    compute_dice, compute_ochiai


class Test(unittest.TestCase):

    @staticmethod
    def get_adjacency_matrix():
        return np.array([[0, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 0]])

    def test_kul(self):
        A = self.get_adjacency_matrix()
        W_Kul = compute_kul(A)
        print(W_Kul)

        self.assertTrue(W_Kul.ndim == 2 and W_Kul.shape[0] == W_Kul.shape[1])
        self.assertTrue(np.allclose(W_Kul, W_Kul.T))
        self.assertTrue(np.all(np.diag(W_Kul) == 0))

    def test_dice(self):
        A = self.get_adjacency_matrix()
        W_Dice = compute_dice(A)
        print(W_Dice)

        self.assertTrue(W_Dice.ndim == 2 and W_Dice.shape[0] == W_Dice.shape[1])
        self.assertTrue(np.allclose(W_Dice, W_Dice.T))
        self.assertTrue(np.all(np.diag(W_Dice) == 0))

    def test_ochiai(self):
        A = self.get_adjacency_matrix()
        W_Ochiai = compute_ochiai(A)
        print(W_Ochiai)

        self.assertTrue(W_Ochiai.ndim == 2 and W_Ochiai.shape[0] == W_Ochiai.shape[1])
        self.assertTrue(np.allclose(W_Ochiai, W_Ochiai.T))
        self.assertTrue(np.all(np.diag(W_Ochiai) == 0))


if __name__ == "__main__":
    unittest.main()
