import unittest

import numpy as np

from pipeline.components.affinity_design.affinity_design_dataclass import AffinityDesign
from pipeline.components.sparsification.sparsification import _count_ground_truth_communities, \
    apply_global_threshold_sparsification


class TestSparsification(unittest.TestCase):

    @staticmethod
    def _non_default_affinity_design() -> AffinityDesign:
        return next(
            affinity_design
            for affinity_design in AffinityDesign
            if affinity_design != AffinityDesign.DEFAULT
        )

    def test_default_affinity_skips_sparsification(self):
        W = np.array(
            [[0.0, 1.0, 0.0, 0.0],
             [1.0, 0.0, 1.0, 0.0],
             [0.0, 1.0, 0.0, 1.0],
             [0.0, 0.0, 1.0, 0.0]]
        )
        ground_truth_labels = [0, 0, 1, 1]

        Ws, As, graph_s, ground_truth_labels_s, k_s, info = (
            apply_global_threshold_sparsification(
                W=W,
                ground_truth_labels=ground_truth_labels,
                affinity_design=AffinityDesign.DEFAULT,
                target_average_degree=1.0,
                keep_lcc=True
            )
        )

        np.testing.assert_array_equal(Ws, W)
        np.testing.assert_array_equal(As, W)
        self.assertEqual(sorted(graph_s.nodes()), [0, 1, 2, 3])
        self.assertEqual(
            sorted(graph_s.edges()),
            [(0, 1), (1, 2), (2, 3)]
        )
        self.assertEqual(ground_truth_labels_s, ground_truth_labels)
        self.assertEqual(k_s, 2)
        self.assertEqual(info.theta, "-")
        self.assertEqual(info.target_average_degree, "-")
        self.assertEqual(info.actual_average_degree, 1.5)
        self.assertEqual(info.diff_n, "4 | 4")

    def test_sparsification_retains_the_strongest_edges(self):
        W = np.array(
            [[0.0, 0.9, 0.8, 0.1],
             [0.9, 0.0, 0.7, 0.2],
             [0.8, 0.7, 0.0, 0.3],
             [0.1, 0.2, 0.3, 0.0]]
        )

        Ws, As, graph_s, ground_truth_labels_s, k_s, info = (
            apply_global_threshold_sparsification(
                W=W,
                ground_truth_labels=[0, 0, 1, 1],
                affinity_design=self._non_default_affinity_design(),
                target_average_degree=1.5,
                keep_lcc=False
            )
        )

        expected_Ws = np.array(
            [[0.0, 0.9, 0.8, 0.0],
             [0.9, 0.0, 0.7, 0.0],
             [0.8, 0.7, 0.0, 0.0],
             [0.0, 0.0, 0.0, 0.0]]
        )
        expected_As = (expected_Ws > 0).astype(float)

        np.testing.assert_array_equal(Ws, expected_Ws)
        np.testing.assert_array_equal(As, expected_As)
        self.assertEqual(graph_s.number_of_nodes(), 4)
        self.assertEqual(graph_s.number_of_edges(), 3)
        self.assertEqual(ground_truth_labels_s, [0, 0, 1, 1])
        self.assertEqual(k_s, 2)
        self.assertEqual(info.theta, 0.7)
        self.assertEqual(info.target_average_degree, 1.5)
        self.assertEqual(info.actual_average_degree, 1.5)
        self.assertEqual(info.diff_n, "4 | 4")

    def test_largest_connected_component_is_retained_and_labels_are_filtered(self):
        W = np.array(
            [[0.0, 0.9, 0.8, 0.0],
             [0.9, 0.0, 0.1, 0.0],
             [0.8, 0.1, 0.0, 0.2],
             [0.0, 0.0, 0.2, 0.0]]
        )

        Ws, As, graph_s, ground_truth_labels_s, k_s, info = (
            apply_global_threshold_sparsification(
                W=W,
                ground_truth_labels=[0, 0, 1, 2],
                affinity_design=self._non_default_affinity_design(),
                target_average_degree=1.0,
                keep_lcc=True
            )
        )

        expected_Ws = np.array(
            [[0.0, 0.9, 0.8],
             [0.9, 0.0, 0.0],
             [0.8, 0.0, 0.0]]
        )
        expected_As = (expected_Ws > 0).astype(float)

        np.testing.assert_array_equal(Ws, expected_Ws)
        np.testing.assert_array_equal(As, expected_As)
        self.assertEqual(sorted(graph_s.nodes()), [0, 1, 2])
        self.assertEqual(
            sorted(graph_s.edges()),
            [(0, 1), (0, 2)]
        )
        self.assertEqual(ground_truth_labels_s, [0, 0, 1])
        self.assertEqual(k_s, 2)
        self.assertEqual(info.theta, 0.8)
        self.assertEqual(info.actual_average_degree, 4.0 / 3.0)
        self.assertEqual(info.diff_n, "4 | 3")

    def test_overlapping_labels_are_filtered_with_the_largest_connected_component(self):
        W = np.array(
            [[0.0, 0.9, 0.8, 0.0],
             [0.9, 0.0, 0.1, 0.0],
             [0.8, 0.1, 0.0, 0.2],
             [0.0, 0.0, 0.2, 0.0]]
        )

        _, _, _, ground_truth_labels_s, k_s, _ = (
            apply_global_threshold_sparsification(
                W=W,
                ground_truth_labels=[[0], [0, 1], [1], [2]],
                affinity_design=self._non_default_affinity_design(),
                target_average_degree=1.0,
                keep_lcc=True
            )
        )

        self.assertEqual(
            ground_truth_labels_s,
            [[0], [0, 1], [1]]
        )
        self.assertEqual(k_s, 2)

    def test_keep_lcc_false_keeps_isolated_nodes(self):
        W = np.array(
            [[0.0, 0.9, 0.8, 0.0],
             [0.9, 0.0, 0.1, 0.0],
             [0.8, 0.1, 0.0, 0.2],
             [0.0, 0.0, 0.2, 0.0]]
        )

        _, _, graph_s, ground_truth_labels_s, k_s, info = (
            apply_global_threshold_sparsification(
                W=W,
                ground_truth_labels=[0, 0, 1, 2],
                affinity_design=self._non_default_affinity_design(),
                target_average_degree=1.0,
                keep_lcc=False
            )
        )

        self.assertEqual(graph_s.number_of_nodes(), 4)
        self.assertEqual(graph_s.number_of_edges(), 2)
        self.assertEqual(ground_truth_labels_s, [0, 0, 1, 2])
        self.assertEqual(k_s, 3)
        self.assertEqual(info.actual_average_degree, 1.0)
        self.assertEqual(info.diff_n, "4 | 4")

    def test_all_available_positive_edges_are_retained_when_target_is_larger(self):
        W = np.array(
            [[0.0, 0.7, 0.0],
             [0.7, 0.0, 0.6],
             [0.0, 0.6, 0.0]]
        )

        Ws, As, graph_s, _, _, info = apply_global_threshold_sparsification(
            W=W,
            ground_truth_labels=None,
            affinity_design=self._non_default_affinity_design(),
            target_average_degree=20.0,
            keep_lcc=True
        )

        np.testing.assert_array_equal(Ws, W)
        np.testing.assert_array_equal(
            As,
            (W > 0).astype(float)
        )
        self.assertEqual(graph_s.number_of_edges(), 2)
        self.assertEqual(info.theta, 0.6)
        self.assertEqual(info.actual_average_degree, 4.0 / 3.0)

    def test_no_positive_off_diagonal_affinities_raises_value_error(self):
        W = np.zeros((3, 3), dtype=float)

        with self.assertRaisesRegex(
                ValueError,
                "W has no positive off-diagonal affinities"
        ):
            apply_global_threshold_sparsification(
                W=W,
                ground_truth_labels=[0, 0, 1],
                affinity_design=self._non_default_affinity_design(),
                target_average_degree=1.0
            )

    def test_input_matrix_is_not_modified(self):
        W = np.array(
            [[0.0, 0.9, 0.8],
             [0.9, 0.0, 0.7],
             [0.8, 0.7, 0.0]]
        )
        original_W = W.copy()

        apply_global_threshold_sparsification(
            W=W,
            ground_truth_labels=[0, 0, 1],
            affinity_design=self._non_default_affinity_design(),
            target_average_degree=1.0,
            keep_lcc=False
        )

        np.testing.assert_array_equal(W, original_W)

    def test_count_non_overlapping_ground_truth_communities(self):
        self.assertEqual(
            _count_ground_truth_communities([0, 0, 2, 2, -1]),
            2
        )

    def test_count_overlapping_ground_truth_communities(self):
        self.assertEqual(
            _count_ground_truth_communities(
                [[0, 1], [1], [2, -1], [-1]]
            ),
            3
        )

    def test_count_ground_truth_communities_without_ground_truth(self):
        self.assertIsNone(
            _count_ground_truth_communities(None)
        )

    def test_count_ground_truth_communities_for_empty_labels(self):
        self.assertEqual(
            _count_ground_truth_communities([]),
            0
        )


if __name__ == "__main__":
    unittest.main()
