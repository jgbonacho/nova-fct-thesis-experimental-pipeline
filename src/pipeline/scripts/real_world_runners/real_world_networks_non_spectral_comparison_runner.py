import os.path

import numpy as np

from pipeline.components.affinity_design.affinity_design_dataclass import AffinityDesign
from pipeline.components.affinity_design.default_affinity import default_affinity
from pipeline.components.defuzzification.defuzzification import apply_defuzzification_rule
from pipeline.components.evaluation_metrics.computational.computational_metrics import get_computation_start_time, \
    get_computation_end_time, compute_computational_metrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics import compute_extrinsic_metrics, \
    compute_extrinsic_metrics_means_and_stds
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics import compute_intrinsic_metrics, \
    compute_intrinsic_metrics_means_and_stds
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import labels_to_membership_matrix
from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix
from pipeline.components.loaders.real_world_data_loader import load_network_from_gml
from pipeline.components.stop_criterion.stop_criterion import set_stop_criterion
from pipeline.scripts.utils.algorithm_dataclass import Algorithm
from pipeline.scripts.utils.comparison_result_dataclass import ComparisonResult, initialize_comparison_results_file
from pipeline.scripts.utils.networks_dataclasses import NetworkFamilyConfig
from pipeline.scripts.utils.utils import create_results_dir, log_progress, create_network_results_dir, \
    save_report_of_real_world_runner


def run_real_world_networks_non_spectral_comparison_experiments(
        results_base_dir: str,
        network_family_configs: list[NetworkFamilyConfig],
        thresholds: dict[str, float],
        number_of_seeds: int
) -> str:
    """
    Run real-world networks non-spectral comparison experiments.

    Parameters:
        results_base_dir : (str)
            Path to the base directory where results will be saved.
        network_family_configs : (list[NetworkFamilyConfig])
            List of network family configs to be processed.
        thresholds : (dict[str, float])
            Dictionary containing threshold values, keyed by network name.
        number_of_seeds : (int)
            Total number of seeds to be processed.

    Returns:
        results_dir : (str)
            The path to the results' directory.
    """

    results_dir = create_results_dir(results_base_dir)
    algorithms = [Algorithm.FADDIS, Algorithm.SLPA, Algorithm.CFINDER]

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
            graph, ground_truth_labels, k = load_network_from_gml(
                dir_path=os.path.join(network_family_config.directory, network_family_config.name),
                network_config=network_config
            )
            if network_config.ground_truth:
                if not network_config.overlapping_ground_truth:
                    network_config.overlapping_ground_truth = True
                    ground_truth_labels = [[label] for label in ground_truth_labels]
            else:
                network_config.overlapping_ground_truth = True
                extrinsic_results = None

            # 1. Compute adjacency matrix A.
            A = compute_adjacency_matrix(graph)

            for idx3, algorithm in enumerate(algorithms, 1):
                log_progress(idx3, len(algorithms), algorithm.value, 3)

                affinity_design, execution_mode, epsilon, tau, k_max, gamma = "-", "-", "-", "-", "-", "-"
                seeds, t, r, clique_size = "-", "-", "-", "-",

                start_time = get_computation_start_time()

                if algorithm == Algorithm.FADDIS:
                    affinity_design = AffinityDesign.DEFAULT.value
                    execution_mode = "LAPIN-off"

                    # 2. Compute the affinity matrix W from the matrix A.
                    W = default_affinity(A)

                    # 3. Apply sparsification to matrix W to obtain the matrix Ws.
                    # Skipped

                    # 4. If enabled, perform the LAPIN transformation on matrix Ws to produce the matrix Ln.
                    # Skipped

                    # 5. Fine-tune the stop criterion for FADDIS.
                    (epsilon, tau, k_max) = set_stop_criterion(
                        graph.number_of_nodes(), network_config.name, thresholds
                    )

                    # 6. Execute algorithm.
                    U = algorithm.execute_faddis(W=W, faddis_stopping_criterion=(epsilon, tau, k_max))

                    # 7. Apply a defuzzification rule to map fuzzy memberships to a binary [overlapping] community cover.
                    gamma = 0.8
                    predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
                        U=U, gamma=gamma, overlapping=network_config.overlapping_ground_truth
                    )

                    end_time = get_computation_end_time()

                    # 8. Compute the computational, intrinsic and extrinsic evaluation metrics.
                    if network_config.ground_truth:
                        extrinsic_results = compute_extrinsic_metrics(
                            graph=graph,
                            ground_truth_labels=ground_truth_labels,
                            predicted_labels=predicted_labels,
                            k=k,
                            k_predicted=k_predicted,
                            overlapping=network_config.overlapping_ground_truth
                        )
                    intrinsic_results = compute_intrinsic_metrics(
                        graph=graph,
                        A=A,
                        U=U if not first_cluster_discarded else np.asarray(U)[:, 1:],
                        predicted_labels=predicted_labels,
                        overlapping=network_config.overlapping_ground_truth
                    )
                    computational_results = compute_computational_metrics(start_time, end_time)

                elif algorithm == Algorithm.SLPA:
                    seeds, t, r = list(range(number_of_seeds)), 21, 0.1

                    U_results, predicted_labels_results, k_predicted_results = [], [], []
                    for seed in range(number_of_seeds):
                        # 6. Execute Algorithm.
                        predicted_labels, k_predicted = algorithm.execute_slpa(graph, t, r, seed)

                        U = labels_to_membership_matrix(predicted_labels, k_predicted)

                        U_results.append(U)
                        predicted_labels_results.append(predicted_labels)
                        k_predicted_results.append(k_predicted)

                    end_time = get_computation_end_time()

                    # 8. Compute the computational, intrinsic and extrinsic evaluation metrics.
                    if network_config.ground_truth:
                        extrinsic_results = compute_extrinsic_metrics_means_and_stds(
                            graph=graph,
                            ground_truth_labels=ground_truth_labels,
                            predicted_labels_results=predicted_labels_results,
                            k=k,
                            k_predicted_results=k_predicted_results,
                            overlapping=network_config.overlapping_ground_truth
                        )
                    intrinsic_results = compute_intrinsic_metrics_means_and_stds(
                        graph=graph,
                        A=A,
                        U_results=U_results,
                        predicted_labels_results=predicted_labels_results,
                        overlapping=network_config.overlapping_ground_truth
                    )
                    computational_results = compute_computational_metrics(start_time, end_time)

                elif algorithm == Algorithm.CFINDER:
                    clique_size = 5

                    predicted_labels, k_predicted = algorithm.execute_cfinder(graph, clique_size)
                    U = labels_to_membership_matrix(predicted_labels, k_predicted)

                    end_time = get_computation_end_time()

                    # 8. Compute the computational, intrinsic and extrinsic evaluation metrics.
                    if network_config.ground_truth:
                        extrinsic_results = compute_extrinsic_metrics(
                            graph=graph,
                            ground_truth_labels=ground_truth_labels,
                            predicted_labels=predicted_labels,
                            k=k,
                            k_predicted=k_predicted,
                            overlapping=network_config.overlapping_ground_truth
                        )
                    intrinsic_results = compute_intrinsic_metrics(
                        graph=graph,
                        A=A,
                        U=U,
                        predicted_labels=predicted_labels,
                        overlapping=network_config.overlapping_ground_truth
                    )
                    computational_results = compute_computational_metrics(start_time, end_time)

                else:
                    raise ValueError("[ERROR] Algorithm not supported.")

                append_result(ComparisonResult(
                    algorithm_name=str(algorithm.value),
                    network=network_config.name,
                    overlapping=network_config.overlapping_ground_truth,
                    affinity_design=affinity_design,
                    execution_mode=execution_mode,
                    faddis_epsilon=epsilon,
                    faddis_tau=tau,
                    faddis_k_max=k_max,
                    faddis_gamma=gamma,
                    seeds=seeds,
                    slpa_t=t,
                    slpa_r=r,
                    cfinder_clique_size=clique_size,
                    extrinsic_results=extrinsic_results,
                    intrinsic_results=intrinsic_results,
                    computational_results=computational_results
                ))

    save_report_of_real_world_runner(results_dir, network_family_configs)

    return results_dir
