import unittest

import numpy as np

from pipeline.components.lapin.lapin import lapin


class Test(unittest.TestCase):

    def test_lapin(self):
        W = np.matrix([[1, 0, 1], [0, 3, 0], [1, 0, 9]])

        for variant in ['symmetric_normalized_laplacian', 'random_walk_normalized_laplacian', 'unnormalized_laplacian']:
            W_transformed = lapin(W, laplacian_variant=variant)
            print("\n" + variant)
            print(W_transformed)
            self.assertTrue(W_transformed.shape == W.shape)


if __name__ == "__main__":
    unittest.main()
