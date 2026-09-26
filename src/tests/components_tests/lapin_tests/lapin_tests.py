import unittest

import numpy as np
from pipeline.components.lapin.lapin import lapin, ENTITY_BOUND


class TestLapin(unittest.TestCase):

    def test_lapin_returns_expected_pseudoinverse(self):
        W = np.matrix(
            [[1.0, 1.0, 0.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]]
        )

        W_transformed = lapin(W)

        W_array = np.asarray(W, dtype=np.float64)
        w_sums = np.abs(W_array.sum(axis=0))
        normalized_affinity = W_array / np.sqrt(np.outer(w_sums, w_sums))
        normalized_laplacian = np.eye(W_array.shape[0]) - normalized_affinity
        expected = np.linalg.pinv(normalized_laplacian)

        self.assertIsInstance(W_transformed, np.ndarray)
        self.assertEqual(W_transformed.shape, W.shape)
        self.assertEqual(W_transformed.dtype, np.float64)
        np.testing.assert_allclose(W_transformed, expected, atol=1e-10)

    def test_lapin_returns_symmetric_finite_matrix(self):
        W = np.array(
            [[1.0, 0.0, 1.0],
             [0.0, 3.0, 0.0],
             [1.0, 0.0, 9.0]]
        )

        W_transformed = lapin(W)

        self.assertTrue(np.isfinite(W_transformed).all())
        np.testing.assert_allclose(W_transformed, W_transformed.T, atol=1e-10)

    def test_lapin_returns_zero_matrix_for_identity(self):
        W = np.eye(3)

        W_transformed = lapin(W)

        np.testing.assert_allclose(W_transformed, np.zeros((3, 3)), atol=1e-10)

    def test_lapin_symmetrizes_input(self):
        W = np.array(
            [[1.0, 2.0, 0.0],
             [0.0, 1.0, 1.0],
             [1.0, 0.0, 1.0]]
        )
        symmetric_W = (W + W.T) / 2

        transformed_from_asymmetric = lapin(W)
        transformed_from_symmetric = lapin(symmetric_W)

        np.testing.assert_allclose(
            transformed_from_asymmetric,
            transformed_from_symmetric,
            atol=1e-10
        )

    def test_lapin_does_not_modify_input(self):
        W = np.array(
            [[1.0, 0.5, 0.0],
             [0.5, 1.0, 0.5],
             [0.0, 0.5, 1.0]]
        )
        original_W = W.copy()

        lapin(W)

        np.testing.assert_array_equal(W, original_W)

    def test_lapin_raises_when_entity_sum_is_zero(self):
        W = np.array(
            [[1.0, 0.0, 0.0],
             [0.0, 0.0, 0.0],
             [0.0, 0.0, 1.0]]
        )

        with self.assertRaisesRegex(Exception, "Entities are no good"):
            lapin(W)

    def test_lapin_raises_when_entity_sum_is_below_boundary(self):
        W = np.diag([1.0, ENTITY_BOUND / 2, 1.0])

        with self.assertRaisesRegex(Exception, "Entities are no good"):
            lapin(W)


if __name__ == "__main__":
    unittest.main()
