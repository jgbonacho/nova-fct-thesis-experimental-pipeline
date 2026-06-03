"""
Entry point.
"""

from pipeline.config.real_world_runner import config as real_world_runner
from pipeline.config.synthetic_runner import config as synthetic_runner
from pipeline.scripts.real_world_networks_runner import run_real_world_networks_experiments
from pipeline.scripts.synthetic_networks_runner import run_synthetic_networks_experiments


def main():
    # Synthetic Networks Experiments
    run_synthetic_networks_experiments(
        networks_base_dir=synthetic_runner.SYNTHETIC_NETWORKS_BASE_DIR,
        results_base_dir=synthetic_runner.RESULTS_BASE_DIR,
        network_family_configs=synthetic_runner.load_network_family_configs(synthetic_runner.CONFIG_DIR),
        thresholds=synthetic_runner.load_thresholds(synthetic_runner.CONFIG_DIR),
        affinity_designs=synthetic_runner.AFFINITY_DESIGNS,
        execution_modes=synthetic_runner.EXECUTION_MODES,
        defuzzification_rules=synthetic_runner.DEFUZZIFICATION_RULES
    )

    # Real-World Networks Experiments
    run_real_world_networks_experiments(
        results_base_dir=real_world_runner.RESULTS_BASE_DIR,
        network_family_configs=real_world_runner.load_network_family_configs(real_world_runner.CONFIG_DIR),
        thresholds=real_world_runner.load_thresholds(real_world_runner.CONFIG_DIR),
        affinity_designs=real_world_runner.AFFINITY_DESIGNS,
        execution_modes=real_world_runner.EXECUTION_MODES,
        defuzzification_rules=real_world_runner.DEFUZZIFICATION_RULES
    )


if __name__ == "__main__":
    main()
