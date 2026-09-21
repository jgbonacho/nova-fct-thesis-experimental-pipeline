import os

from pipeline.components.affinity_design.affinity_design_dataclass import AffinityDesign
from pipeline.components.affinity_design.default_affinity import default_affinity
from pipeline.components.affinity_design.neighborhood_based_similarities.binary_set_similarities import compute_kul, \
    compute_dice, compute_ochiai
from pipeline.components.affinity_design.neighborhood_based_similarities.weighted_inner_product_similarities import \
    compute_ip, compute_cosip
from pipeline.config.utils.defuzzification_rule_dataclass import DefuzzificationRule
from pipeline.config.utils.execution_mode_dataclass import ExecutionMode

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')

SYNTHETIC_NETWORKS_BASE_DIR = os.path.join(ROOT_DIR, 'networks', 'synthetic', 'validation')
SYNTHETIC_NETWORKS_BVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'boundary_variation_set')
SYNTHETIC_NETWORKS_MVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'membership_variation_set')
SYNTHETIC_NETWORKS_OVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'overlap_variation_set')
SYNTHETIC_NETWORKS_SVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'size_variation_set')
SYNTHETIC_NETWORKS_UPDATED_SVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'updated_size_variation_set')

CONFIG_DIR = os.path.join(os.path.dirname(__file__))
NETWORK_FAMILIES_BVS = "networks_families_bvs.json"
NETWORK_FAMILIES_MVS = "networks_families_mvs.json"
NETWORK_FAMILIES_OVS = "networks_families_ovs.json"
NETWORK_FAMILIES_SVS = "networks_families_svs.json"
NETWORK_FAMILIES_UPDATED_SVS = "networks_families_updated_svs.json"

RESULTS_BASE_DIR = os.path.join(ROOT_DIR, 'results', 'synthetic')

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
