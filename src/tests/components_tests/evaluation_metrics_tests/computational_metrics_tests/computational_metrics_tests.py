import unittest
from dataclasses import fields
from unittest.mock import patch

from pipeline.components.evaluation_metrics.computational import computational_metrics as metrics_module
from pipeline.components.evaluation_metrics.computational.computational_metrics_dataclass import ComputationalMetrics


class TestComputationalMetrics(unittest.TestCase):

    @patch.object(metrics_module, "_get_current_time", return_value=12.5)
    def test_get_computation_start_time(self, mocked_get_current_time):
        start_time = metrics_module.get_computation_start_time()

        self.assertEqual(start_time, 12.5)
        mocked_get_current_time.assert_called_once_with()

    @patch.object(metrics_module, "_get_current_time", return_value=18.75)
    def test_get_computation_end_time(self, mocked_get_current_time):
        end_time = metrics_module.get_computation_end_time()

        self.assertEqual(end_time, 18.75)
        mocked_get_current_time.assert_called_once_with()

    @patch.object(metrics_module.time, "perf_counter", return_value=42.25)
    def test_get_current_time_uses_performance_counter(self, mocked_perf_counter):
        current_time = metrics_module._get_current_time()

        self.assertEqual(current_time, 42.25)
        mocked_perf_counter.assert_called_once_with()

    def test_compute_runtime(self):
        self.assertAlmostEqual(
            metrics_module._compute_runtime(
                start_time=10.25,
                end_time=13.75
            ),
            3.5
        )

    def test_compute_runtime_can_be_zero(self):
        self.assertEqual(
            metrics_module._compute_runtime(
                start_time=5.0,
                end_time=5.0
            ),
            0.0
        )

    def test_compute_computational_metrics(self):
        metrics = metrics_module.compute_computational_metrics(
            start_time=20.0,
            end_time=22.75
        )

        self.assertIsInstance(metrics, ComputationalMetrics)
        self.assertEqual(metrics.runtime, 2.75)

    def test_computational_metrics_field_metadata(self):
        self.assertEqual(
            [
                dataclass_field.metadata["label"]
                for dataclass_field in fields(ComputationalMetrics)
            ],
            ["FADDIS Runtime"]
        )


if __name__ == "__main__":
    unittest.main()
