import unittest

import numpy as np
from pipeline.components.affinity_design.neighborhood_based_similarities.binary_set_similarities import compute_kul, \
    compute_dice, compute_ochiai


class TestBinarySetSimilarities(unittest.TestCase):

    def setUp(self):
        # Path graph: 0 -- 1 -- 2 -- 3.
        self.A = np.array(
            [[0, 1, 0, 0],
             [1, 0, 1, 0],
             [0, 1, 0, 1],
             [0, 0, 1, 0]],
            dtype=float
        )

    def test_compute_kul(self):
        W = compute_kul(self.A)

        expected_W = np.array(
            [[0.0, 0.0, 0.75, 0.0],
             [0.0, 0.0, 0.0, 0.75],
             [0.75, 0.0, 0.0, 0.0],
             [0.0, 0.75, 0.0, 0.0]]
        )

        np.testing.assert_allclose(W, expected_W)

    def test_compute_dice(self):
        W = compute_dice(self.A)

        expected_value = 2.0 / 3.0
        expected_W = np.array(
            [[0.0, 0.0, expected_value, 0.0],
             [0.0, 0.0, 0.0, expected_value],
             [expected_value, 0.0, 0.0, 0.0],
             [0.0, expected_value, 0.0, 0.0]]
        )

        np.testing.assert_allclose(W, expected_W)

    def test_compute_ochiai(self):
        W = compute_ochiai(self.A)

        expected_value = 1.0 / np.sqrt(2.0)
        expected_W = np.array(
            [[0.0, 0.0, expected_value, 0.0],
             [0.0, 0.0, 0.0, expected_value],
             [expected_value, 0.0, 0.0, 0.0],
             [0.0, expected_value, 0.0, 0.0]]
        )

        np.testing.assert_allclose(W, expected_W)

    def test_output_properties(self):
        for similarity_function in (compute_kul, compute_dice, compute_ochiai):
            with self.subTest(similarity_function=similarity_function.__name__):
                W = similarity_function(self.A)

                self.assertEqual(W.shape, self.A.shape)
                self.assertEqual(W.dtype, np.float64)
                np.testing.assert_allclose(W, W.T)
                np.testing.assert_array_equal(np.diag(W), np.zeros(4))
                self.assertTrue(np.isfinite(W).all())

    def test_input_matrix_is_not_modified(self):
        original_A = self.A.copy()

        compute_kul(self.A)
        compute_dice(self.A)
        compute_ochiai(self.A)

        np.testing.assert_array_equal(self.A, original_A)

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

        for similarity_function in (compute_kul, compute_dice, compute_ochiai):
            for A, expected_message in invalid_cases:
                with self.subTest(
                        similarity_function=similarity_function.__name__,
                        shape=A.shape,
                        expected_message=expected_message
                ):
                    with self.assertRaisesRegex(ValueError, expected_message):
                        similarity_function(A)


if __name__ == "__main__":
    unittest.main()
