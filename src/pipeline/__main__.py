"""
Entry point.
"""

from pipeline.config.real_world_runners.baselines_comparison import config as baselines_comparison_real_world_runner
from pipeline.config.real_world_runners.experimental_pipeline import config as experimental_pipeline_real_world_runner
from pipeline.config.synthetic_runners.baselines_comparison import config as baselines_comparison_synthetic_runner
from pipeline.config.synthetic_runners.experimental_pipeline import config as experimental_pipeline_synthetic_runner
from pipeline.config.utils.loaders import load_network_family_configs_for_synthetic_experiments, \
    load_thresholds_for_synthetic_experiments, load_network_family_configs_for_real_world_experiments, \
    load_thresholds_for_real_world_experiments
from pipeline.scripts.real_world_runners.baselines_comparison.real_world_networks_non_spectral_comparison_runner import \
    run_real_world_networks_non_spectral_comparison_experiments
from pipeline.scripts.real_world_runners.baselines_comparison.real_world_networks_spectral_comparison_runner import \
    run_real_world_networks_spectral_comparison_experiments
from pipeline.scripts.real_world_runners.experimental_pipeline.real_world_networks_runner import \
    run_real_world_networks_experiments
from pipeline.scripts.synthetic_runners.baselines_comparison.synthetic_networks_non_spectral_comparison_runner import \
    run_synthetic_networks_non_spectral_comparison_experiments
from pipeline.scripts.synthetic_runners.baselines_comparison.synthetic_networks_spectral_comparison_runner import \
    run_synthetic_networks_spectral_comparison_experiments
from pipeline.scripts.synthetic_runners.experimental_pipeline.synthetic_networks_runner import \
    run_synthetic_networks_experiments


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
            networks_base_dir=experimental_pipeline_synthetic_runner.SYNTHETIC_NETWORKS_BVS_BASE_DIR,
            results_base_dir=experimental_pipeline_synthetic_runner.RESULTS_BASE_DIR,
            network_family_configs=load_network_family_configs_for_synthetic_experiments(
                config_dir=experimental_pipeline_synthetic_runner.CONFIG_DIR,
                input_filename=experimental_pipeline_synthetic_runner.NETWORK_FAMILIES_BVS
            ),
            thresholds=load_thresholds_for_synthetic_experiments(experimental_pipeline_synthetic_runner.CONFIG_DIR),
            affinity_designs=experimental_pipeline_synthetic_runner.AFFINITY_DESIGNS,
            execution_modes=experimental_pipeline_synthetic_runner.EXECUTION_MODES,
            defuzzification_rules=experimental_pipeline_synthetic_runner.DEFUZZIFICATION_RULES
        )

    # ----

    if execute_synthetic_networks_spectral_comparison_experiments:
        run_synthetic_networks_spectral_comparison_experiments(
            networks_base_dir=baselines_comparison_synthetic_runner.SYNTHETIC_NETWORKS_BVS_BASE_DIR,
            results_base_dir=baselines_comparison_synthetic_runner.RESULTS_BASE_DIR,
            network_family_configs=load_network_family_configs_for_synthetic_experiments(
                config_dir=baselines_comparison_synthetic_runner.CONFIG_DIR,
                input_filename=baselines_comparison_synthetic_runner.NETWORK_FAMILIES_BVS
            ),
            number_of_seeds=5
        )

    if execute_synthetic_networks_non_spectral_comparison_experiments:
        run_synthetic_networks_non_spectral_comparison_experiments(
            networks_base_dir=baselines_comparison_synthetic_runner.SYNTHETIC_NETWORKS_BVS_BASE_DIR,
            results_base_dir=baselines_comparison_synthetic_runner.RESULTS_BASE_DIR,
            network_family_configs=load_network_family_configs_for_synthetic_experiments(
                config_dir=baselines_comparison_synthetic_runner.CONFIG_DIR,
                input_filename=baselines_comparison_synthetic_runner.NETWORK_FAMILIES_BVS
            ),
            thresholds=load_thresholds_for_synthetic_experiments(baselines_comparison_synthetic_runner.CONFIG_DIR),
            number_of_seeds=5,
        )

    # Real-World Networks Experiments.
    if execute_real_world_networks_experiments:
        run_real_world_networks_experiments(
            results_base_dir=experimental_pipeline_real_world_runner.RESULTS_BASE_DIR,
            network_family_configs=load_network_family_configs_for_real_world_experiments(
                config_dir=experimental_pipeline_real_world_runner.CONFIG_DIR,
                input_filename=experimental_pipeline_real_world_runner.NETWORK_FAMILIES_VALIDATION_WITHOUT_GT,
                with_ground_truth_dir=experimental_pipeline_real_world_runner.WITH_GROUND_TRUTH_DIR,
                without_ground_truth_dir=experimental_pipeline_real_world_runner.WITHOUT_GROUND_TRUTH_DIR
            ),
            thresholds=load_thresholds_for_real_world_experiments(experimental_pipeline_real_world_runner.CONFIG_DIR),
            affinity_designs=experimental_pipeline_real_world_runner.AFFINITY_DESIGNS,
            execution_modes=experimental_pipeline_real_world_runner.EXECUTION_MODES,
            defuzzification_rules=experimental_pipeline_real_world_runner.DEFUZZIFICATION_RULES
        )

    # ----

    if execute_real_world_networks_spectral_comparison_experiments:
        run_real_world_networks_spectral_comparison_experiments(
            results_base_dir=baselines_comparison_real_world_runner.RESULTS_BASE_DIR,
            network_family_configs=load_network_family_configs_for_real_world_experiments(
                config_dir=baselines_comparison_real_world_runner.CONFIG_DIR,
                input_filename=baselines_comparison_real_world_runner.NETWORK_FAMILIES_TEST_WITHOUT_GT,
                with_ground_truth_dir=baselines_comparison_real_world_runner.WITH_GROUND_TRUTH_DIR,
                without_ground_truth_dir=baselines_comparison_real_world_runner.WITHOUT_GROUND_TRUTH_DIR
            ),
            thresholds=load_thresholds_for_real_world_experiments(baselines_comparison_real_world_runner.CONFIG_DIR),
            number_of_seeds=5
        )

    if execute_real_world_networks_non_spectral_comparison_experiments:
        run_real_world_networks_non_spectral_comparison_experiments(
            results_base_dir=baselines_comparison_real_world_runner.RESULTS_BASE_DIR,
            network_family_configs=load_network_family_configs_for_real_world_experiments(
                config_dir=baselines_comparison_real_world_runner.CONFIG_DIR,
                input_filename=baselines_comparison_real_world_runner.NETWORK_FAMILIES_TEST_WITHOUT_GT,
                with_ground_truth_dir=baselines_comparison_real_world_runner.WITH_GROUND_TRUTH_DIR,
                without_ground_truth_dir=baselines_comparison_real_world_runner.WITHOUT_GROUND_TRUTH_DIR
            ),
            thresholds=load_thresholds_for_real_world_experiments(baselines_comparison_real_world_runner.CONFIG_DIR),
            number_of_seeds=5
        )


if __name__ == "__main__":
    main(
        execute_synthetic_networks_experiments=True,
        execute_synthetic_networks_spectral_comparison_experiments=True,
        execute_synthetic_networks_non_spectral_comparison_experiments=True,
        execute_real_world_networks_experiments=False,
        execute_real_world_networks_spectral_comparison_experiments=True,
        execute_real_world_networks_non_spectral_comparison_experiments=True
    )
