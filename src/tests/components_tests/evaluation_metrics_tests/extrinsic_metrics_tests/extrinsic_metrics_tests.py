import math
import unittest
from dataclasses import fields
from types import SimpleNamespace
from unittest.mock import call, patch

import networkx as nx
from pipeline.components.evaluation_metrics.extrinsic import extrinsic_metrics as metrics_module
from pipeline.components.evaluation_metrics.extrinsic import \
    extrinsic_metrics_for_non_overlapping_ground_truth as non_overlapping_module
from pipeline.components.evaluation_metrics.extrinsic import \
    extrinsic_metrics_for_overlapping_ground_truth as overlapping_module
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics


class TestExtrinsicMetrics(unittest.TestCase):

    def test_extrinsic_metrics_defaults_and_metadata(self):
        metrics = ExtrinsicMetrics(diff_of_k="2 | 2")

        self.assertEqual(metrics.diff_of_k, "2 | 2")
        self.assertIsNone(metrics.relative_error_of_k)
        self.assertIsNone(metrics.ami)
        self.assertIsNone(metrics.f_measure)
        self.assertIsNone(metrics.ari)
        self.assertIsNone(metrics.fmi)
        self.assertIsNone(metrics.nmi)
        self.assertIsNone(metrics.vi)
        self.assertIsNone(metrics.onmi)
        self.assertIsNone(metrics.omega)

        self.assertEqual(
            [
                dataclass_field.metadata["label"]
                for dataclass_field in fields(ExtrinsicMetrics)
            ],
            [
                "K' | K",
                "|K'-K|/K",
                "AMI",
                "F-measure",
                "ARI",
                "FMI",
                "NMI",
                "VI",
                "ONMI",
                "Omega"
            ]
        )

    def test_compute_extrinsic_metrics_dispatches_non_overlapping_after_filtering(self):
        graph = nx.Graph()
        graph.add_nodes_from([40, 10, 30, 20])
        graph.add_edges_from([(10, 20), (20, 30), (30, 40)])
        expected = ExtrinsicMetrics(
            diff_of_k="2 | 2",
            relative_error_of_k=0.0,
            ami=0.75
        )

        with patch.object(
                metrics_module,
                "compute_extrinsic_metrics_for_non_overlapping_ground_truth",
                return_value=expected
        ) as mocked_non_overlapping, patch.object(
            metrics_module,
            "compute_extrinsic_metrics_for_overlapping_ground_truth"
        ) as mocked_overlapping:
            result = metrics_module.compute_extrinsic_metrics(
                graph=graph,
                ground_truth_labels=[0, -1, 1, 1],
                predicted_labels=[2, 2, 3, 3],
                k=2,
                k_predicted=2,
                overlapping=False
            )

        self.assertIs(result, expected)
        mocked_non_overlapping.assert_called_once_with(
            [0, 1, 1],
            [2, 3, 3],
            2,
            2
        )
        mocked_overlapping.assert_not_called()

    def test_compute_extrinsic_metrics_dispatches_overlapping_after_filtering(self):
        graph = nx.path_graph(4)
        expected = ExtrinsicMetrics(
            diff_of_k="3 | 3",
            relative_error_of_k=0.0,
            onmi=0.8,
            omega=0.7
        )

        with patch.object(
                metrics_module,
                "compute_extrinsic_metrics_for_non_overlapping_ground_truth"
        ) as mocked_non_overlapping, patch.object(
            metrics_module,
            "compute_extrinsic_metrics_for_overlapping_ground_truth",
            return_value=expected
        ) as mocked_overlapping:
            result = metrics_module.compute_extrinsic_metrics(
                graph=graph,
                ground_truth_labels=[[0], [-1], [1, 2], [2]],
                predicted_labels=[[0], [0], [1, 2], [2]],
                k=3,
                k_predicted=3,
                overlapping=True
            )

        self.assertIs(result, expected)
        mocked_non_overlapping.assert_not_called()

        call_args = mocked_overlapping.call_args.args
        filtered_graph = call_args[0]
        self.assertEqual(set(filtered_graph.nodes()), {0, 2, 3})
        self.assertEqual(set(filtered_graph.edges()), {(2, 3)})
        self.assertEqual(call_args[1], [[0], [1, 2], [2]])
        self.assertEqual(call_args[2], [[0], [1, 2], [2]])
        self.assertEqual(call_args[3:], (3, 3))

    def test_remove_nodes_without_labels_returns_original_objects_when_unnecessary(self):
        graph = nx.path_graph(3)
        ground_truth_labels = [0, 0, 1]
        predicted_labels = [2, 2, 3]

        result = metrics_module._remove_nodes_without_community_labels(
            graph=graph,
            ground_truth_labels=ground_truth_labels,
            predicted_labels=predicted_labels,
            k=2,
            k_predicted=2,
            overlapping=False
        )

        self.assertIs(result[0], graph)
        self.assertIs(result[1], ground_truth_labels)
        self.assertIs(result[2], predicted_labels)
        self.assertEqual(result[3:], (2, 2))

    def test_remove_nodes_without_labels_validates_lengths(self):
        graph = nx.path_graph(3)

        with self.assertRaisesRegex(
                ValueError,
                "must have the same length"
        ):
            metrics_module._remove_nodes_without_community_labels(
                graph=graph,
                ground_truth_labels=[0, 1, 1],
                predicted_labels=[0, 1],
                k=2,
                k_predicted=2,
                overlapping=False
            )

        with self.assertRaisesRegex(
                ValueError,
                "must match the number of graph nodes"
        ):
            metrics_module._remove_nodes_without_community_labels(
                graph=graph,
                ground_truth_labels=[0, 1],
                predicted_labels=[0, 1],
                k=2,
                k_predicted=2,
                overlapping=False
            )

    def test_remove_nodes_without_labels_rejects_fully_unlabelled_ground_truth(self):
        with self.assertRaisesRegex(
                ValueError,
                "There are no nodes with community labels"
        ):
            metrics_module._remove_nodes_without_community_labels(
                graph=nx.path_graph(3),
                ground_truth_labels=[[-1], [], [-1]],
                predicted_labels=[[0], [0], [1]],
                k=2,
                k_predicted=2,
                overlapping=True
            )

    def test_has_ground_truth_label(self):
        self.assertTrue(
            metrics_module._has_ground_truth_label(0, False)
        )
        self.assertFalse(
            metrics_module._has_ground_truth_label(-1, False)
        )
        self.assertTrue(
            metrics_module._has_ground_truth_label([0, -1], True)
        )
        self.assertFalse(
            metrics_module._has_ground_truth_label([-1], True)
        )
        self.assertFalse(
            metrics_module._has_ground_truth_label([], True)
        )

    def test_count_communities(self):
        self.assertEqual(
            metrics_module._count_communities(
                [0, 0, 2, 2],
                overlapping=False
            ),
            2
        )
        self.assertEqual(
            metrics_module._count_communities(
                [[0, 1], [1], [2]],
                overlapping=True
            ),
            3
        )

    def test_non_overlapping_metrics_for_identical_partitions(self):
        metrics = (
            non_overlapping_module.compute_extrinsic_metrics_for_non_overlapping_ground_truth(
                ground_truth_labels=[0, 0, 1, 1],
                predicted_labels=[5, 5, 7, 7],
                k=2,
                k_predicted=2
            )
        )

        self.assertEqual(metrics.diff_of_k, "2 | 2")
        self.assertEqual(metrics.relative_error_of_k, 0.0)
        self.assertAlmostEqual(metrics.ami, 1.0)
        self.assertAlmostEqual(metrics.f_measure, 1.0)
        self.assertAlmostEqual(metrics.ari, 1.0)
        self.assertAlmostEqual(metrics.fmi, 1.0)
        self.assertAlmostEqual(metrics.nmi, 1.0)
        self.assertAlmostEqual(metrics.vi, 0.0)
        self.assertIsNone(metrics.onmi)
        self.assertIsNone(metrics.omega)

    def test_non_overlapping_metrics_report_k_difference(self):
        metrics = (
            non_overlapping_module.compute_extrinsic_metrics_for_non_overlapping_ground_truth(
                ground_truth_labels=[0, 0, 1, 1],
                predicted_labels=[0, 1, 2, 2],
                k=2,
                k_predicted=3
            )
        )

        self.assertEqual(metrics.diff_of_k, "3 | 2")
        self.assertEqual(metrics.relative_error_of_k, 0.5)

    def test_purity_and_f_measure(self):
        labels_a = [0, 0, 0, 1]
        labels_b = [0, 0, 1, 1]

        purity = non_overlapping_module._compute_purity(
            labels_a,
            labels_b
        )
        inverse_purity = non_overlapping_module._compute_purity(
            labels_b,
            labels_a
        )
        f_measure = non_overlapping_module._compute_f_measure(
            ground_truth_labels=labels_b,
            predicted_labels=labels_a
        )

        self.assertEqual(purity, 0.75)
        self.assertEqual(inverse_purity, 0.75)
        self.assertEqual(f_measure, 0.75)

    def test_entropy_and_variation_of_information(self):
        labels = [0, 0, 1, 1]

        self.assertAlmostEqual(
            non_overlapping_module._compute_entropy(labels),
            math.log(2)
        )
        self.assertAlmostEqual(
            non_overlapping_module._compute_vi(labels, labels),
            0.0
        )
        self.assertAlmostEqual(
            non_overlapping_module._compute_vi(
                labels,
                [0, 0, 0, 0]
            ),
            math.log(2)
        )

    def test_overlapping_metrics_orchestration(self):
        graph = nx.path_graph(3)
        ground_truth_node_clustering = object()
        predicted_node_clustering = object()

        with patch.object(
                overlapping_module,
                "_to_node_clustering",
                side_effect=[
                    ground_truth_node_clustering,
                    predicted_node_clustering
                ]
        ) as mocked_conversion, patch.object(
            overlapping_module,
            "_compute_onmi",
            return_value=0.80
        ) as mocked_onmi, patch.object(
            overlapping_module,
            "_compute_omega",
            return_value=0.75
        ) as mocked_omega:
            metrics = (
                overlapping_module.compute_extrinsic_metrics_for_overlapping_ground_truth(
                    graph=graph,
                    ground_truth_labels=[[0], [0, 1], [1]],
                    predicted_labels=[[2], [2, 3], [3]],
                    k=2,
                    k_predicted=3
                )
            )

        self.assertEqual(
            mocked_conversion.call_args_list,
            [
                call(
                    [[0], [0, 1], [1]],
                    graph,
                    method_name="ground_truth"
                ),
                call(
                    [[2], [2, 3], [3]],
                    graph,
                    method_name="predicted"
                )
            ]
        )
        mocked_onmi.assert_called_once_with(
            ground_truth_node_clustering,
            predicted_node_clustering
        )
        mocked_omega.assert_called_once_with(
            ground_truth_node_clustering,
            predicted_node_clustering
        )
        self.assertEqual(metrics.diff_of_k, "3 | 2")
        self.assertEqual(metrics.relative_error_of_k, 0.5)
        self.assertEqual(metrics.onmi, 0.80)
        self.assertEqual(metrics.omega, 0.75)
        self.assertIsNone(metrics.ami)

    def test_to_node_clustering(self):
        graph = nx.path_graph(3)

        with patch.object(
                overlapping_module,
                "NodeClustering"
        ) as mocked_node_clustering:
            overlapping_module._to_node_clustering(
                labels=[[0], [0, 1], [1]],
                graph=graph,
                method_name="predicted"
            )

        mocked_node_clustering.assert_called_once_with(
            communities=[[0, 1], [1, 2]],
            graph=graph,
            method_name="predicted",
            overlap=True
        )

    def test_build_overlapping_communities_from_sorted_graph_nodes(self):
        graph = nx.Graph()
        graph.add_nodes_from([30, 10, 20])

        communities = (
            overlapping_module._build_communities_from_labels(
                graph=graph,
                labels=[[1], [0, 1], [0]]
            )
        )

        self.assertEqual(
            communities,
            [
                [20, 30],
                [10, 20]
            ]
        )

    def test_onmi_and_omega_return_cdlib_scores(self):
        ground_truth = object()
        predicted = object()

        with patch.object(
                overlapping_module.ev,
                "overlapping_normalized_mutual_information_MGH",
                return_value=SimpleNamespace(score=0.61)
        ) as mocked_onmi, patch.object(
            overlapping_module.ev,
            "omega",
            return_value=SimpleNamespace(score=0.72)
        ) as mocked_omega:
            onmi = overlapping_module._compute_onmi(
                ground_truth,
                predicted
            )
            omega = overlapping_module._compute_omega(
                ground_truth,
                predicted
            )

        self.assertEqual(onmi, 0.61)
        self.assertEqual(omega, 0.72)
        mocked_onmi.assert_called_once_with(
            ground_truth,
            predicted
        )
        mocked_omega.assert_called_once_with(
            ground_truth,
            predicted
        )

    def test_compute_extrinsic_metrics_means_and_stds(self):
        graph = nx.path_graph(4)
        ground_truth_labels = [0, 0, 1, 1]
        predicted_labels_results = [
            [0, 0, 1, 1],
            [0, 1, 1, 1],
            [0, 0, 0, 1]
        ]
        k_predicted_results = [2, 4, 6]

        execution_results = [
            ExtrinsicMetrics(
                diff_of_k="2 | 3",
                relative_error_of_k=0.5,
                ami=0.75,
                f_measure=0.5,
                ari=0.25,
                fmi=0.625,
                nmi=0.875,
                vi=1.5,
                onmi=None,
                omega=float("nan")
            ),
            ExtrinsicMetrics(
                diff_of_k="4 | 3",
                relative_error_of_k=0.5,
                ami=0.75,
                f_measure=0.5,
                ari=0.25,
                fmi=0.625,
                nmi=0.875,
                vi=1.5,
                onmi=None,
                omega=float("nan")
            ),
            ExtrinsicMetrics(
                diff_of_k="6 | 3",
                relative_error_of_k=0.5,
                ami=0.75,
                f_measure=0.5,
                ari=0.25,
                fmi=0.625,
                nmi=0.875,
                vi=1.5,
                onmi=None,
                omega=float("nan")
            )
        ]

        with patch.object(
                metrics_module,
                "compute_extrinsic_metrics",
                side_effect=execution_results
        ) as mocked_compute_extrinsic_metrics:
            metrics = metrics_module.compute_extrinsic_metrics_means_and_stds(
                graph=graph,
                ground_truth_labels=ground_truth_labels,
                predicted_labels_results=predicted_labels_results,
                k=3,
                k_predicted_results=k_predicted_results,
                overlapping=False
            )

        self.assertEqual(
            mocked_compute_extrinsic_metrics.call_args_list,
            [
                call(
                    graph,
                    ground_truth_labels,
                    predicted_labels_results[0],
                    3,
                    2,
                    overlapping=False
                ),
                call(
                    graph,
                    ground_truth_labels,
                    predicted_labels_results[1],
                    3,
                    4,
                    overlapping=False
                ),
                call(
                    graph,
                    ground_truth_labels,
                    predicted_labels_results[2],
                    3,
                    6,
                    overlapping=False
                )
            ]
        )

        self.assertEqual(metrics.diff_of_k, "4.0 ± 2.0 | 3")
        self.assertEqual(metrics.relative_error_of_k, "0.5 ± 0.0")
        self.assertEqual(metrics.ami, "0.75 ± 0.0")
        self.assertEqual(metrics.f_measure, "0.5 ± 0.0")
        self.assertEqual(metrics.ari, "0.25 ± 0.0")
        self.assertEqual(metrics.fmi, "0.625 ± 0.0")
        self.assertEqual(metrics.nmi, "0.875 ± 0.0")
        self.assertEqual(metrics.vi, "1.5 ± 0.0")
        self.assertIsNone(metrics.onmi)
        self.assertIsNone(metrics.omega)

    def test_format_mean_and_sample_std(self):
        self.assertEqual(
            metrics_module._format_mean_and_sample_std(
                [1.0, 2.0, 3.0]
            ),
            "2.0 ± 1.0"
        )

        self.assertEqual(
            metrics_module._format_mean_and_sample_std(
                [4.5]
            ),
            "4.5 ± 0.0"
        )

        formatted_result = (
            metrics_module._format_mean_and_sample_std(
                [1.0, None, float("nan"), float("inf"), 3.0]
            )
        )
        mean, sample_std = formatted_result.split(" ± ")

        self.assertEqual(mean, "2.0")
        self.assertAlmostEqual(
            float(sample_std),
            math.sqrt(2.0)
        )

        self.assertIsNone(
            metrics_module._format_mean_and_sample_std(
                [
                    None,
                    float("nan"),
                    float("inf"),
                    float("-inf")
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()
