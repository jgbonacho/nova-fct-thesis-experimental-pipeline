import unittest

import numpy as np

from pipeline.components.lapin.lapin import lapin


class Test(unittest.TestCase):

    def test_lapin(self):
        W = np.matrix([[1, 0, 1], [0, 3, 0], [1, 0, 9]])

        for variant in ['Lsym', 'Lrw', 'L']:
            W_transformed = lapin(W, laplacian_variant=variant)
            print("\n" + variant)
            print(W_transformed)
            self.assertTrue(W_transformed.shape == W.shape)

    def test_invalid_laplacian_variant(self):
        W = np.matrix([[1, 0, 1], [0, 3, 0], [1, 0, 9]])

        self.assertRaises(ValueError, lapin, W, laplacian_variant="invalid")


if __name__ == "__main__":
    unittest.main()
