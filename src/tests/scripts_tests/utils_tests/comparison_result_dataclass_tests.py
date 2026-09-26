import csv
import os
import unittest
from dataclasses import fields
from tempfile import TemporaryDirectory

from pipeline.components.evaluation_metrics.computational.computational_metrics_dataclass import ComputationalMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import IntrinsicMetrics
from pipeline.scripts.utils.comparison_result_dataclass import ComparisonResult, initialize_comparison_results_file
from pipeline.scripts.utils.utils import _format_value


class TestComparisonResult(unittest.TestCase):

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

    def test_default_values(self):
        result = ComparisonResult(
            algorithm_name="FADDIS",
            network="network_a",
            overlapping=False
        )

        self.assertEqual(result.algorithm_name, "FADDIS")
        self.assertEqual(result.network, "network_a")
        self.assertFalse(result.overlapping)
        self.assertIsNone(result.seeds)
        self.assertIsNone(result.affinity_design)
        self.assertIsNone(result.execution_mode)
        self.assertIsNone(result.faddis_epsilon)
        self.assertIsNone(result.njw_fcm_m)
        self.assertIsNone(result.slpa_t)
        self.assertIsNone(result.cfinder_clique_size)
        self.assertIsNone(result.extrinsic_results)
        self.assertIsNone(result.intrinsic_results)
        self.assertIsNone(result.computational_results)

    def test_field_labels(self):
        labels = {
            dataclass_field.name: dataclass_field.metadata.get("label")
            for dataclass_field in fields(ComparisonResult)
            if "label" in dataclass_field.metadata
        }

        self.assertEqual(labels["algorithm_name"], "Algorithm")
        self.assertEqual(labels["network"], "Network")
        self.assertEqual(labels["overlapping"], "Overlapping?")
        self.assertEqual(labels["seeds"], "Seeds")
        self.assertEqual(labels["faddis_epsilon"], "epsilon (FADDIS)")
        self.assertEqual(labels["njw_fcm_m"], "m (NJW+FCM)")
        self.assertEqual(labels["slpa_t"], "t (SLPA)")
        self.assertEqual(labels["cfinder_clique_size"], "k (CFinder)")

    def test_initialize_comparison_results_file_with_base_fields(self):
        with TemporaryDirectory() as temporary_dir:
            append_result = initialize_comparison_results_file(
                results_dir=temporary_dir
            )

            append_result(ComparisonResult(
                algorithm_name="SLPA",
                network="network_a",
                overlapping=True,
                seeds=(0, 1, 2),
                slpa_t=100,
                slpa_r=0.45
            ))

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "_comparison_results.csv"
                )
            )

        self.assertEqual(
            rows[0],
            [
                "Algorithm",
                "Network",
                "Overlapping?",
                "Seeds",
                "t (SLPA)",
                "r (SLPA)"
            ]
        )
        self.assertEqual(
            rows[1],
            [
                "SLPA",
                "network_a",
                "Yes",
                "(0, 1, 2)",
                "100",
                "0.45"
            ]
        )

    def test_initialize_comparison_results_file_with_metric_dataclasses(self):
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

            append_result = initialize_comparison_results_file(
                results_dir=temporary_dir,
                output_filename="comparison"
            )
            append_result(ComparisonResult(
                algorithm_name="FADDIS",
                network="network_a",
                overlapping=False,
                affinity_design="Default",
                execution_mode="LAPIN-off",
                extrinsic_results=extrinsic_results,
                intrinsic_results=intrinsic_results,
                computational_results=computational_results
            ))

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "comparison.csv"
                )
            )

        expected_headers = [
            "Algorithm",
            "Network",
            "Overlapping?",
            "Affinity Design",
            "Execution Mode"
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

        expected_values = [
            "FADDIS",
            "network_a",
            "No",
            "Default",
            "LAPIN-off"
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

    def test_first_result_defines_the_csv_schema(self):
        with TemporaryDirectory() as temporary_dir:
            append_result = initialize_comparison_results_file(
                results_dir=temporary_dir
            )

            append_result(ComparisonResult(
                algorithm_name="FADDIS",
                network="network_a",
                overlapping=False,
                affinity_design="Default"
            ))
            append_result(ComparisonResult(
                algorithm_name="NJW+FCM",
                network="network_b",
                overlapping=False,
                affinity_design="Dice",
                njw_fcm_m=2.0
            ))

            rows = self._read_csv(
                os.path.join(
                    temporary_dir,
                    "_comparison_results.csv"
                )
            )

        self.assertEqual(
            rows[0],
            [
                "Algorithm",
                "Network",
                "Overlapping?",
                "Affinity Design"
            ]
        )
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            rows[2],
            [
                "NJW+FCM",
                "network_b",
                "No",
                "Dice"
            ]
        )


if __name__ == "__main__":
    unittest.main()
