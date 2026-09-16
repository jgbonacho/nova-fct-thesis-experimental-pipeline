"""
Entry point.
"""

from pipeline.config.real_world_runners import config as real_world_runner
from pipeline.config.synthetic_runners import config as synthetic_runner
from pipeline.scripts.real_world_runners.real_world_networks_non_spectral_comparison_runner import \
    run_real_world_networks_non_spectral_comparison_experiments
from pipeline.scripts.real_world_runners.real_world_networks_runner import run_real_world_networks_experiments
from pipeline.scripts.real_world_runners.real_world_networks_spectral_comparison_runner import \
    run_real_world_networks_spectral_comparison_experiments
from pipeline.scripts.synthetic_runners.synthetic_networks_non_spectral_comparison_runner import \
    run_synthetic_networks_non_spectral_comparison_experiments
from pipeline.scripts.synthetic_runners.synthetic_networks_runner import run_synthetic_networks_experiments
from pipeline.scripts.synthetic_runners.synthetic_networks_spectral_comparison_runner import \
    run_synthetic_networks_spectral_comparison_experiments


def main(
        execute_synthetic_networks_experiments: bool = True,
        execute_synthetic_networks_spectral_comparison_experiments: bool = True,
        execute_synthetic_networks_non_spectral_comparison_experiments: bool = True,
        execute_real_world_networks_experiments: bool = True,
        execute_real_world_networks_spectral_comparison_experiments: bool = True,
        execute_real_world_networks_non_spectral_comparison_experiments: bool = True
):
    """
    Entry point.

    Parameters:
        execute_synthetic_networks_experiments : (bool, optional)
            Whether to execute the FADDIS experiments on synthetic networks.
            Default is True.
        execute_synthetic_networks_spectral_comparison_experiments : (bool, optional)
            Whether to execute the spectral baseline comparison experiments on synthetic networks.
            Default is True.
        execute_synthetic_networks_non_spectral_comparison_experiments : (bool, optional)
            Whether to execute the non-spectral baseline comparison experiments on synthetic networks.
            Default is True.
        execute_real_world_networks_experiments : (bool, optional)
            Whether to execute the FADDIS experiments on real-world networks.
            Default is True.
        execute_real_world_networks_spectral_comparison_experiments : (bool, optional)
            Whether to execute the spectral baseline comparison experiments on real-world networks.
            Default is True.
        execute_real_world_networks_non_spectral_comparison_experiments : (bool, optional)
            Whether to execute the non-spectral baseline comparison experiments on real-world networks.
            Default is True.
    """

    # Synthetic Networks Experiments.
    if execute_synthetic_networks_experiments:
        run_synthetic_networks_experiments(
            networks_base_dir=synthetic_runner.SYNTHETIC_NETWORKS_BASE_DIR,
            results_base_dir=synthetic_runner.RESULTS_BASE_DIR,
            network_family_configs=synthetic_runner.load_network_family_configs(synthetic_runner.CONFIG_DIR),
            thresholds=synthetic_runner.load_thresholds(synthetic_runner.CONFIG_DIR),
            affinity_designs=synthetic_runner.AFFINITY_DESIGNS,
            execution_modes=synthetic_runner.EXECUTION_MODES,
            defuzzification_rules=synthetic_runner.DEFUZZIFICATION_RULES
        )

    if execute_synthetic_networks_spectral_comparison_experiments:
        run_synthetic_networks_spectral_comparison_experiments(
            networks_base_dir=synthetic_runner.SYNTHETIC_NETWORKS_BASE_DIR,
            results_base_dir=synthetic_runner.RESULTS_BASE_DIR,
            network_family_configs=synthetic_runner.load_network_family_configs(synthetic_runner.CONFIG_DIR),
            number_of_seeds=5
        )

    if execute_synthetic_networks_non_spectral_comparison_experiments:
        run_synthetic_networks_non_spectral_comparison_experiments(
            networks_base_dir=synthetic_runner.SYNTHETIC_NETWORKS_BASE_DIR,
            results_base_dir=synthetic_runner.RESULTS_BASE_DIR,
            network_family_configs=synthetic_runner.load_network_family_configs(synthetic_runner.CONFIG_DIR),
            thresholds=synthetic_runner.load_thresholds(synthetic_runner.CONFIG_DIR),
            number_of_seeds=5,
        )

    # Real-World Networks Experiments
    if execute_real_world_networks_experiments:
        run_real_world_networks_experiments(
            results_base_dir=real_world_runner.RESULTS_BASE_DIR,
            network_family_configs=real_world_runner.load_network_family_configs(real_world_runner.CONFIG_DIR),
            thresholds=real_world_runner.load_thresholds(real_world_runner.CONFIG_DIR),
            affinity_designs=real_world_runner.AFFINITY_DESIGNS,
            execution_modes=real_world_runner.EXECUTION_MODES,
            defuzzification_rules=real_world_runner.DEFUZZIFICATION_RULES
        )

    if execute_real_world_networks_spectral_comparison_experiments:
        run_real_world_networks_spectral_comparison_experiments(
            results_base_dir=real_world_runner.RESULTS_BASE_DIR,
            network_family_configs=real_world_runner.load_network_family_configs(real_world_runner.CONFIG_DIR),
            thresholds=real_world_runner.load_thresholds(real_world_runner.CONFIG_DIR),
            number_of_seeds=5
        )

    if execute_real_world_networks_non_spectral_comparison_experiments:
        run_real_world_networks_non_spectral_comparison_experiments(
            results_base_dir=real_world_runner.RESULTS_BASE_DIR,
            network_family_configs=real_world_runner.load_network_family_configs(real_world_runner.CONFIG_DIR),
            thresholds=real_world_runner.load_thresholds(real_world_runner.CONFIG_DIR),
            number_of_seeds=5
        )


if __name__ == "__main__":
    main(
        execute_synthetic_networks_experiments=True,
        execute_synthetic_networks_spectral_comparison_experiments=True,
        execute_synthetic_networks_non_spectral_comparison_experiments=True,
        execute_real_world_networks_experiments=True,
        execute_real_world_networks_spectral_comparison_experiments=True,
        execute_real_world_networks_non_spectral_comparison_experiments=True
    )
