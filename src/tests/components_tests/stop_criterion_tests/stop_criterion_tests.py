import unittest

from pipeline.components.stop_criterion.stop_criterion import set_stop_criterion


class TestStopCriterion(unittest.TestCase):

    def test_stop_criterion_uses_experimental_threshold(self):
        epsilon, tau, k_max = set_stop_criterion(
            n=100,
            threshold_identifier="family_01",
            thresholds={
                "family_01": 0.025,
                "family_02": 0.05
            }
        )

        self.assertEqual(epsilon, 0.025)
        self.assertEqual(tau, 0.05)
        self.assertEqual(k_max, 50)

    def test_stop_criterion_uses_inverse_number_of_nodes_when_threshold_is_missing(self):
        epsilon, tau, k_max = set_stop_criterion(
            n=200,
            threshold_identifier="missing_family",
            thresholds={
                "family_01": 0.025
            }
        )

        self.assertEqual(epsilon, 1 / 200)
        self.assertEqual(tau, 0.05)
        self.assertEqual(k_max, 100)

    def test_zero_threshold_is_used(self):
        epsilon, tau, k_max = set_stop_criterion(
            n=20,
            threshold_identifier="family_01",
            thresholds={
                "family_01": 0.0
            }
        )

        self.assertEqual(epsilon, 0.0)
        self.assertEqual(tau, 0.05)
        self.assertEqual(k_max, 10)

    def test_k_max_is_limited_to_five_hundred(self):
        epsilon, tau, k_max = set_stop_criterion(
            n=2000,
            threshold_identifier="family_01",
            thresholds={}
        )

        self.assertEqual(epsilon, 1 / 2000)
        self.assertEqual(tau, 0.05)
        self.assertEqual(k_max, 500)

    def test_k_max_uses_integer_division_for_odd_number_of_nodes(self):
        _, _, k_max = set_stop_criterion(
            n=9,
            threshold_identifier="family_01",
            thresholds={}
        )

        self.assertEqual(k_max, 4)

    def test_single_node_graph(self):
        epsilon, tau, k_max = set_stop_criterion(
            n=1,
            threshold_identifier="family_01",
            thresholds={}
        )

        self.assertEqual(epsilon, 1.0)
        self.assertEqual(tau, 0.05)
        self.assertEqual(k_max, 0)

    def test_non_positive_number_of_nodes_raises_value_error(self):
        for n in (0, -1, -100):
            with self.subTest(n=n):
                with self.assertRaisesRegex(
                        ValueError,
                        "Number of nodes must be positive"
                ):
                    set_stop_criterion(
                        n=n,
                        threshold_identifier="family_01",
                        thresholds={}
                    )

    def test_threshold_dictionary_is_not_modified(self):
        thresholds = {
            "family_01": 0.025
        }
        original_thresholds = thresholds.copy()

        set_stop_criterion(
            n=100,
            threshold_identifier="family_01",
            thresholds=thresholds
        )

        self.assertEqual(
            thresholds,
            original_thresholds
        )


if __name__ == "__main__":
    unittest.main()
