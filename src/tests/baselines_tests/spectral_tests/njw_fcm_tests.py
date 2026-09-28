import unittest
from unittest.mock import patch

import numpy as np

import pipeline.baselines.spectral.njw_fcm as njw_fcm_module
from pipeline.baselines.spectral.njw_fcm import apply_njw_fcm_defuzzification_rule, njw_fcm


class TestNJWFCM(unittest.TestCase):

    def test_njw_fcm(self):
        W = np.array(
            [[0.0, 1.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 0.0]]
        )

        eigenvalues = np.array([0.0, 1.0, 2.0])
        eigenvectors = np.eye(3)
        memberships = np.array(
            [[0.8, 0.2, 0.4],
             [0.2, 0.8, 0.6]]
        )

        with (
            patch.object(
                njw_fcm_module.np.linalg,
                "eigh",
                return_value=(eigenvalues, eigenvectors)
            ) as mocked_eigh,
            patch.object(
                njw_fcm_module.fuzz.cluster,
                "cmeans",
                return_value=(
                        None,
                        memberships,
                        None,
                        None,
                        None,
                        None,
                        None
                )
            ) as mocked_cmeans
        ):
            U = njw_fcm(
                W=W,
                k=2,
                fcm_m=2.0,
                fcm_error=1e-5,
                fcm_max_iter=300,
                fcm_seed=13
            )

        expected_normalized_affinity = W / 2.0
        np.testing.assert_allclose(
            mocked_eigh.call_args.args[0],
            expected_normalized_affinity
        )

        expected_fcm_data = np.array(
            [[0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0]]
        )
        cmeans_kwargs = mocked_cmeans.call_args.kwargs
        np.testing.assert_allclose(
            cmeans_kwargs["data"],
            expected_fcm_data
        )
        self.assertEqual(cmeans_kwargs["c"], 2)
        self.assertEqual(cmeans_kwargs["m"], 2.0)
        self.assertEqual(cmeans_kwargs["error"], 1e-5)
        self.assertEqual(cmeans_kwargs["maxiter"], 300)
        self.assertEqual(cmeans_kwargs["seed"], 13)

        np.testing.assert_array_equal(
            U,
            memberships.T
        )

    def test_njw_fcm_estimates_k_using_eigengap(self):
        W = np.array(
            [[0.0, 1.0, 1.0, 1.0],
             [1.0, 0.0, 1.0, 1.0],
             [1.0, 1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0, 0.0]]
        )

        eigenvalues = np.array([0.1, 0.2, 0.9, 1.0])
        eigenvectors = np.eye(4)
        memberships = np.array(
            [[0.8, 0.7, 0.2, 0.1],
             [0.2, 0.3, 0.8, 0.9]]
        )

        with (
            patch.object(
                njw_fcm_module.np.linalg,
                "eigh",
                return_value=(eigenvalues, eigenvectors)
            ),
            patch.object(
                njw_fcm_module.fuzz.cluster,
                "cmeans",
                return_value=(
                        None,
                        memberships,
                        None,
                        None,
                        None,
                        None,
                        None
                )
            ) as mocked_cmeans
        ):
            U = njw_fcm(
                W=W,
                k=None,
                fcm_m=2.0,
                fcm_error=1e-5,
                fcm_max_iter=300,
                fcm_seed=13
            )

        self.assertEqual(mocked_cmeans.call_args.kwargs["c"], 2)
        np.testing.assert_array_equal(
            U,
            memberships.T
        )

    def test_non_overlapping_defuzzification(self):
        U = np.array(
            [[0.2, 0.8, 0.0],
             [0.6, 0.1, 0.3],
             [0.1, 0.2, 0.7]]
        )

        predicted_labels, k_predicted = apply_njw_fcm_defuzzification_rule(
            U=U,
            fi=-1.0,
            overlapping=False
        )

        self.assertEqual(predicted_labels, [1, 0, 2])
        self.assertEqual(k_predicted, 3)

    def test_overlapping_defuzzification(self):
        U = np.array(
            [[0.65, 0.60, 0.00],
             [0.10, 0.20, 0.70],
             [0.55, 0.10, 0.35]]
        )

        predicted_labels, k_predicted = apply_njw_fcm_defuzzification_rule(
            U=U,
            fi=0.60,
            overlapping=True
        )

        self.assertEqual(
            predicted_labels,
            [[0, 1], [2], [0]]
        )
        self.assertEqual(k_predicted, 3)

    def test_overlapping_defuzzification_uses_maximum_membership_fallback(self):
        U = np.array(
            [[0.30, 0.50, 0.20],
             [0.45, 0.40, 0.15]]
        )

        predicted_labels, k_predicted = apply_njw_fcm_defuzzification_rule(
            U=U,
            fi=0.80,
            overlapping=True
        )

        self.assertEqual(
            predicted_labels,
            [[1], [0]]
        )
        self.assertEqual(k_predicted, 2)

    def test_membership_threshold_boundary_values(self):
        U = np.array(
            [[1.0, 0.0],
             [0.0, 1.0]]
        )

        expected_results = {
            0.0: ([[0, 1], [0, 1]], 2),
            1.0: ([[0], [1]], 2)
        }

        for fi, expected_result in expected_results.items():
            with self.subTest(fi=fi):
                predicted_labels, k_predicted = apply_njw_fcm_defuzzification_rule(
                    U=U,
                    fi=fi,
                    overlapping=True
                )

                self.assertEqual(
                    predicted_labels,
                    expected_result[0]
                )
                self.assertEqual(
                    k_predicted,
                    expected_result[1]
                )

    def test_invalid_membership_threshold_for_overlapping_defuzzification(self):
        U = np.array(
            [[0.6, 0.4],
             [0.3, 0.7]]
        )

        for fi in (-0.1, 1.1):
            with self.subTest(fi=fi):
                with self.assertRaisesRegex(
                        ValueError,
                        "The membership threshold must be in the range"
                ):
                    apply_njw_fcm_defuzzification_rule(
                        U=U,
                        fi=fi,
                        overlapping=True
                    )

    def test_membership_threshold_is_not_used_for_non_overlapping_defuzzification(self):
        U = np.array(
            [[0.6, 0.4],
             [0.3, 0.7]]
        )

        predicted_labels, k_predicted = apply_njw_fcm_defuzzification_rule(
            U=U,
            fi=-1.0,
            overlapping=False
        )

        self.assertEqual(predicted_labels, [0, 1])
        self.assertEqual(k_predicted, 2)

    def test_only_assigned_communities_are_counted(self):
        U = np.array(
            [[0.9, 0.05, 0.05],
             [0.1, 0.1, 0.8]]
        )

        predicted_labels, k_predicted = apply_njw_fcm_defuzzification_rule(
            U=U,
            fi=0.7,
            overlapping=True
        )

        self.assertEqual(
            predicted_labels,
            [[0], [2]]
        )
        self.assertEqual(k_predicted, 2)

    def test_input_matrix_is_not_modified(self):
        W = np.array(
            [[0.0, 1.0],
             [1.0, 0.0]]
        )
        original_W = W.copy()

        memberships = np.array(
            [[0.8, 0.2],
             [0.2, 0.8]]
        )

        with patch.object(
                njw_fcm_module.fuzz.cluster,
                "cmeans",
                return_value=(
                        None,
                        memberships,
                        None,
                        None,
                        None,
                        None,
                        None
                )
        ):
            njw_fcm(
                W=W,
                k=2,
                fcm_m=2.0,
                fcm_error=1e-5,
                fcm_max_iter=300,
                fcm_seed=0
            )

        np.testing.assert_array_equal(
            W,
            original_W
        )


if __name__ == "__main__":
    unittest.main()
