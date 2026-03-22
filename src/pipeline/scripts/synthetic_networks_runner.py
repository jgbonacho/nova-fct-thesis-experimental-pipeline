import os.path

from pipeline.components.defuzzification.defuzzification import apply_defuzzification_rule
from pipeline.components.evaluation_metrics.computational.computational_metrics import compute_computational_metrics, \
    get_computation_start_time, get_computation_end_time
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics import compute_extrinsic_metrics
from pipeline.components.faddis.faddis import faddis
from pipeline.components.lapin.lapin import lapin
from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix
from pipeline.components.loaders.synthetic_data_loader import load_lfr_benchmark_network
from pipeline.components.stop_criterion.stop_criterion import set_stop_criterion
from pipeline.scripts.utils.result_dataclass import Result
from pipeline.scripts.utils.utils import create_results_dir, create_network_results_dir, log_progress, \
    initialize_results_file, save_report, save_faddis_clustering_results


def run_synthetic_networks_experiments(
        networks_base_dir,
        results_base_dir,
        network_families,
        thresholds,
        affinity_designs,
        execution_modes,
        defuzzification_rules
):
    """
    Run synthetic networks experiments.

    Parameters:
        networks_base_dir : (str)
            Path to the base directory containing the synthetic networks.
        results_base_dir : (str)
            Path to the base directory where results will be saved.
        network_families : (list)
            List of network families to be processed.
        thresholds : (dict)
            Dictionary containing threshold values, keyed by network family name.
        affinity_designs : (dict)
            Dictionary of affinity designs to be applied, keyed by design label.
        execution_modes : (list)
            List of execution modes to be applied.
        defuzzification_rules : (list)
            List of defuzzification rules to be applied.
    """

    results_dir = create_results_dir(results_base_dir)

    for idx1, network_family in enumerate(network_families, 1):
        log_progress(idx1, len(network_families), network_family.name, 5, True)

        for idx2, network in enumerate(network_family.networks, 1):
            log_progress(idx2, len(network_family.networks), network.name, 4, True)

            results_network_dir = create_network_results_dir(results_dir, network_family.name, network.name)

            append_result = initialize_results_file(results_network_dir)
            results_id = 0

            try:
                # 0. Load network.
                graph, ground_truth_labels, k = load_lfr_benchmark_network(
                    os.path.join(networks_base_dir, network_family.name), network.name,
                    overlapping_ground_truth=network.overlapping_ground_truth
                )

                for idx3, (affinity_design_label, affinity_matrix_lambda) in enumerate(affinity_designs.items(), 1):
                    log_progress(idx3, len(affinity_designs), affinity_design_label, 3)

                    for idx4, execution_mode in enumerate(execution_modes, 1):
                        log_progress(idx4, len(execution_modes), execution_mode.label, 2)

                        for idx5, defuzzification_rule in enumerate(defuzzification_rules, 1):
                            log_progress(idx5, len(defuzzification_rules), defuzzification_rule, 1)

                            # --- Start of the computation ---
                            start_time = get_computation_start_time()

                            # 1. Compute adjacency matrix A.
                            A = compute_adjacency_matrix(graph)

                            # 2. Compute the affinity matrix W from the matrix A.
                            W = affinity_matrix_lambda(A)

                            # 3. Apply sparsification to matrix W to obtain the matrix Ws.
                            Ws = W.copy()

                            # 4. If enabled, perform the LAPIN transformation on matrix Ws to produce the matrix Ln.
                            Ln = lapin(Ws, execution_mode.laplacian_variant) if execution_mode.apply_lapin else None

                            # 5. Fine-tune the stop criterion for FADDIS.
                            epsilon, tau, k_max = set_stop_criterion(
                                graph.number_of_nodes(), network_family.name, thresholds
                            )

                            # 6. Execute FADDIS.
                            results = faddis(Ws if not execution_mode.apply_lapin else Ln, epsilon, tau, k_max)

                            # 7. Apply a defuzzification rule to map fuzzy memberships to a binary [overlapping] community cover.
                            _, membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, stop_condition = results
                            predicted_labels, first_cluster_discarded = apply_defuzzification_rule(
                                membership_matrix,
                                defuzzification_rule.gamma,
                                defuzzification_rule.conditionally_discard_first_cluster,
                                overlapping=network.overlapping_ground_truth
                            )
                            k_predicted = number_of_clusters - 1 if first_cluster_discarded else number_of_clusters

                            end_time = get_computation_end_time()
                            # --- End of the computation ---

                            # 8. Compute the computational, intrinsic and extrinsic evaluation metrics.
                            computational_results = compute_computational_metrics(
                                start_time, end_time
                            )
                            extrinsic_results = compute_extrinsic_metrics(
                                graph, ground_truth_labels, predicted_labels, k, k_predicted,
                                overlapping=network.overlapping_ground_truth
                            )

                            results_id += 1
                            append_result(Result(
                                id=results_id,
                                network_family=network_family.name,
                                network=network.name,
                                overlapping=network.overlapping_ground_truth,
                                affinity_design=affinity_design_label,
                                execution_mode=execution_mode.label,
                                laplacian_variant=execution_mode.laplacian_variant,
                                epsilon=epsilon,
                                tau=tau,
                                k_max=k_max,
                                stop_condition=stop_condition,
                                gamma=defuzzification_rule.gamma,
                                conditionally_discard_first_cluster=defuzzification_rule.conditionally_discard_first_cluster,
                                first_cluster_discarded=first_cluster_discarded,
                                extrinsic_results=extrinsic_results,
                                computational_results=computational_results
                            ))

                            save_faddis_clustering_results(results_network_dir, results_id, results)
            except Exception as e:
                print(f"[ERROR] Network {network.name} processing failed with error: {e}")
                continue

    save_report(results_dir, network_families, thresholds, affinity_designs, execution_modes, defuzzification_rules)
