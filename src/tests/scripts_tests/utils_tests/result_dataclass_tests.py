import csv
import os
import unittest
from dataclasses import fields
from tempfile import TemporaryDirectory

from pipeline.components.evaluation_metrics.computational.computational_metrics_dataclass import ComputationalMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import IntrinsicMetrics
from pipeline.scripts.utils.result_dataclass import Result, initialize_results_file
from pipeline.scripts.utils.utils import _format_value


class TestResult(unittest.TestCase):

    @staticmethod
    def _read_csv(file_path: str) -> list[list[str]]:
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            return list(csv.reader(file))

    @staticmethod
    def _create_populated_dataclass(dataclass_type, start_value: int):
        instance = object.__new__(dataclass_type)

        for index, dataclass_field in enumerate(fields(dataclass_type)):
            setattr(
                instance,
                dataclass_field.name,
                start_value + index
            )

        return instance

    @staticmethod
    def _create_result(**overrides) -> Result:
        values = {
            "id": "001",
            "network_family": "family_01",
            "network": "network_a",
            "overlapping": False,
            "affinity_design": "Default",
            "execution_mode": "LAPIN-off",
            "laplacian_variant": "-",
            "epsilon": 0.1,
            "tau": 0.05,
            "k_max": 100,
            "stop_condition": "epsilon",
            "gamma": None,
            "first_cluster_discarded": False
        }
        values.update(overrides)

        return Result(**values)

    def test_default_optional_values(self):
        result = self._create_result()

        self.assertEqual(result.id, "001")
        self.assertEqual(result.network_family, "family_01")
        self.assertEqual(result.network, "network_a")
        self.assertFalse(result.overlapping)
        self.assertIsNone(result.gamma)
        self.assertIsNone(result.actual_average_degree)
        self.assertIsNone(result.sparsification_target_average_degree)
        self.assertIsNone(result.sparsification_theta)
        self.assertIsNone(result.sparsification_diff_n)
        self.assertIsNone(result.extrinsic_results)
        self.assertIsNone(result.intrinsic_results)
        self.assertIsNone(result.computational_results)

    def test_field_labels(self):
        labels = {
            dataclass_field.name: dataclass_field.metadata.get("label")
            for dataclass_field in fields(Result)
            if "label" in dataclass_field.metadata
        }

        self.assertEqual(labels["id"], "ID")
        self.assertEqual(labels["network_family"], "Network Family")
        self.assertEqual(labels["network"], "Network")
        self.assertEqual(labels["overlapping"], "Overlapping?")
        self.assertEqual(labels["epsilon"], "Epsilon")
        self.assertEqual(labels["k_max"], "Kmax")
        self.assertEqual(
            labels["first_cluster_discarded"],
            "C0 discarded?"
        )
        self.assertEqual(
            labels["sparsification_diff_n"],
            "N | Sparsified N"
        )

    def test_initialize_results_file_with_base_fields(self):
        with TemporaryDirectory() as temporary_dir:
            append_result = initialize_results_file(
                results_dir=temporary_dir
            )
            append_result(self._create_result(
                actual_average_degree=20.0,
                sparsification_target_average_degree=20.0,
                sparsification_theta=0.25,
                sparsification_diff_n="100 | 95"
            ))

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "_results.csv"
                )
            )

        self.assertEqual(
            rows[0],
            [
                "ID",
                "Network Family",
                "Network",
                "Overlapping?",
                "Affinity Design",
                "Execution Mode",
                "Laplacian",
                "Epsilon",
                "Tau",
                "Kmax",
                "Stop Condition",
                "C0 discarded?",
                "Actual Avg Degree",
                "Target Avg Degree",
                "Theta",
                "N | Sparsified N"
            ]
        )
        self.assertEqual(
            rows[1],
            [
                "001",
                "family_01",
                "network_a",
                "No",
                "Default",
                "LAPIN-off",
                "-",
                "0.1",
                "0.05",
                "100",
                "epsilon",
                "No",
                "20",
                "20",
                "0.25",
                "100 | 95"
            ]
        )

    def test_initialize_results_file_with_metric_dataclasses(self):
        with TemporaryDirectory() as temporary_dir:
            extrinsic_results = self._create_populated_dataclass(
                ExtrinsicMetrics,
                10
            )
            intrinsic_results = self._create_populated_dataclass(
                IntrinsicMetrics,
                30
            )
            computational_results = self._create_populated_dataclass(
                ComputationalMetrics,
                50
            )

            append_result = initialize_results_file(
                results_dir=temporary_dir,
                output_filename="results"
            )
            append_result(self._create_result(
                extrinsic_results=extrinsic_results,
                intrinsic_results=intrinsic_results,
                computational_results=computational_results
            ))

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "results.csv"
                )
            )

        expected_headers = [
            dataclass_field.metadata.get(
                "label",
                dataclass_field.name
            )
            for dataclass_field in fields(Result)
            if (
                    dataclass_field.name not in {
                "extrinsic_results",
                "intrinsic_results",
                "computational_results"
            }
                    and getattr(
                self._create_result(),
                dataclass_field.name
            ) is not None
            )
        ]
        expected_headers += [
            dataclass_field.metadata.get(
                "label",
                dataclass_field.name
            )
            for dataclass_field in fields(ExtrinsicMetrics)
        ]
        expected_headers += [
            dataclass_field.metadata.get(
                "label",
                dataclass_field.name
            )
            for dataclass_field in fields(IntrinsicMetrics)
        ]
        expected_headers += [
            dataclass_field.metadata.get(
                "label",
                dataclass_field.name
            )
            for dataclass_field in fields(ComputationalMetrics)
        ]

        base_result = self._create_result(
            extrinsic_results=extrinsic_results,
            intrinsic_results=intrinsic_results,
            computational_results=computational_results
        )
        expected_values = [
            str(_format_value(
                getattr(base_result, dataclass_field.name)
            ))
            for dataclass_field in fields(Result)
            if (
                    dataclass_field.name not in {
                "extrinsic_results",
                "intrinsic_results",
                "computational_results"
            }
                    and getattr(
                base_result,
                dataclass_field.name
            ) is not None
            )
        ]
        expected_values += [
            str(_format_value(
                getattr(extrinsic_results, dataclass_field.name)
            ))
            for dataclass_field in fields(ExtrinsicMetrics)
        ]
        expected_values += [
            str(_format_value(
                getattr(intrinsic_results, dataclass_field.name)
            ))
            for dataclass_field in fields(IntrinsicMetrics)
        ]
        expected_values += [
            str(_format_value(
                getattr(computational_results, dataclass_field.name)
            ))
            for dataclass_field in fields(ComputationalMetrics)
        ]

        self.assertEqual(rows[0], expected_headers)
        self.assertEqual(rows[1], expected_values)

    def test_multiple_results_are_appended(self):
        with TemporaryDirectory() as temporary_dir:
            append_result = initialize_results_file(
                results_dir=temporary_dir
            )

            append_result(self._create_result(
                id="001",
                network="network_a"
            ))
            append_result(self._create_result(
                id="002",
                network="network_b",
                overlapping=True
            ))

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "_results.csv"
                )
            )

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1][0], "001")
        self.assertEqual(rows[1][2], "network_a")
        self.assertEqual(rows[2][0], "002")
        self.assertEqual(rows[2][2], "network_b")
        self.assertEqual(rows[2][3], "Yes")

    def test_first_result_defines_the_csv_schema(self):
        with TemporaryDirectory() as temporary_dir:
            append_result = initialize_results_file(
                results_dir=temporary_dir
            )

            append_result(self._create_result())
            append_result(self._create_result(
                id="002",
                actual_average_degree=20.0
            ))

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "_results.csv"
                )
            )

        self.assertNotIn("Actual Avg Degree", rows[0])
        self.assertEqual(len(rows[1]), len(rows[0]))
        self.assertEqual(len(rows[2]), len(rows[0]))


if __name__ == "__main__":
    unittest.main()
