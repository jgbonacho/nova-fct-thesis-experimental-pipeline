import csv
import json
import os

from pipeline.scripts.utils.networks_dataclasses import LFRNetworkFamilyConfig, NetworkFamilyConfig


def load_network_family_configs_for_synthetic_experiments(
        config_dir: str,
        input_filename: str
) -> list[LFRNetworkFamilyConfig]:
    """
    Load network families configs from JSON file.

    Parameters:
        config_dir : (str)
            Path to the directory containing the JSON file.
        input_filename : (str)
            Name of the JSON file.

    Returns:
        network_families_configs : (list[LFRNetworkFamilyConfig])
            List of network  configs.
    """
    with open(os.path.join(config_dir, input_filename), "r", encoding="utf-8") as in_file:
        json_network_families = json.load(in_file)

    return [LFRNetworkFamilyConfig.from_dict(json_network_family) for json_network_family in json_network_families]


def load_thresholds_for_synthetic_experiments(
        config_dir: str,
        input_filename: str = "thresholds.csv",
        network_families_key: str = "Network Family",
        thresholds_key: str = "Threshold"
) -> dict[str, float]:
    """
    Load thresholds from CSV file.

    Parameters:
        config_dir : (str)
            Path to the directory containing the CSV file.
        input_filename : (str, optional)
            Name of the CSV file.
            Default is "thresholds.csv".
        network_families_key : (str, optional)
            The key in the CSV file corresponding to the network family names.
            Default is "Network Family".
        thresholds_key : (str, optional)
            The key in the CSV file corresponding to the threshold values.
            Default is "Threshold".

    Returns:
        thresholds : (dict[str, float])
            Dictionary of thresholds keyed by network family.
    """

    thresholds = {}
    with open(os.path.join(config_dir, input_filename), "r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            thresholds[row[network_families_key]] = float(row[thresholds_key])
    return thresholds


def load_network_family_configs_for_real_world_experiments(
        config_dir: str,
        input_filename: str,
        with_ground_truth_dir: str,
        without_ground_truth_dir: str,
) -> list[NetworkFamilyConfig]:
    """
    Load network families configs from JSON file.

    Parameters:
        config_dir : (str)
            Path to the directory containing the JSON file.
        input_filename : (str)
            Name of the JSON file.

    Returns:
        network_families_configs : (list[NetworkFamilyConfig])
            List of network families configs.
    """
    with open(os.path.join(config_dir, input_filename), "r", encoding="utf-8") as in_file:
        json_network_families = json.load(in_file)

    return [
        NetworkFamilyConfig.from_dict(json_network_family, with_ground_truth_dir, without_ground_truth_dir)
        for json_network_family in json_network_families
    ]


def load_thresholds_for_real_world_experiments(
        config_dir: str,
        input_filename: str = "thresholds.csv",
        network_key: str = "Network",
        thresholds_key: str = "Threshold"
) -> dict[str, float]:
    """
    Load thresholds from CSV file.

    Parameters:
        config_dir : (str)
            Path to the directory containing the CSV file.
        input_filename : (str, optional)
            Name of the CSV file.
            Default is "thresholds.csv".
        network_key : (str, optional)
            The key in the CSV file corresponding to the network names.
            Default is "Network".
        thresholds_key : (str, optional)
            The key in the CSV file corresponding to the threshold values.
            Default is "Threshold".

    Returns:
        thresholds : (dict[str, float])
            Dictionary of thresholds keyed by network family.
    """

    thresholds = {}
    with open(os.path.join(config_dir, input_filename), "r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            thresholds[row[network_key]] = float(row[thresholds_key])
    return thresholds
