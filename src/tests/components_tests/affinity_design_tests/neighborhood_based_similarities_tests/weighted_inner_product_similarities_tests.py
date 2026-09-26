import unittest

import numpy as np
from pipeline.components.affinity_design.neighborhood_based_similarities.weighted_inner_product_similarities import \
    compute_ip, compute_cosip, _compute_weights_from_degrees


class TestWeightedInnerProductSimilarities(unittest.TestCase):

    def setUp(self):
        # Path graph: 0 -- 1 -- 2 -- 3.
        self.A = np.array(
            [[0, 1, 0, 0],
             [1, 0, 1, 0],
             [0, 1, 0, 1],
             [0, 0, 1, 0]],
            dtype=float
        )

    def test_compute_ip_with_beta_zero(self):
        W = compute_ip(self.A, beta=0)

        expected_W = np.array(
            [[0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, 1.0],
             [1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0]]
        )

        np.testing.assert_allclose(W, expected_W)

    def test_compute_ip_with_beta_one(self):
        W = compute_ip(self.A, beta=1)

        expected_W = np.array(
            [[0.0, 0.0, 0.5, 0.0],
             [0.0, 0.0, 0.0, 0.5],
             [0.5, 0.0, 0.0, 0.0],
             [0.0, 0.5, 0.0, 0.0]]
        )

        np.testing.assert_allclose(W, expected_W)

    def test_compute_cosip_with_beta_zero(self):
        W = compute_cosip(self.A, beta=0)

        expected_value = 1.0 / np.sqrt(2.0)
        expected_W = np.array(
            [[0.0, 0.0, expected_value, 0.0],
             [0.0, 0.0, 0.0, expected_value],
             [expected_value, 0.0, 0.0, 0.0],
             [0.0, expected_value, 0.0, 0.0]]
        )

        np.testing.assert_allclose(W, expected_W)

    def test_compute_cosip_with_beta_one(self):
        W = compute_cosip(self.A, beta=1)

        expected_value = 1.0 / np.sqrt(3.0)
        expected_W = np.array(
            [[0.0, 0.0, expected_value, 0.0],
             [0.0, 0.0, 0.0, expected_value],
             [expected_value, 0.0, 0.0, 0.0],
             [0.0, expected_value, 0.0, 0.0]]
        )

        np.testing.assert_allclose(W, expected_W)

    def test_output_properties(self):
        for similarity_function in (compute_ip, compute_cosip):
            with self.subTest(similarity_function=similarity_function.__name__):
                W = similarity_function(self.A, beta=0.5)

                self.assertEqual(W.shape, self.A.shape)
                self.assertEqual(W.dtype, np.float64)
                np.testing.assert_allclose(W, W.T)
                np.testing.assert_array_equal(np.diag(W), np.zeros(4))
                self.assertTrue(np.isfinite(W).all())

    def test_input_matrix_is_not_modified(self):
        original_A = self.A.copy()

        compute_ip(self.A, beta=0.5)
        compute_cosip(self.A, beta=0.5)

        np.testing.assert_array_equal(self.A, original_A)

    def test_compute_weights_from_degrees(self):
        degrees = np.array([0.0, 1.0, 4.0, 9.0])

        np.testing.assert_allclose(
            _compute_weights_from_degrees(degrees, beta=0),
            np.array([0.0, 1.0, 1.0, 1.0])
        )
        np.testing.assert_allclose(
            _compute_weights_from_degrees(degrees, beta=0.5),
            np.array([0.0, 1.0, 0.5, 1.0 / 3.0])
        )
        np.testing.assert_allclose(
            _compute_weights_from_degrees(degrees, beta=1),
            np.array([0.0, 1.0, 0.25, 1.0 / 9.0])
        )

    def test_invalid_beta(self):
        for beta in (-0.1, 1.1):
            for similarity_function in (compute_ip, compute_cosip):
                with self.subTest(
                        beta=beta,
                        similarity_function=similarity_function.__name__
                ):
                    with self.assertRaisesRegex(ValueError, "Beta must be in"):
                        similarity_function(self.A, beta=beta)

    def test_invalid_matrices(self):
        invalid_cases = [
            (
                np.zeros((2, 3)),
                "not square"
            ),
            (
                np.array(
                    [[0, 2],
                     [2, 0]]
                ),
                "not binary"
            ),
            (
                np.array(
                    [[0, 1],
                     [0, 0]]
                ),
                "not symmetric"
            ),
            (
                np.array(
                    [[1, 0],
                     [0, 0]]
                ),
                "diagonal is not zero"
            )
        ]

        for similarity_function in (compute_ip, compute_cosip):
            for A, expected_message in invalid_cases:
                with self.subTest(
                        similarity_function=similarity_function.__name__,
                        shape=A.shape,
                        expected_message=expected_message
                ):
                    with self.assertRaisesRegex(ValueError, expected_message):
                        similarity_function(A, beta=0.5)


if __name__ == "__main__":
    unittest.main()
