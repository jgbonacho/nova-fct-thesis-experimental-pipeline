import unittest
from dataclasses import asdict, fields

from pipeline.components.sparsification.sparsification_dataclass import SparsificationInfo


class TestSparsificationInfo(unittest.TestCase):

    def test_sparsification_info_stores_values(self):
        info = SparsificationInfo(
            theta=0.75,
            target_average_degree=20.0,
            actual_average_degree=19.4,
            diff_n="1000 | 980"
        )

        self.assertEqual(info.theta, 0.75)
        self.assertEqual(info.target_average_degree, 20.0)
        self.assertEqual(info.actual_average_degree, 19.4)
        self.assertEqual(info.diff_n, "1000 | 980")

    def test_sparsification_info_supports_skipped_sparsification_values(self):
        info = SparsificationInfo(
            theta="-",
            target_average_degree="-",
            actual_average_degree=7.5,
            diff_n="100 | 100"
        )

        self.assertEqual(info.theta, "-")
        self.assertEqual(info.target_average_degree, "-")
        self.assertEqual(info.actual_average_degree, 7.5)
        self.assertEqual(info.diff_n, "100 | 100")

    def test_sparsification_info_can_be_converted_to_dictionary(self):
        info = SparsificationInfo(
            theta=0.4,
            target_average_degree=10.0,
            actual_average_degree=9.8,
            diff_n="500 | 490"
        )

        self.assertEqual(
            asdict(info),
            {
                "theta": 0.4,
                "target_average_degree": 10.0,
                "actual_average_degree": 9.8,
                "diff_n": "500 | 490"
            }
        )

    def test_sparsification_info_field_labels(self):
        labels = {
            dataclass_field.name: dataclass_field.metadata["label"]
            for dataclass_field in fields(SparsificationInfo)
        }

        self.assertEqual(
            labels,
            {
                "theta": "Theta",
                "target_average_degree": "Target Avg Degree",
                "actual_average_degree": "Actual Avg Degree",
                "diff_n": "N | Sparsified N"
            }
        )

    def test_sparsification_info_equality(self):
        first = SparsificationInfo(
            theta=0.5,
            target_average_degree=20.0,
            actual_average_degree=19.9,
            diff_n="1000 | 995"
        )
        second = SparsificationInfo(
            theta=0.5,
            target_average_degree=20.0,
            actual_average_degree=19.9,
            diff_n="1000 | 995"
        )

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
