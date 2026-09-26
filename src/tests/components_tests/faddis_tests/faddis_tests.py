import io
import unittest
from contextlib import redirect_stdout

import numpy as np
from pipeline.components.faddis.faddis import faddis


class TestFaddis(unittest.TestCase):

    def setUp(self):
        self.W = np.asarray(
            [[1, .5, .3, .1],
             [.5, 1, .98, .4],
             [.3, .98, 1, .6],
             [.1, .4, .6, 1]],
            dtype=float
        )

    @staticmethod
    def _run_faddis(W, **kwargs):
        # Suppress the debug output produced during cluster extraction.
        with redirect_stdout(io.StringIO()):
            return faddis(W=W, **kwargs)

    def _assert_consistent_results(
            self,
            membership_matrix,
            contributions,
            intensities,
            eigenvalues,
            number_of_clusters
    ):
        self.assertIsInstance(membership_matrix, np.ndarray)
        self.assertIsInstance(contributions, np.ndarray)
        self.assertIsInstance(intensities, np.ndarray)
        self.assertIsInstance(eigenvalues, np.ndarray)

        self.assertEqual(membership_matrix.shape, (self.W.shape[0], number_of_clusters))
        self.assertEqual(contributions.shape, (number_of_clusters,))
        self.assertEqual(intensities.shape, (number_of_clusters, 2))
        self.assertEqual(eigenvalues.shape, (number_of_clusters,))

        self.assertTrue(np.all(membership_matrix >= 0.0))
        self.assertTrue(np.all(membership_matrix <= 1.0))
        np.testing.assert_allclose(
            np.linalg.norm(membership_matrix, axis=0),
            np.ones(number_of_clusters),
            atol=1e-12
        )

        self.assertTrue(np.all(contributions > 0.0))
        self.assertLessEqual(float(np.sum(contributions)), 1.0 + 1e-12)
        self.assertTrue(np.all(intensities >= 0.0))
        np.testing.assert_allclose(intensities[:, 0] ** 2, intensities[:, 1], atol=1e-12)
        self.assertTrue(np.all(eigenvalues > 0.0))

    def test_faddis_with_epsilon_tau_k_max(self):
        results = self._run_faddis(
            self.W,
            epsilon=1 / 40,
            tau=0.005,
            k_max=50
        )
        membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, stop_condition = results

        self._assert_consistent_results(
            membership_matrix,
            contributions,
            intensities,
            eigenvalues,
            number_of_clusters
        )
        self.assertEqual(number_of_clusters, 3)
        self.assertEqual(stop_condition, "epsilon")

    def test_faddis_with_desired_k(self):
        results = self._run_faddis(self.W, desired_k=3)
        membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, stop_condition = results

        self._assert_consistent_results(
            membership_matrix,
            contributions,
            intensities,
            eigenvalues,
            number_of_clusters
        )
        self.assertEqual(number_of_clusters, 3)
        self.assertEqual(stop_condition, "desiredK")

    def test_faddis_stops_at_k_max(self):
        results = self._run_faddis(
            self.W,
            epsilon=-np.inf,
            tau=-np.inf,
            k_max=2
        )
        membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, stop_condition = results

        self._assert_consistent_results(
            membership_matrix,
            contributions,
            intensities,
            eigenvalues,
            number_of_clusters
        )
        self.assertEqual(number_of_clusters, 2)
        self.assertEqual(stop_condition, "Kmax")

    def test_faddis_stops_at_tau(self):
        membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, stop_condition = (
            self._run_faddis(
                self.W,
                epsilon=-np.inf,
                tau=0.9,
                k_max=50
            )
        )

        self.assertEqual(number_of_clusters, 0)
        self.assertEqual(stop_condition, "tau")
        self.assertEqual(membership_matrix.shape, (self.W.shape[0], 0))
        self.assertEqual(contributions.size, 0)
        self.assertEqual(intensities.size, 0)
        self.assertEqual(eigenvalues.size, 0)

    def test_faddis_stops_when_no_positive_eigenvalues_exist(self):
        W = np.zeros((3, 3), dtype=float)

        membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, stop_condition = (
            self._run_faddis(W, desired_k=2)
        )

        self.assertEqual(number_of_clusters, 0)
        self.assertEqual(stop_condition, "W")
        self.assertEqual(membership_matrix.shape, (3, 0))
        self.assertEqual(contributions.size, 0)
        self.assertEqual(intensities.size, 0)
        self.assertEqual(eigenvalues.size, 0)

    def test_faddis_single_node(self):
        W = np.asarray([[1.0]])

        membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, stop_condition = (
            self._run_faddis(W, desired_k=1)
        )

        self.assertEqual(number_of_clusters, 1)
        self.assertEqual(stop_condition, "desiredK")
        np.testing.assert_allclose(membership_matrix, [[1.0]])
        np.testing.assert_allclose(contributions, [1.0])
        np.testing.assert_allclose(intensities, [[1.0, 1.0]])
        np.testing.assert_allclose(eigenvalues, [1.0])

    def test_faddis_does_not_modify_input_matrix(self):
        original_W = self.W.copy()

        self._run_faddis(self.W, desired_k=2)

        np.testing.assert_array_equal(self.W, original_W)

    def test_invalid_stop_criterion_combinations(self):
        invalid_parameters = [
            {"desired_k": 2, "epsilon": 1 / 40, "tau": 0.005, "k_max": 50},
            {"epsilon": None, "tau": 0.005, "k_max": 50},
            {"epsilon": 1 / 40, "tau": None, "k_max": 50},
            {"epsilon": 1 / 40, "tau": 0.005, "k_max": None},
            {}
        ]

        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters):
                with self.assertRaises(ValueError):
                    self._run_faddis(self.W, **parameters)

    def test_invalid_number_of_clusters(self):
        invalid_parameters = [
            {"desired_k": 0},
            {"desired_k": -1},
            {"epsilon": 1 / 40, "tau": 0.005, "k_max": 0},
            {"epsilon": 1 / 40, "tau": 0.005, "k_max": -1}
        ]

        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters):
                with self.assertRaises(ValueError):
                    self._run_faddis(self.W, **parameters)


if __name__ == "__main__":
    unittest.main()
