import os.path

from pipeline.components.defuzzification.defuzzification import apply_defuzzification_rule
from pipeline.components.evaluation_metrics.computational.computational_metrics import get_computation_start_time, \
    get_computation_end_time, compute_computational_metrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics import compute_extrinsic_metrics
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics import compute_intrinsic_metrics
from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix
from pipeline.components.loaders.synthetic_data_loader import load_lfr_benchmark_network
from pipeline.scripts.baselines.algorithm_dataclass import Algorithm
from pipeline.scripts.baselines.comparison_result_dataclass import ComparisonResult
from pipeline.scripts.baselines.utils import initialize_comparison_results_file, wrapper_spectral_algorithm
from pipeline.scripts.utils.networks_dataclasses import LFRNetworkFamilyConfig
from pipeline.scripts.utils.utils import create_results_dir, log_progress, create_network_results_dir


def run_synthetic_networks_spectral_comparison_experiments(
        networks_base_dir: str,
        results_base_dir: str,
        network_family_configs: list[LFRNetworkFamilyConfig],
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

    Returns:
        results_dir : (str)
            The path to the results' directory.
    """

    affinity_design = "Default"
    execution_mode = "LAPIN-off"
    algorithms = [Algorithm.FADDIS, Algorithm.NJW_FCM]

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

            try:
                # 0. Load network.
                graph, ground_truth_labels, k = load_lfr_benchmark_network(
                    os.path.join(networks_base_dir, network_family_config.name), network_config.name,
                    overlapping_ground_truth=network_config.overlapping_ground_truth
                )

                for gamma in [0.3, 0.5, 0.8]:
                    for idx3, algorithm in enumerate(algorithms, 1):
                        log_progress(idx3, len(algorithms), algorithm.value, 3)

                        # ----------------------------------------- Start computation -----------------------------------------
                        start_time = get_computation_start_time()
                        # 1. Compute adjacency matrix A.
                        A = compute_adjacency_matrix(graph)

                        # 2. Compute the affinity matrix W from the matrix A.
                        W = A.copy()

                        # 3. Apply sparsification to matrix W to obtain the matrix Ws.
                        # Skipped

                        # 4. If enabled, perform the LAPIN transformation on matrix Ws to produce the matrix Ln.
                        # Skipped

                        # 5. Fine-tune the stop criterion for FADDIS.
                        # Skipped

                        # 6. Execute Algorithm.
                        membership_matrix = wrapper_spectral_algorithm(algorithm, W, k)

                        # 7. Apply a defuzzification rule to map fuzzy memberships to a binary [overlapping] community cover.
                        predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
                            membership_matrix,
                            gamma=gamma,
                            conditionally_discard_first_cluster=(algorithm == Algorithm.FADDIS),
                            overlapping=network_config.overlapping_ground_truth
                        )

                        end_time = get_computation_end_time()
                        # ------------------------------------------ End computation ------------------------------------------

                        # 8. Compute the computational, intrinsic and extrinsic evaluation metrics.
                        extrinsic_results = compute_extrinsic_metrics(
                            graph, ground_truth_labels, predicted_labels, k, k_predicted,
                            overlapping=network_config.overlapping_ground_truth
                        )
                        intrinsic_results = compute_intrinsic_metrics(
                            graph, A, membership_matrix, predicted_labels,
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
                            intrinsic_results=intrinsic_results,
                            computational_results=computational_results,
                        ))

            except Exception as e:
                print(f"[ERROR] Network {network_config.name} processing failed with error: {e}")
                continue

    return results_dir
