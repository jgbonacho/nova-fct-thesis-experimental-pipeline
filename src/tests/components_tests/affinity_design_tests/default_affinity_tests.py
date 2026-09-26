import unittest

import numpy as np
from pipeline.components.affinity_design.default_affinity import default_affinity


class TestDefaultAffinity(unittest.TestCase):

    def test_default_affinity(self):
        A = np.array(
            [[0, 1, 0],
             [1, 0, 1],
             [0, 1, 0]],
            dtype=int
        )

        W = default_affinity(A)

        np.testing.assert_array_equal(
            W,
            np.array(
                [[0.0, 1.0, 0.0],
                 [1.0, 0.0, 1.0],
                 [0.0, 1.0, 0.0]],
                dtype=np.float64
            )
        )
        self.assertEqual(W.dtype, np.float64)

    def test_float32_input_is_converted_to_float64(self):
        A = np.array(
            [[0.0, 0.5],
             [0.5, 0.0]],
            dtype=np.float32
        )

        W = default_affinity(A)

        np.testing.assert_allclose(W, A)
        self.assertEqual(W.dtype, np.float64)

    def test_input_matrix_is_not_modified(self):
        A = np.array(
            [[0, 1],
             [1, 0]],
            dtype=int
        )
        original_A = A.copy()

        default_affinity(A)

        np.testing.assert_array_equal(A, original_A)

    def test_output_is_independent_from_integer_input(self):
        A = np.array(
            [[0, 1],
             [1, 0]],
            dtype=int
        )

        W = default_affinity(A)
        W[0, 1] = 0.0

        self.assertEqual(A[0, 1], 1)


if __name__ == "__main__":
    unittest.main()
