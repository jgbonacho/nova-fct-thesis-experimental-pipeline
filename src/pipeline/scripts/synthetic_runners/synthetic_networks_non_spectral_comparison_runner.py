import os.path

from pipeline.components.defuzzification.defuzzification import apply_defuzzification_rule
from pipeline.components.evaluation_metrics.computational.computational_metrics import get_computation_start_time, \
    get_computation_end_time, compute_computational_metrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics import compute_extrinsic_metrics
from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix
from pipeline.components.loaders.synthetic_data_loader import load_lfr_benchmark_network
from pipeline.components.stop_criterion.stop_criterion import set_stop_criterion
from pipeline.scripts.utils.algorithm_dataclass import Algorithm, wrapper_spectral_algorithm, \
    wrapper_non_spectral_algorithm
from pipeline.scripts.utils.comparison_result_dataclass import ComparisonResult, initialize_comparison_results_file
from pipeline.scripts.utils.networks_dataclasses import LFRNetworkFamilyConfig
from pipeline.scripts.utils.utils import create_results_dir, log_progress, create_network_results_dir

SPECTRAL_ALGORITHMS = [
    Algorithm.FADDIS
]

NON_SPECTRAL_ALGORITHMS = [
    Algorithm.SLPA,
    Algorithm.CFINDER,
]


def run_synthetic_networks_non_spectral_comparison_experiments(
        networks_base_dir: str,
        results_base_dir: str,
        network_family_configs: list[LFRNetworkFamilyConfig],
        thresholds: dict[str, float],
):
    """
    Run synthetic networks comparison experiments.

    Parameters:
        networks_base_dir : (str)
            Path to the base directory containing the synthetic networks.
        results_base_dir : (str)
            Path to the base directory where results will be saved.
        network_family_configs : (list[LFRNetworkFamilyConfig])
            List of network family configs to be processed.
        thresholds : (dict[str, float])
            Dictionary containing threshold values, keyed by network family name.

    Returns:
        results_dir : (str)
            The path to the results' directory.
    """

    algorithms = SPECTRAL_ALGORITHMS + NON_SPECTRAL_ALGORITHMS

    results_dir = create_results_dir(results_base_dir)

    for idx1, network_family_config in enumerate(network_family_configs, 1):
        log_progress(idx1, len(network_family_configs), network_family_config.name, 5, True)

        network_configs = sorted(network_family_config.network_configs, key=lambda n: n.name)
        for idx2, network_config in enumerate(network_configs, 1):
            log_progress(idx2, len(network_configs), network_config.name, 4, True)

            results_network_dir = create_network_results_dir(
                results_dir, network_family_config.name, network_config.name
            )

            append_result = initialize_comparison_results_file(results_network_dir)

            # 0. Load network.
            graph, ground_truth_labels, k = load_lfr_benchmark_network(
                os.path.join(networks_base_dir, network_family_config.name), network_config.name,
                overlapping_ground_truth=network_config.overlapping_ground_truth
            )

            for idx3, algorithm in enumerate(algorithms, 1):
                log_progress(idx3, len(algorithms), algorithm.value, 3)

                affinity_design = "-"
                execution_mode = "-"
                gamma = "-"
                first_cluster_discarded = "-"

                # ----------------------------------------- Start computation -----------------------------------------
                start_time = get_computation_start_time()

                if algorithm in SPECTRAL_ALGORITHMS:
                    affinity_design = "Default"
                    execution_mode = "LAPIN-off"
                    gamma = 0.8

                    # 1. Compute adjacency matrix A.
                    A = compute_adjacency_matrix(graph)

                    # 2. Compute the affinity matrix W from the matrix A.
                    W = A.copy()

                    # 3. Apply sparsification to matrix W to obtain the matrix Ws.
                    # Skipped

                    # 4. If enabled, perform the LAPIN transformation on matrix Ws to produce the matrix Ln.
                    # Skipped

                    # 5. Fine-tune the stop criterion for FADDIS.
                    epsilon, tau, k_max = set_stop_criterion(
                        graph.number_of_nodes(), network_family_config.name, thresholds
                    )

                    # 6. Execute algorithm.
                    faddis_stopping_criterion = (epsilon, tau, k_max)
                    membership_matrix = wrapper_spectral_algorithm(algorithm, W, k, faddis_stopping_criterion)

                    # 7. Apply a defuzzification rule to map fuzzy memberships to a binary [overlapping] community cover.
                    predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
                        membership_matrix,
                        gamma=gamma,
                        conditionally_discard_first_cluster=(algorithm == Algorithm.FADDIS),
                        overlapping=network_config.overlapping_ground_truth
                    )

                else:
                    predicted_labels, k_predicted = wrapper_non_spectral_algorithm(algorithm, graph)

                end_time = get_computation_end_time()
                # ------------------------------------------ End computation ------------------------------------------

                # 8. Compute the computational and extrinsic evaluation metrics.
                extrinsic_results = compute_extrinsic_metrics(
                    graph, ground_truth_labels, predicted_labels, k, k_predicted,
                    overlapping=network_config.overlapping_ground_truth
                )
                computational_results = compute_computational_metrics(start_time, end_time)

                append_result(ComparisonResult(
                    algorithm_name=algorithm.value,
                    network_family=network_family_config.name,
                    network=network_config.name,
                    overlapping=network_config.overlapping_ground_truth,
                    affinity_design=affinity_design,
                    execution_mode=execution_mode,
                    gamma=gamma,
                    first_cluster_discarded=first_cluster_discarded,
                    extrinsic_results=extrinsic_results,
                    computational_results=computational_results,
                    intrinsic_results=None
                ))

    return results_dir
