import os

from pipeline.components.affinity_design.affinity_design_dataclass import AffinityDesign
from pipeline.components.affinity_design.default_affinity import default_affinity
from pipeline.config.utils.defuzzification_rule_dataclass import DefuzzificationRule
from pipeline.config.utils.execution_mode_dataclass import ExecutionMode

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')

REAL_WORLD_NETWORKS_BASE_DIR = os.path.join(ROOT_DIR, 'networks', 'real-world', 'validation')
WITH_GROUND_TRUTH_DIR = os.path.join(REAL_WORLD_NETWORKS_BASE_DIR, 'with-gt')
WITHOUT_GROUND_TRUTH_DIR = os.path.join(REAL_WORLD_NETWORKS_BASE_DIR, 'without-gt')

CONFIG_DIR = os.path.join(os.path.dirname(__file__))
NETWORK_FAMILIES_VALIDATION_WITH_GT = "networks_families_validation_with_gt.json"
NETWORK_FAMILIES_VALIDATION_WITHOUT_GT = "networks_families_validation_without_gt.json"

RESULTS_BASE_DIR = os.path.join(ROOT_DIR, 'results', 'real-world')

AFFINITY_DESIGNS = {
    AffinityDesign.DEFAULT: lambda A: default_affinity(A),
    # AffinityDesign.KUL: lambda A: compute_kul(A),
    # AffinityDesign.DICE: lambda A: compute_dice(A),
    # AffinityDesign.OCHIAI: lambda A: compute_ochiai(A),
    # AffinityDesign.IP_B0: lambda A: compute_ip(A, beta=0),
    # AffinityDesign.IP_B0_5: lambda A: compute_ip(A, beta=0.5),
    # AffinityDesign.IP_B1: lambda A: compute_ip(A, beta=1),
    # AffinityDesign.COSIP_B0: lambda A: compute_cosip(A, beta=0),
    # AffinityDesign.COSIP_B0_5: lambda A: compute_cosip(A, beta=0.5),
    # AffinityDesign.COSIP_B1: lambda A: compute_cosip(A, beta=1),
}

EXECUTION_MODES = [
    ExecutionMode('LAPIN-off', False),
    # ExecutionMode('LAPIN-on', True)
]

DEFUZZIFICATION_RULES = [
    DefuzzificationRule(0.3),
    DefuzzificationRule(0.5),
    DefuzzificationRule(0.6),
    DefuzzificationRule(0.7),
    DefuzzificationRule(0.8),
    DefuzzificationRule(0.9)
]
