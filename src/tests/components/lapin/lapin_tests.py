import unittest

import numpy as np

from pipeline.components.lapin.lapin import lapin


class Test(unittest.TestCase):

    def test_lapin(self):
        W = np.matrix([[1, 0, 1], [0, 3, 0], [1, 0, 9]])

        W_transformed = lapin(W)
        print(W_transformed)
        self.assertTrue(W_transformed.shape == W.shape)


if __name__ == "__main__":
    unittest.main()
