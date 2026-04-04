import unittest

import numpy as np

from pipeline.components.defuzzification.defuzzification import apply_defuzzification_rule


class Test(unittest.TestCase):

    def test1_maximum_membership_assignment(self):
        U = np.array([[0.1, 0.1, 0.8], [0.8, 0.1, 0.1], [0.2, 0.6, 0.2], [0.0, 0.5, 0.5]])

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U, conditionally_discard_first_cluster=True, overlapping=False
        )
        self.assertFalse(first_cluster_discarded)
        self.assertEqual(predicted_labels, [2, 0, 1, 1])
        self.assertEqual(k_predicted, 3)

    def test2_maximum_membership_assignment(self):
        U = np.array([[0.1, 0.1, 0.8], [0.8, 0.1, 0.1], [0.2, 0.6, 0.2], [0.1, 0.5, 0.4]])

        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
            U, conditionally_discard_first_cluster=True, overlapping=False
        )
        self.assertTrue(first_cluster_discarded)
        self.assertEqual(predicted_labels, [2, 1, 1, 1])
        self.assertEqual(k_predicted, 2)

    def test1_node_wise_alpha_cut_thresholding(self):
        U = np.array([[0.1, 0.1, 0.8], [0.8, 0.1, 0.1], [0.2, 0.6, 0.2], [0.0, 0.5, 0.5]])

        for gamma in [0.3, 0.5, 0.7]:
            predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
                U, gamma=gamma, conditionally_discard_first_cluster=True, overlapping=True
            )
            self.assertFalse(first_cluster_discarded)
            print(predicted_labels)

    def test2_node_wise_alpha_cut_thresholding(self):
        U = np.array([[0.1, 0.1, 0.8], [0.8, 0.1, 0.1], [0.2, 0.6, 0.2], [0.1, 0.5, 0.4]])

        for gamma in [0.3, 0.5, 0.7]:
            predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
                U, gamma=gamma, conditionally_discard_first_cluster=True, overlapping=True
            )
            self.assertTrue(first_cluster_discarded)
            print(predicted_labels)

    def test_invalid_gamma(self):
        U = np.array([[0.1, 0.1, 0.8], [0.8, 0.1, 0.1], [0.2, 0.6, 0.2], [0.1, 0.5, 0.4]])

        self.assertRaises(ValueError, apply_defuzzification_rule, U, gamma=-0.5, overlapping=True)
        self.assertRaises(ValueError, apply_defuzzification_rule, U, gamma=1.5, overlapping=True)


if __name__ == "__main__":
    unittest.main()
