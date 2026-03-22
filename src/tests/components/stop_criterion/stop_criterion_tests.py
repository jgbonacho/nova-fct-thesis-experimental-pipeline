import unittest

from pipeline.components.stop_criterion.stop_criterion import set_stop_criterion


class Test(unittest.TestCase):

    def test_stop_criterion(self):
        epsilon, tau, k_max = set_stop_criterion(1000, "", {})

        self.assertEqual(epsilon, 1 / 1000)
        self.assertEqual(tau, 0.05)
        self.assertEqual(k_max, 100)

    def test_stop_criterion_invalid_number_of_nodes(self):
        self.assertRaises(ValueError, set_stop_criterion, 0, "", {})
        self.assertRaises(ValueError, set_stop_criterion, -1, "", {})


if __name__ == "__main__":
    unittest.main()
