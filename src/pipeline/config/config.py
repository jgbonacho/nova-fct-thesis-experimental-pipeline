import csv
import json
import os
from dataclasses import dataclass

from pipeline.components.affinity_design.default_affinity import default_affinity
from pipeline.scripts.utils.networks_dataclasses import NetworkFamily

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..')
SYNTHETIC_NETWORKS_BASE_DIR = os.path.join(ROOT_DIR, 'networks', 'synthetic', 'variation_sets', 'updated_size_variation_set')
RESULTS_BASE_DIR = os.path.join(ROOT_DIR, 'results', 'synthetic')
CONFIG_DIR = os.path.join(os.path.dirname(__file__))


def load_network_families(config_dir: str, input_filename: str = "networks_families.json") -> list[NetworkFamily]:
    """
    Load network families from JSON file.

    Parameters:
        config_dir : (str)
            Path to the directory containing the JSON file.
        input_filename : (str, optional)
            Name of the JSON file.
            Default is "networks_families.json".

    Returns:
        network_families : list[NetworkFamily]
            List of network families.
    """
    with open(os.path.join(config_dir, input_filename), "r", encoding="utf-8") as in_file:
        json_network_families = json.load(in_file)

    return [NetworkFamily.from_dict(json_network_family) for json_network_family in json_network_families]


# ----------------------------------------------------------------------------------------------------------------------


def load_thresholds(
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
        thresholds : dict[str, float]
            Dictionary of thresholds keyed by network family.
    """

    thresholds = {}
    with open(os.path.join(config_dir, input_filename), "r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            thresholds[row[network_families_key]] = float(row[thresholds_key])
    return thresholds


# ----------------------------------------------------------------------------------------------------------------------


AFFINITY_DESIGNS = {
    'Default': lambda A: default_affinity(A),
}


# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class ExecutionMode:
    """
    Dataclass for execution mode.

    Attributes:
        label : str
            The label for the execution mode.
        apply_lapin : bool
            Whether to apply LAPIN or not.
        laplacian_variant : str
            The variant of the Laplacian to apply if apply_lapin is True.
    """

    label: str
    apply_lapin: bool
    laplacian_variant: str


EXECUTION_MODES = [
    ExecutionMode('LAPIN-off', False, '-'),
    ExecutionMode('LAPIN-on', True, 'Lsym'),
    # ExecutionMode('LAPIN-on', True, 'Lrw'),
    # ExecutionMode('LAPIN-on', True, 'L'),
]


# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class DefuzzificationRule:
    """
    Dataclass for defuzzification rule.

    Attributes:
        gamma : float
            Hyperparameter for the defuzzification rule.
    """

    gamma: float


DEFUZZIFICATION_RULES = [
    DefuzzificationRule(0.3),
    DefuzzificationRule(0.5),
    DefuzzificationRule(0.6),
    DefuzzificationRule(0.7),
    DefuzzificationRule(0.8),
    DefuzzificationRule(0.9)
]
