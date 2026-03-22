import time
import unittest

from pipeline.components.evaluation_metrics.computational.computational_metrics import get_computation_start_time, \
    get_computation_end_time, compute_computational_metrics


def aux_delay():
    time.sleep(0.5)


class Test(unittest.TestCase):

    def test_computational_metrics(self):
        start_time = get_computation_start_time()
        aux_delay()
        end_time = get_computation_end_time()
        results = compute_computational_metrics(start_time, end_time)

        self.assertTrue(results.runtime >= 0.5)


if __name__ == "__main__":
    unittest.main()
