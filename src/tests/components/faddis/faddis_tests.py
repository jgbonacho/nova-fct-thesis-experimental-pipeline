import unittest

import numpy as np

from pipeline.components.faddis.faddis import faddis


class Test(unittest.TestCase):

    def test_faddis_with_epsilon_tau_k_max(self):
        W = np.matrix(
            [[1, .5, .3, .1],
             [.5, 1, .98, .4],
             [.3, .98, 1, .6],
             [.1, .4, .6, 1]]
        )

        sequence_of_matrices, membership_matrix, contributions, intensities, eigenvalues, number_of_clusters = faddis(
            W, epsilon=1 / 40, tau=0.005, k_max=50
        )

        print("=== Sequence of matrices===")
        print(sequence_of_matrices)
        self.assertTrue(len(sequence_of_matrices) == number_of_clusters + 1)
        print("=== Membership matrix ===")
        print(membership_matrix)
        self.assertTrue(membership_matrix.shape == (4, number_of_clusters))
        print("=== Contributions ===")
        print(contributions)
        self.assertTrue(len(contributions) == number_of_clusters)
        print("=== Intensities ===")
        print(intensities)
        self.assertTrue(intensities.shape == (number_of_clusters, 2))
        print("=== Maximums eigenvalues ===")
        print(eigenvalues)
        self.assertTrue(len(eigenvalues) == number_of_clusters)
        print("=== Number of clusters ===")
        print(number_of_clusters)
        self.assertEqual(number_of_clusters, 3)

    def test_faddis_with_desired_k(self):
        W = np.matrix(
            [[1, .5, .3, .1],
             [.5, 1, .98, .4],
             [.3, .98, 1, .6],
             [.1, .4, .6, 1]]
        )

        sequence_of_matrices, membership_matrix, contributions, intensities, eigenvalues, number_of_clusters = faddis(
            W, desired_k=3
        )

        print("=== Sequence of matrices===")
        print(sequence_of_matrices)
        self.assertTrue(len(sequence_of_matrices) == number_of_clusters)
        print("=== Membership matrix ===")
        print(membership_matrix)
        self.assertTrue(membership_matrix.shape == (4, number_of_clusters))
        print("=== Contributions ===")
        print(contributions)
        self.assertTrue(len(contributions) == number_of_clusters)
        print("=== Intensities ===")
        print(intensities)
        self.assertTrue(intensities.shape == (number_of_clusters, 2))
        print("=== Maximums eigenvalues ===")
        print(eigenvalues)
        self.assertTrue(len(eigenvalues) == number_of_clusters)
        print("=== Number of clusters ===")
        print(number_of_clusters)
        self.assertEqual(number_of_clusters, 3)

    def test_invalid_parameters(self):
        W = np.matrix(
            [[1, .5, .3, .1],
             [.5, 1, .98, .4],
             [.3, .98, 1, .6],
             [.1, .4, .6, 1]]
        )

        self.assertRaises(
            ValueError,
            faddis, W, desired_k=2, epsilon=1 / 40, tau=0.005, k_max=50
        )
        self.assertRaises(
            ValueError,
            faddis, W, desired_k=2, epsilon=None, tau=0.005, k_max=50
        )
        self.assertRaises(
            ValueError,
            faddis, W, desired_k=2, epsilon=1 / 40, tau=None, k_max=50
        )
        self.assertRaises(
            ValueError,
            faddis, W, desired_k=2, epsilon=1 / 40, tau=0.005, k_max=None
        )

        self.assertRaises(
            ValueError,
            faddis, W, desired_k=None, epsilon=None, tau=0.005, k_max=50
        )
        self.assertRaises(
            ValueError,
            faddis, W, desired_k=None, epsilon=1 / 40, tau=None, k_max=50
        )
        self.assertRaises(
            ValueError,
            faddis, W, desired_k=None, epsilon=1 / 40, tau=0.005, k_max=None
        )
        self.assertRaises(
            ValueError,
            faddis, W, desired_k=-1
        )
        self.assertRaises(
            ValueError,
            faddis, W, epsilon=1 / 40, tau=0.005, k_max=-1
        )


if __name__ == "__main__":
    unittest.main()
