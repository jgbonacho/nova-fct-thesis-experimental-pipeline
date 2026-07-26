import os.path
from collections.abc import Callable

import numpy as np

from pipeline.components.defuzzification.defuzzification import apply_defuzzification_rule
from pipeline.components.evaluation_metrics.computational.computational_metrics import get_computation_start_time, \
    get_computation_end_time, compute_computational_metrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics import compute_extrinsic_metrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics import compute_intrinsic_metrics
from pipeline.components.faddis.faddis import faddis
from pipeline.components.lapin.lapin import lapin
from pipeline.components.loaders.adjacency_matrix import compute_adjacency_matrix
from pipeline.components.loaders.real_world_data_loader import load_network_from_gml
from pipeline.components.sparsification.sparsification import apply_global_threshold_sparsification
from pipeline.components.stop_criterion.stop_criterion import set_stop_criterion
from pipeline.config.real_world_runners.config import ExecutionMode, DefuzzificationRule
from pipeline.scripts.utils.networks_dataclasses import NetworkFamilyConfig
from pipeline.scripts.utils.result_dataclass import Result, initialize_results_file
from pipeline.scripts.utils.utils import create_results_dir, log_progress, create_network_results_dir, \
    save_faddis_clustering_results
from pipeline.scripts.utils.utils import save_report_of_real_world_runner


def run_real_world_networks_experiments(
        results_base_dir: str,
        network_family_configs: list[NetworkFamilyConfig],
        thresholds: dict[str, float],
        affinity_designs: dict[str, Callable[[np.ndarray], np.ndarray]],
        execution_modes: list[ExecutionMode],
        defuzzification_rules: list[DefuzzificationRule],
        stop_criterion_until_k: bool = False
):
    """
    Run real-world networks experiments.

    Parameters:
        results_base_dir : (str)
            Path to the base directory where results will be saved.
        network_family_configs : (list[NetworkFamilyConfig])
            List of network family configs to be processed.
        thresholds : (dict[str, float])
            Dictionary containing threshold values, keyed by network family name.
        affinity_designs : (dict[str, Callable[[np.ndarray], np.ndarray]])
            Dictionary of affinity designs to be applied, keyed by design label.
        execution_modes : (list[ExecutionMode])
            List of execution modes to be applied.
        defuzzification_rules : (list[DefuzzificationRule])
            List of defuzzification rules to be applied.
        stop_criterion_until_k : (bool, optional)
            Set the stop criterion of FADDIS for extracting k clusters.
            Default is False.

    Returns:
        results_dir : (str)
            The path to the results' directory.
    """

    results_dir = create_results_dir(results_base_dir)

    for idx1, network_family_config in enumerate(network_family_configs, 1):
        log_progress(idx1, len(network_family_configs), network_family_config.name, 5, True)

        network_configs = sorted(network_family_config.network_configs, key=lambda n: n.name)
        for idx2, network_config in enumerate(network_configs, 1):
            log_progress(idx2, len(network_configs), network_config.name, 4, True)

            results_network_dir = create_network_results_dir(
                results_dir, network_family_config.name, network_config.name
            )

            append_result = initialize_results_file(results_network_dir)
            number_of_results = 0

            try:
                # 0. Load network.
                graph, ground_truth_labels, k = load_network_from_gml(
                    dir_path=os.path.join(network_family_config.directory, network_family_config.name),
                    network_config=network_config
                )

                # 1. Compute adjacency matrix A.
                A = compute_adjacency_matrix(graph)

                for idx3, (affinity_design_label, affinity_matrix_lambda) in enumerate(affinity_designs.items(), 1):
                    log_progress(idx3, len(affinity_designs), affinity_design_label, 3)

                    # 2. Compute the affinity matrix W from the matrix A.
                    W = affinity_matrix_lambda(A)

                    # 3. Apply sparsification to matrix W to obtain the matrix Ws.
                    Ws, As, graph_s, ground_truth_labels_s, k_s, sparsification_info = apply_global_threshold_sparsification(
                        W, ground_truth_labels, affinity_design_label,
                        target_average_degree=20.0
                    )

                    for idx4, execution_mode in enumerate(execution_modes, 1):
                        log_progress(idx4, len(execution_modes), execution_mode.label, 2)

                        # 4. If enabled, perform the LAPIN transformation on matrix Ws to produce the matrix Ln.
                        Ln = lapin(Ws) if execution_mode.apply_lapin else None

                        # 5. Fine-tune the stop criterion for FADDIS.
                        if not stop_criterion_until_k:
                            epsilon, tau, k_max = set_stop_criterion(
                                graph_s.number_of_nodes(), network_family_config.name, thresholds
                            )
                        else:
                            epsilon, tau, k_max = None, None, None

                        # 6. Execute FADDIS.
                        start_time = get_computation_start_time()
                        if not stop_criterion_until_k:
                            results = faddis(Ws if not execution_mode.apply_lapin else Ln, epsilon, tau, k_max)
                        else:
                            results = faddis(
                                W=Ws if not execution_mode.apply_lapin else Ln,
                                desired_k=k_s + 1 if not execution_mode.apply_lapin else k_s
                            )
                        end_time = get_computation_end_time()

                        if network_config.overlapping_ground_truth is True:
                            current_defuzzification_rules = defuzzification_rules
                        elif network_config.overlapping_ground_truth is False:
                            current_defuzzification_rules = [None]
                        else:
                            current_defuzzification_rules = defuzzification_rules + [None]

                        for idx5, defuzzification_rule in enumerate(current_defuzzification_rules, 1):
                            log_progress(idx5, len(current_defuzzification_rules), str(defuzzification_rule), 1)

                            # 7. Apply a defuzzification rule to map fuzzy memberships to a binary [overlapping] community cover.
                            membership_matrix, _, _, _, _, stop_condition = results
                            overlapping = defuzzification_rule is not None
                            gamma = defuzzification_rule.gamma if overlapping else None
                            predicted_labels, k_predicted, first_cluster_discarded = apply_defuzzification_rule(
                                membership_matrix,
                                gamma,
                                overlapping=overlapping
                            )

                            # 8. Compute the evaluation metrics.
                            if network_config.ground_truth:
                                extrinsic_results = compute_extrinsic_metrics(
                                    graph_s, ground_truth_labels_s, predicted_labels, k_s, k_predicted,
                                    overlapping=overlapping
                                )
                            else:
                                extrinsic_results = ExtrinsicMetrics(diff_of_k=f"{k_predicted}")

                            intrinsic_results = compute_intrinsic_metrics(
                                graph_s, As, membership_matrix, predicted_labels,
                                overlapping=overlapping
                            )

                            computational_results = compute_computational_metrics(start_time, end_time)

                            number_of_results += 1
                            results_id = f"{number_of_results:03d}"
                            laplacian_variant = "Lsym" if execution_mode.apply_lapin else "-"
                            append_result(Result(
                                id=results_id,
                                network_family=network_family_config.name,
                                network=network_config.name,
                                overlapping=overlapping,
                                affinity_design=affinity_design_label,
                                actual_average_degree=sparsification_info.actual_average_degree,
                                sparsification_target_average_degree=sparsification_info.target_average_degree,
                                sparsification_theta=sparsification_info.theta,
                                sparsification_diff_n=sparsification_info.diff_n,
                                execution_mode=execution_mode.label,
                                laplacian_variant=laplacian_variant,
                                epsilon=epsilon,
                                tau=tau,
                                k_max=k_max,
                                stop_condition=stop_condition,
                                gamma=gamma,
                                first_cluster_discarded=first_cluster_discarded,
                                extrinsic_results=extrinsic_results,
                                intrinsic_results=intrinsic_results,
                                computational_results=computational_results,
                            ))

                            save_faddis_clustering_results(
                                results_network_dir,
                                results_id,
                                results,
                                predicted_labels,
                                ground_truth_labels_s,
                                save_membership_matrix=True
                            )
            except Exception as e:
                print(f"[ERROR] Network {network_config.name} processing failed with error: {e}")
                continue

    save_report_of_real_world_runner(
        results_dir, network_family_configs, thresholds, affinity_designs, execution_modes, defuzzification_rules
    )

    return results_dir
