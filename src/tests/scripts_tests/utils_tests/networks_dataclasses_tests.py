import unittest

from pipeline.scripts.utils.networks_dataclasses import LFRNetworkConfig, LFRNetworkFamilyConfig, NetworkConfig, \
    NetworkFamilyConfig


class TestNetworksDataclasses(unittest.TestCase):

    def test_lfr_network_config_from_dict(self):
        data = {
            "description": "LFR test network",
            "instance": 3,
            "name": "network_03",
            "overlapping_ground_truth": True
        }

        config = LFRNetworkConfig.from_dict(data)

        self.assertEqual(config.description, "LFR test network")
        self.assertEqual(config.instance, 3)
        self.assertEqual(config.name, "network_03")
        self.assertTrue(config.overlapping_ground_truth)

    def test_lfr_network_family_config_from_dict(self):
        data = {
            "name": "family_01",
            "networks": [
                {
                    "description": "First network",
                    "instance": 1,
                    "name": "network_01",
                    "overlapping_ground_truth": False
                },
                {
                    "description": "Second network",
                    "instance": 2,
                    "name": "network_02",
                    "overlapping_ground_truth": True
                }
            ]
        }

        family_config = LFRNetworkFamilyConfig.from_dict(data)

        self.assertEqual(family_config.name, "family_01")
        self.assertEqual(len(family_config.network_configs), 2)
        self.assertIsInstance(
            family_config.network_configs[0],
            LFRNetworkConfig
        )
        self.assertEqual(
            family_config.network_configs[0].name,
            "network_01"
        )
        self.assertFalse(
            family_config.network_configs[0].overlapping_ground_truth
        )
        self.assertTrue(
            family_config.network_configs[1].overlapping_ground_truth
        )

    def test_network_config_from_dict_with_ground_truth(self):
        data = {
            "name": "zachary-karate-club",
            "gml_filename": "karate",
            "ground_truth": True,
            "overlapping_ground_truth": False,
            "ground_truth_attr": "community"
        }

        config = NetworkConfig.from_dict(data)

        self.assertEqual(config.name, "zachary-karate-club")
        self.assertEqual(config.gml_filename, "karate")
        self.assertTrue(config.ground_truth)
        self.assertFalse(config.overlapping_ground_truth)
        self.assertEqual(config.ground_truth_attr, "community")

    def test_network_config_from_dict_without_optional_ground_truth_fields(self):
        data = {
            "name": "network-without-ground-truth",
            "gml_filename": "network",
            "ground_truth": False
        }

        config = NetworkConfig.from_dict(data)

        self.assertEqual(
            config.name,
            "network-without-ground-truth"
        )
        self.assertEqual(config.gml_filename, "network")
        self.assertFalse(config.ground_truth)
        self.assertIsNone(config.overlapping_ground_truth)
        self.assertIsNone(config.ground_truth_attr)

    def test_network_family_config_uses_with_ground_truth_directory(self):
        data = {
            "name": "with-ground-truth",
            "ground_truth_family": True,
            "networks": [
                {
                    "name": "network_a",
                    "gml_filename": "network_a",
                    "ground_truth": True,
                    "overlapping_ground_truth": False,
                    "ground_truth_attr": "community"
                }
            ]
        }

        family_config = NetworkFamilyConfig.from_dict(
            data=data,
            with_ground_truth_dir="/networks/with-gt",
            without_ground_truth_dir="/networks/without-gt"
        )

        self.assertEqual(
            family_config.directory,
            "/networks/with-gt"
        )
        self.assertEqual(family_config.name, "with-ground-truth")
        self.assertEqual(len(family_config.network_configs), 1)
        self.assertIsInstance(
            family_config.network_configs[0],
            NetworkConfig
        )

    def test_network_family_config_uses_without_ground_truth_directory(self):
        data = {
            "name": "without-ground-truth",
            "ground_truth_family": False,
            "networks": [
                {
                    "name": "network_b",
                    "gml_filename": "network_b",
                    "ground_truth": False
                }
            ]
        }

        family_config = NetworkFamilyConfig.from_dict(
            data=data,
            with_ground_truth_dir="/networks/with-gt",
            without_ground_truth_dir="/networks/without-gt"
        )

        self.assertEqual(
            family_config.directory,
            "/networks/without-gt"
        )
        self.assertEqual(
            family_config.network_configs[0].name,
            "network_b"
        )
        self.assertIsNone(
            family_config.network_configs[0].ground_truth_attr
        )

    def test_missing_required_field_raises_key_error(self):
        incomplete_data = {
            "description": "Network",
            "instance": 1,
            "name": "network_a"
        }

        with self.assertRaises(KeyError):
            LFRNetworkConfig.from_dict(incomplete_data)


if __name__ == "__main__":
    unittest.main()
