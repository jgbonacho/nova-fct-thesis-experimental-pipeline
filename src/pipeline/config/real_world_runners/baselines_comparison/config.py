import os

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')

REAL_WORLD_NETWORKS_BASE_DIR = os.path.join(ROOT_DIR, 'networks', 'real-world', 'test')
WITH_GROUND_TRUTH_DIR = os.path.join(REAL_WORLD_NETWORKS_BASE_DIR, 'with-gt')
WITHOUT_GROUND_TRUTH_DIR = os.path.join(REAL_WORLD_NETWORKS_BASE_DIR, 'without-gt')

CONFIG_DIR = os.path.join(os.path.dirname(__file__))
NETWORK_FAMILIES_TEST_WITH_GT = "networks_families_test_with_gt.json"
NETWORK_FAMILIES_TEST_WITHOUT_GT = "networks_families_test_without_gt.json"

RESULTS_BASE_DIR = os.path.join(ROOT_DIR, 'results', 'real-world')