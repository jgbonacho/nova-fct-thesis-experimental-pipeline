import csv
import json
import os
import unittest
from dataclasses import fields
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np

from pipeline.components.affinity_design.affinity_design_dataclass import AffinityDesign
from pipeline.config.utils.defuzzification_rule_dataclass import DefuzzificationRule
from pipeline.config.utils.execution_mode_dataclass import ExecutionMode
from pipeline.scripts.utils.networks_dataclasses import LFRNetworkConfig, LFRNetworkFamilyConfig, NetworkConfig, \
    NetworkFamilyConfig
from pipeline.scripts.utils.utils import _count_assigned_nodes, _format_label, _format_value, _int_to_roman, \
    create_network_results_dir, create_results_dir, log_progress, save_faddis_clustering_results, \
    save_report_of_real_world_runner, save_report_of_synthetic_runner


class TestUtils(unittest.TestCase):

    @staticmethod
    def _read_csv(file_path: str) -> list[list[str]]:
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            return list(csv.reader(file))

    @staticmethod
    def _read_json(file_path: str) -> dict:
        with open(file_path, mode="r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _create_populated_dataclass(dataclass_type):
        instance = object.__new__(dataclass_type)

        for dataclass_field in fields(dataclass_type):
            setattr(instance, dataclass_field.name, 1)

        return instance

    def test_create_results_dir_creates_missing_base_directory(self):
        with TemporaryDirectory() as temporary_dir:
            base_dir = os.path.join(
                temporary_dir,
                "missing",
                "results"
            )

            results_dir = create_results_dir(base_dir)

            self.assertTrue(os.path.isdir(base_dir))
            self.assertTrue(os.path.isdir(results_dir))

    def test_create_network_results_dir(self):
        with TemporaryDirectory() as temporary_dir:
            network_results_dir = create_network_results_dir(
                results_dir=temporary_dir,
                network_family="family_01",
                network="network_a"
            )

            self.assertEqual(
                network_results_dir,
                os.path.join(
                    temporary_dir,
                    "family_01",
                    "network_a"
                )
            )
            self.assertTrue(
                os.path.isdir(network_results_dir)
            )

    def test_log_progress(self):
        with patch("builtins.print") as mocked_print:
            log_progress(
                current_step=2,
                total_steps=5,
                item_label="network_a",
                indent_level=3
            )

        mocked_print.assert_called_once_with(
            "### [2/5] 'network_a'"
        )

    def test_log_progress_with_empty_line(self):
        with patch("builtins.print") as mocked_print:
            log_progress(
                current_step=1,
                total_steps=2,
                item_label="family_01",
                indent_level=4,
                empty_line=True
            )

        mocked_print.assert_called_once_with(
            "\n#### [1/2] 'family_01'"
        )

    def test_save_faddis_clustering_results(self):
        with TemporaryDirectory() as temporary_dir:
            faddis_results = (
                np.array(
                    [[0.9, 0.1],
                     [0.6, 0.4],
                     [0.2, 0.8]]
                ),
                np.array([0.6, 0.4]),
                np.array(
                    [[0.7, 1.2],
                     [0.5, 0.8]]
                ),
                np.array([2.5, 1.5]),
                2,
                "epsilon"
            )

            save_faddis_clustering_results(
                results_dir=temporary_dir,
                results_id="001",
                faddis_results=faddis_results,
                predicted_labels=[0, 0, 1],
                ground_truth_labels=[0, 1, 1]
            )

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "faddis-clusters_001.csv"
                )
            )

        self.assertEqual(
            rows[0],
            [
                "Cluster",
                "Contribution",
                "Eigenvalue",
                "Intensity",
                "Weight",
                "Assigned Nodes"
            ]
        )
        self.assertEqual(
            rows[1],
            ["0", "60.0", "2.5", "0.7", "1.2", "2"]
        )
        self.assertEqual(
            rows[2],
            ["I", "40.0", "1.5", "0.5", "0.8", "1"]
        )

    def test_save_faddis_membership_matrix(self):
        with TemporaryDirectory() as temporary_dir:
            faddis_results = (
                np.array(
                    [[0.9, 0.1],
                     [0.4, 0.6]]
                ),
                np.array([0.6, 0.4]),
                np.array(
                    [[0.7, 1.2],
                     [0.5, 0.8]]
                ),
                np.array([2.0, 1.0]),
                2,
                "desiredK"
            )

            save_faddis_clustering_results(
                results_dir=temporary_dir,
                results_id="002",
                faddis_results=faddis_results,
                predicted_labels=[[0], [0, 1]],
                ground_truth_labels=[[0], [1]],
                save_membership_matrix=True
            )

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "faddis-nodes-002.csv"
                )
            )

        self.assertEqual(
            rows[0],
            [
                "Node",
                "Cluster_0",
                "Cluster_I",
                "Predicted Label",
                "Ground-Truth Label"
            ]
        )
        self.assertEqual(
            rows[1],
            ["0", "0.9", "0.1", "[0]", "[0]"]
        )
        self.assertEqual(
            rows[2],
            ["1", "0.4", "0.6", "[0, 1]", "[1]"]
        )

    def test_save_faddis_membership_matrix_without_ground_truth(self):
        with TemporaryDirectory() as temporary_dir:
            faddis_results = (
                np.array(
                    [[1.0],
                     [1.0]]
                ),
                np.array([1.0]),
                np.array([[1.0, 1.0]]),
                np.array([1.0]),
                1,
                "desiredK"
            )

            save_faddis_clustering_results(
                results_dir=temporary_dir,
                results_id="003",
                faddis_results=faddis_results,
                predicted_labels=[0, 0],
                ground_truth_labels=None,
                save_membership_matrix=True
            )

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "faddis-nodes-003.csv"
                )
            )

        self.assertEqual(
            rows[0],
            ["Node", "Cluster_0", "Predicted Label"]
        )
        self.assertEqual(len(rows[1]), 3)

    def test_save_report_of_synthetic_runner(self):
        with TemporaryDirectory() as temporary_dir:
            network_families = [
                LFRNetworkFamilyConfig(
                    name="family_01",
                    network_configs=[
                        LFRNetworkConfig(
                            description="Network",
                            instance=1,
                            name="network_a",
                            overlapping_ground_truth=False
                        )
                    ]
                )
            ]
            execution_mode = self._create_populated_dataclass(
                ExecutionMode
            )
            defuzzification_rule = self._create_populated_dataclass(
                DefuzzificationRule
            )

            save_report_of_synthetic_runner(
                results_dir=temporary_dir,
                network_families=network_families,
                thresholds={"family_01": 0.1},
                affinity_designs={AffinityDesign.DEFAULT: lambda A: A},
                execution_modes=[execution_mode],
                defuzzification_rules=[defuzzification_rule]
            )

            report = self._read_json(
                os.path.join(
                    temporary_dir,
                    "report.json"
                )
            )

        self.assertEqual(
            report["network_families"][0]["name"],
            "family_01"
        )
        self.assertEqual(
            report["thresholds"],
            {"family_01": 0.1}
        )
        self.assertEqual(
            report["affinity_designs"],
            [AffinityDesign.DEFAULT.value]
        )
        self.assertEqual(len(report["execution_modes"]), 1)
        self.assertEqual(len(report["defuzzification_rules"]), 1)

    def test_save_report_of_real_world_runner_with_only_required_values(self):
        with TemporaryDirectory() as temporary_dir:
            network_families = [
                NetworkFamilyConfig(
                    name="family_01",
                    directory="/networks",
                    network_configs=[
                        NetworkConfig(
                            name="network_a",
                            gml_filename="network_a",
                            ground_truth=False,
                            overlapping_ground_truth=None,
                            ground_truth_attr=None
                        )
                    ]
                )
            ]

            save_report_of_real_world_runner(
                results_dir=temporary_dir,
                network_families=network_families,
                output_filename="real-world-report"
            )

            report = self._read_json(
                os.path.join(
                    temporary_dir,
                    "real-world-report.json"
                )
            )

        self.assertEqual(
            list(report.keys()),
            ["network_families"]
        )
        self.assertEqual(
            report["network_families"][0]["directory"],
            "/networks"
        )

    def test_count_assigned_nodes_for_non_overlapping_labels(self):
        counts = _count_assigned_nodes(
            predicted_labels=[0, 1, 1, 2],
            number_of_clusters=3
        )

        self.assertEqual(
            counts,
            {0: 1, 1: 2, 2: 1}
        )

    def test_count_assigned_nodes_for_overlapping_labels(self):
        counts = _count_assigned_nodes(
            predicted_labels=[[0, 1], [1], [0, 2]],
            number_of_clusters=3
        )

        self.assertEqual(
            counts,
            {0: 2, 1: 2, 2: 1}
        )

    def test_format_label(self):
        test_cases = [
            (np.int64(3), 3),
            ([np.int64(1), 2], "[1, 2]"),
            (4, 4)
        ]

        for label, expected in test_cases:
            with self.subTest(label=label):
                self.assertEqual(
                    _format_label(label),
                    expected
                )

    def test_format_value(self):
        test_cases = [
            (True, "Yes"),
            (False, "No"),
            (0.0, "0"),
            (0.0000123, "1.230000e-05"),
            (0.25, "0.25"),
            (0.123456789, "0.123457"),
            (np.float64(2.5), "2.5"),
            ("value", "value"),
            (5, 5)
        ]

        for value, expected in test_cases:
            with self.subTest(value=value):
                self.assertEqual(
                    _format_value(value),
                    expected
                )

    def test_int_to_roman(self):
        test_cases = [
            (0, "0"),
            (1, "I"),
            (4, "IV"),
            (9, "IX"),
            (58, "LVIII"),
            (1994, "MCMXCIV"),
            (40000, "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
        ]

        for number, expected in test_cases:
            with self.subTest(number=number):
                self.assertEqual(
                    _int_to_roman(number),
                    expected
                )

    def test_int_to_roman_rejects_out_of_range_values(self):
        for number in (-1, 40001):
            with self.subTest(number=number):
                with self.assertRaisesRegex(
                        ValueError,
                        "Input must be an integer between 0 and 40000"
                ):
                    _int_to_roman(number)


if __name__ == "__main__":
    unittest.main()
