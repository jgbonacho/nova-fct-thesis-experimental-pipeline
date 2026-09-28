import unittest

import numpy as np

from pipeline.components.defuzzification.defuzzification import apply_defuzzification_rule


class TestDefuzzification(unittest.TestCase):

    def test_overlapping_defuzzification(self):
        U = np.array(
            [[0.9, 0.6, 0.1],
             [0.2, 0.8, 0.5],
             [0.1, 0.2, 0.9]]
        )

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U=U,
            gamma=0.5,
            conditionally_discard_first_cluster=False,
            overlapping=True
        )

        self.assertEqual(predicted_labels, [[0, 1], [1, 2], [2]])
        self.assertEqual(k_predicted, 3)
        self.assertFalse(first_cluster_discarded)

    def test_non_overlapping_defuzzification(self):
        U = np.array(
            [[0.9, 0.6, 0.1],
             [0.2, 0.8, 0.5],
             [0.1, 0.2, 0.9]]
        )

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U=U,
            conditionally_discard_first_cluster=False,
            overlapping=False
        )

        self.assertEqual(predicted_labels, [0, 1, 2])
        self.assertEqual(k_predicted, 3)
        self.assertFalse(first_cluster_discarded)

    def test_overlapping_defuzzification_discards_first_cluster(self):
        U = np.array(
            [[0.4, 0.9, 0.1],
             [0.2, 0.5, 0.8],
             [0.3, 0.6, 0.6]]
        )

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U=U,
            gamma=0.8,
            conditionally_discard_first_cluster=True,
            overlapping=True
        )

        self.assertEqual(predicted_labels, [[1], [2], [1, 2]])
        self.assertEqual(k_predicted, 2)
        self.assertTrue(first_cluster_discarded)

    def test_non_overlapping_defuzzification_discards_first_cluster(self):
        U = np.array(
            [[0.4, 0.9, 0.1],
             [0.2, 0.5, 0.8],
             [0.3, 0.6, 0.6]]
        )

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U=U,
            conditionally_discard_first_cluster=True,
            overlapping=False
        )

        self.assertEqual(predicted_labels, [1, 2, 1])
        self.assertEqual(k_predicted, 2)
        self.assertTrue(first_cluster_discarded)

    def test_first_cluster_is_not_discarded_when_it_contains_zero_membership(self):
        U = np.array(
            [[0.0, 0.8, 0.1],
             [0.2, 0.7, 0.3]]
        )

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U=U,
            gamma=0.5,
            conditionally_discard_first_cluster=True,
            overlapping=True
        )

        self.assertEqual(predicted_labels, [[1], [1]])
        self.assertEqual(k_predicted, 1)
        self.assertFalse(first_cluster_discarded)

    def test_single_cluster_is_not_discarded(self):
        U = np.array(
            [[0.4],
             [0.7]]
        )

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U=U,
            gamma=0.5,
            conditionally_discard_first_cluster=True,
            overlapping=True
        )

        self.assertEqual(predicted_labels, [[0], [0]])
        self.assertEqual(k_predicted, 1)
        self.assertFalse(first_cluster_discarded)

    def test_gamma_boundary_values(self):
        U = np.array(
            [[0.8, 0.4, 0.0],
             [0.2, 0.2, 0.1]]
        )

        labels_gamma_zero, k_gamma_zero, _ = apply_defuzzification_rule(
            U=U,
            gamma=0.0,
            conditionally_discard_first_cluster=False,
            overlapping=True
        )
        labels_gamma_one, k_gamma_one, _ = apply_defuzzification_rule(
            U=U,
            gamma=1.0,
            conditionally_discard_first_cluster=False,
            overlapping=True
        )

        self.assertEqual(labels_gamma_zero, [[0, 1, 2], [0, 1, 2]])
        self.assertEqual(k_gamma_zero, 3)
        self.assertEqual(labels_gamma_one, [[0], [0, 1]])
        self.assertEqual(k_gamma_one, 2)

    def test_invalid_gamma_for_overlapping_defuzzification(self):
        U = np.array(
            [[0.8, 0.2],
             [0.3, 0.7]]
        )

        for gamma in (-0.1, 1.1):
            with self.subTest(gamma=gamma):
                with self.assertRaisesRegex(
                        ValueError,
                        "Gamma must be in the range"
                ):
                    apply_defuzzification_rule(
                        U=U,
                        gamma=gamma,
                        conditionally_discard_first_cluster=False,
                        overlapping=True
                    )

    def test_gamma_is_not_used_for_non_overlapping_defuzzification(self):
        U = np.array(
            [[0.8, 0.2],
             [0.3, 0.7]]
        )

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U=U,
            gamma=-1.0,
            conditionally_discard_first_cluster=False,
            overlapping=False
        )

        self.assertEqual(predicted_labels, [0, 1])
        self.assertEqual(k_predicted, 2)
        self.assertFalse(first_cluster_discarded)

    def test_input_matrix_is_not_modified(self):
        U = np.array(
            [[0.4, 0.9, 0.1],
             [0.2, 0.5, 0.8]]
        )
        original_U = U.copy()

        apply_defuzzification_rule(
            U=U,
            gamma=0.5,
            conditionally_discard_first_cluster=True,
            overlapping=True
        )

        np.testing.assert_array_equal(U, original_U)


if __name__ == "__main__":
    unittest.main()
