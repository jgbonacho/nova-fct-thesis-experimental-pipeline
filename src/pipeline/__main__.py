"""
Entry point.
"""

from pipeline.config.config import SYNTHETIC_NETWORKS_BASE_DIR, CONFIG_DIR, RESULTS_BASE_DIR, load_network_families, \
    load_thresholds, AFFINITY_DESIGNS, EXECUTION_MODES, DEFUZZIFICATION_RULES
from pipeline.scripts.synthetic_networks_runner import run_synthetic_networks_experiments


def main():
    run_synthetic_networks_experiments(
        networks_base_dir=SYNTHETIC_NETWORKS_BASE_DIR,
        results_base_dir=RESULTS_BASE_DIR,
        network_families=load_network_families(CONFIG_DIR),
        thresholds=load_thresholds(CONFIG_DIR),
        affinity_designs=AFFINITY_DESIGNS,
        execution_modes=EXECUTION_MODES,
        defuzzification_rules=DEFUZZIFICATION_RULES
    )


if __name__ == "__main__":
    main()
