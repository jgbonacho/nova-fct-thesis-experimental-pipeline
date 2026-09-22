import os

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')

SYNTHETIC_NETWORKS_BASE_DIR = os.path.join(ROOT_DIR, 'networks', 'synthetic', 'test')
SYNTHETIC_NETWORKS_BVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'boundary_variation_set')
SYNTHETIC_NETWORKS_MVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'membership_variation_set')
SYNTHETIC_NETWORKS_OVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'overlap_variation_set')
SYNTHETIC_NETWORKS_IVS_BASE_DIR = os.path.join(SYNTHETIC_NETWORKS_BASE_DIR, 'interaction_variation_set')

CONFIG_DIR = os.path.join(os.path.dirname(__file__))
NETWORK_FAMILIES_BVS = "networks_families_bvs.json"
NETWORK_FAMILIES_MVS = "networks_families_mvs.json"
NETWORK_FAMILIES_OVS = "networks_families_ovs.json"
NETWORK_FAMILIES_IVS = "networks_families_ivs.json"

RESULTS_BASE_DIR = os.path.join(ROOT_DIR, 'results', 'synthetic')
