import csv
import json
import os

from pipeline.components.affinity_design.affinity_design_dataclass import AffinityDesign
from pipeline.components.affinity_design.default_affinity import default_affinity
from pipeline.components.affinity_design.neighborhood_based_similarities.binary_set_similarities import compute_kul, \
    compute_dice, compute_ochiai
from pipeline.components.affinity_design.neighborhood_based_similarities.weighted_inner_product_similarities import \
    compute_ip, compute_cosip
from pipeline.config.utils.defuzzification_rule_dataclass import DefuzzificationRule
from pipeline.config.utils.execution_mode_dataclass import ExecutionMode
from pipeline.scripts.utils.networks_dataclasses import LFRNetworkFamilyConfig

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
SYNTHETIC_NETWORKS_BASE_DIR = os.path.join(
    ROOT_DIR, 'networks', 'synthetic', 'variation_sets', 'boundary_variation_set'
)
RESULTS_BASE_DIR = os.path.join(ROOT_DIR, 'results', 'synthetic')
CONFIG_DIR = os.path.join(os.path.dirname(__file__))

AFFINITY_DESIGNS = {
    AffinityDesign.DEFAULT: lambda A: default_affinity(A),
    AffinityDesign.KUL: lambda A: compute_kul(A),
    AffinityDesign.DICE: lambda A: compute_dice(A),
    AffinityDesign.OCHIAI: lambda A: compute_ochiai(A),
    AffinityDesign.IP_B0: lambda A: compute_ip(A, beta=0),
    AffinityDesign.IP_B0_5: lambda A: compute_ip(A, beta=0.5),
    AffinityDesign.IP_B1: lambda A: compute_ip(A, beta=1),
    AffinityDesign.COSIP_B0: lambda A: compute_cosip(A, beta=0),
    AffinityDesign.COSIP_B0_5: lambda A: compute_cosip(A, beta=0.5),
    AffinityDesign.COSIP_B1: lambda A: compute_cosip(A, beta=1),
}

EXECUTION_MODES = [
    ExecutionMode('LAPIN-off', False),
    ExecutionMode('LAPIN-on', True)
]

DEFUZZIFICATION_RULES = [
    DefuzzificationRule(0.3),
    DefuzzificationRule(0.5),
    DefuzzificationRule(0.6),
    DefuzzificationRule(0.7),
    DefuzzificationRule(0.8),
    DefuzzificationRule(0.9)
]


def load_network_family_configs(
        config_dir: str,
        input_filename: str = "networks_families.json"
) -> list[LFRNetworkFamilyConfig]:
    """
    Load network families configs from JSON file.

    Parameters:
        config_dir : (str)
            Path to the directory containing the JSON file.
        input_filename : (str, optional)
            Name of the JSON file.
            Default is "networks_families.json".

    Returns:
        network_families_configs : (list[LFRNetworkFamilyConfig])
            List of network  configs.
    """
    with open(os.path.join(config_dir, input_filename), "r", encoding="utf-8") as in_file:
        json_network_families = json.load(in_file)

    return [LFRNetworkFamilyConfig.from_dict(json_network_family) for json_network_family in json_network_families]


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
        thresholds : (dict[str, float])
            Dictionary of thresholds keyed by network family.
    """

    thresholds = {}
    with open(os.path.join(config_dir, input_filename), "r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            thresholds[row[network_families_key]] = float(row[thresholds_key])
    return thresholds
