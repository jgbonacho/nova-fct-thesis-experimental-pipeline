import unittest
from unittest.mock import patch

import networkx as nx
import numpy as np
import pipeline.scripts.utils.algorithm_dataclass as algorithm_module
from pipeline.scripts.utils.algorithm_dataclass import Algorithm


class TestAlgorithm(unittest.TestCase):

    def test_algorithm_values(self):
        self.assertEqual(Algorithm.FADDIS.value, "FADDIS")
        self.assertEqual(Algorithm.NJW_FCM.value, "NJW+FCM")
        self.assertEqual(Algorithm.SLPA.value, "SLPA")
        self.assertEqual(Algorithm.CFINDER.value, "CFinder")

    def test_execute_faddis_with_desired_k(self):
        W = np.array(
            [[0.0, 1.0],
             [1.0, 0.0]]
        )
        expected_U = np.array(
            [[0.8, 0.2],
             [0.2, 0.8]]
        )

        with patch.object(
                algorithm_module,
                "faddis",
                return_value=(
                        expected_U,
                        np.array([0.6, 0.4]),
                        np.empty((2, 2)),
                        np.empty(2),
                        2,
                        "desiredK"
                )
        ) as mocked_faddis:
            U = Algorithm.FADDIS.execute_faddis(
                W=W,
                k=2
            )

        mocked_faddis.assert_called_once_with(
            W=W,
            desired_k=3
        )
        np.testing.assert_array_equal(U, expected_U)

    def test_execute_faddis_with_stopping_criterion(self):
        W = np.array(
            [[0.0, 0.5],
             [0.5, 0.0]]
        )
        expected_U = np.array(
            [[0.7],
             [0.3]]
        )

        with patch.object(
                algorithm_module,
                "faddis",
                return_value=(
                        expected_U,
                        np.array([1.0]),
                        np.empty((1, 2)),
                        np.empty(1),
                        1,
                        "epsilon"
                )
        ) as mocked_faddis:
            U = Algorithm.FADDIS.execute_faddis(
                W=W,
                faddis_stopping_criterion=(0.1, 0.05, 50)
            )

        mocked_faddis.assert_called_once_with(
            W=W,
            epsilon=0.1,
            tau=0.05,
            k_max=50
        )
        np.testing.assert_array_equal(U, expected_U)

    def test_execute_faddis_rejects_invalid_parameter_combinations(self):
        W = np.eye(2)

        invalid_parameters = [
            {"k": None, "faddis_stopping_criterion": None},
            {"k": 2, "faddis_stopping_criterion": (0.1, 0.05, 50)}
        ]

        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters):
                with self.assertRaisesRegex(
                        Exception,
                        "Algorithm parameters are invalid"
                ):
                    Algorithm.FADDIS.execute_faddis(
                        W=W,
                        **parameters
                    )

    def test_execute_faddis_rejects_wrong_algorithm(self):
        with self.assertRaisesRegex(
                Exception,
                "Algorithm is not FADDIS"
        ):
            Algorithm.SLPA.execute_faddis(
                W=np.eye(2),
                k=2
            )

    def test_execute_njw_fcm(self):
        W = np.array(
            [[0.0, 1.0],
             [1.0, 0.0]]
        )
        expected_U = np.array(
            [[0.9, 0.1],
             [0.1, 0.9]]
        )

        with patch.object(
                algorithm_module,
                "njw_fcm",
                return_value=expected_U
        ) as mocked_njw_fcm:
            U = Algorithm.NJW_FCM.execute_njw_fcm(
                W=W,
                k=2,
                fcm_m=2.0,
                fcm_error=1e-5,
                fcm_max_iter=300,
                fcm_seed=7
            )

        mocked_njw_fcm.assert_called_once_with(
            W,
            2,
            2.0,
            1e-5,
            300,
            7
        )
        np.testing.assert_array_equal(U, expected_U)

    def test_execute_njw_fcm_rejects_wrong_algorithm(self):
        with self.assertRaisesRegex(
                Exception,
                r"Algorithm is not NJW\+FCM"
        ):
            Algorithm.FADDIS.execute_njw_fcm(
                W=np.eye(2),
                k=2,
                fcm_m=2.0,
                fcm_error=1e-5,
                fcm_max_iter=300,
                fcm_seed=0
            )

    def test_execute_slpa(self):
        graph = nx.path_graph(4)
        expected_result = (
            [[0], [0, 1], [1], [-1]],
            2
        )

        with patch.object(
                algorithm_module,
                "slpa",
                return_value=expected_result
        ) as mocked_slpa:
            result = Algorithm.SLPA.execute_slpa(
                graph=graph,
                t=100,
                r=0.45,
                seed=11
            )

        mocked_slpa.assert_called_once_with(
            graph,
            100,
            0.45,
            11
        )
        self.assertEqual(result, expected_result)

    def test_execute_slpa_rejects_wrong_algorithm(self):
        with self.assertRaisesRegex(
                Exception,
                "Algorithm is not SLPA"
        ):
            Algorithm.CFINDER.execute_slpa(
                graph=nx.path_graph(3),
                t=100,
                r=0.45,
                seed=0
            )

    def test_execute_cfinder(self):
        graph = nx.complete_graph(4)
        expected_result = (
            [[0], [0], [0], [0]],
            1
        )

        with patch.object(
                algorithm_module,
                "cfinder",
                return_value=expected_result
        ) as mocked_cfinder:
            result = Algorithm.CFINDER.execute_cfinder(
                graph=graph,
                clique_size=3
            )

        mocked_cfinder.assert_called_once_with(
            graph,
            3
        )
        self.assertEqual(result, expected_result)

    def test_execute_cfinder_rejects_wrong_algorithm(self):
        with self.assertRaisesRegex(
                Exception,
                "Algorithm is not CFinder"
        ):
            Algorithm.SLPA.execute_cfinder(
                graph=nx.complete_graph(3),
                clique_size=3
            )


if __name__ == "__main__":
    unittest.main()
