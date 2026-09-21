import csv
import json
import os
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime
from typing import Any

import numpy as np

from pipeline.components.affinity_design.affinity_design_dataclass import AffinityDesign
from pipeline.config.utils.defuzzification_rule_dataclass import DefuzzificationRule
from pipeline.config.utils.execution_mode_dataclass import ExecutionMode
from pipeline.scripts.utils.networks_dataclasses import LFRNetworkFamilyConfig, NetworkFamilyConfig


def create_results_dir(base_dir: str) -> str:
    """
    Create a directory to store results, named with the current timestamp.

    Parameters:
        base_dir : (str)
            The base directory for the results.

    Returns:
        results_dir : (str)
            Path to the created results' directory.

    Saves:
        A new directory within 'base_dir' named "results_YYYY-MM-DD_HH-MM-SS-ffffff".
    """

    os.makedirs(base_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    results_dir_name = f"results_{timestamp}"
    results_dir = os.path.join(base_dir, results_dir_name)
    os.makedirs(results_dir)

    return results_dir


def create_network_results_dir(results_dir: str, network_family: str, network: str) -> str:
    """
    Create a directory to store results for a specific network.

    Parameters:
        results_dir : (str)
            Path to the created results' directory.
        network_family : (str)
            The family name of the network.
        network : (str)
            The name of the network.

    Returns:
        network_results_dir : (str)
            Path to the created network results' directory.

    Saves:
        A new directory within 'results_dir' named "{network_family}/{network}".
    """

    results_network_dir = os.path.join(results_dir, network_family, network)
    os.makedirs(results_network_dir)

    return results_network_dir


def log_progress(
        current_step: int,
        total_steps: int,
        item_label: str,
        indent_level: int,
        empty_line: bool = False
) -> None:
    """
    Log a progress message to the console with a specific format.

    Parameters:
        current_step : (int)
            The current step.
        total_steps : (int)
            The total number of steps.
        item_label : (str)
            The label of the item being processed.
        indent_level : (int)
            The level of indentation (number of '#' characters).
        empty_line : (bool, optional)
            Whether to print an empty line before the progress log.
            Default is False.
    """

    prefix = "\n" if empty_line else ""
    print(f"{prefix}{indent_level * '#'} [{current_step}/{total_steps}] '{item_label}'")


def save_faddis_clustering_results(
        results_dir: str,
        results_id: str,
        faddis_results: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, str],
        predicted_labels: list,
        ground_truth_labels: list,
        output_filename: str = "faddis-clusters",
        save_membership_matrix: bool = False
) -> None:
    """
    Save the results of the FADDIS clustering algorithm.

    Parameters:
        results_dir : (str)
            Path to the directory where the results will be saved.
        results_id : (str)
            An identifier for the results, used in the filename.
        faddis_results : (tuple[list[np.matrix], np.matrix, np.ndarray, np.ndarray, np.ndarray, int, str])
            A list containing the results of the FADDIS algorithm, expected to include:
                - membership_matrix
                - contributions
                - intensities
                - eigenvalues
                - number_of_clusters
                - stop_condition
        predicted_labels : (list[int], length n | list[list[int]], length n)
            Predicted labels.
        ground_truth_labels : (list[int], length n | list[list[int]], length n | None)
            Ground-truth labels.
        output_filename : (str, optional)
            The name of the output CSV file.
            Default is "results-faddis-clusters.csv".
        save_membership_matrix : (bool, optional)
            whether to save the membership matrix of the FADDIS algorithm.
            Default is False.

    Saves:
        A CSV file within 'results_dir' named "{output_filename}_{results_id}.csv" containing the clustering results.
    """

    membership_matrix, contributions, intensities, eigenvalues, number_of_clusters, _ = faddis_results
    assigned_nodes_per_cluster = _count_assigned_nodes(predicted_labels, number_of_clusters)
    with open(os.path.join(results_dir, f"{output_filename}_{results_id}.csv"), mode="w", newline="",
              encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Cluster", "Contribution", "Eigenvalue", "Intensity", "Weight", "Assigned Nodes"])

        for i in range(0, number_of_clusters):
            writer.writerow([
                _int_to_roman(i),
                round((contributions[i] * 100), 4),
                round((eigenvalues[i]), 4),
                round((intensities[i, 0]), 4),
                round((intensities[i, 1]), 4),
                assigned_nodes_per_cluster[i],
            ])

    if save_membership_matrix:
        membership_matrix = np.asarray(membership_matrix)
        with open(os.path.join(results_dir, f"faddis-nodes-{results_id}.csv"), mode="w", newline="",
                  encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            header = (
                    ["Node"]
                    + [f"Cluster_{_int_to_roman(i)}" for i in range(number_of_clusters)]
                    + ["Predicted Label"]
            )
            if ground_truth_labels is not None:
                header += ["Ground-Truth Label"]
            writer.writerow(header)

            for node_id in range(membership_matrix.shape[0]):
                row = [node_id]
                row += [float(membership_matrix[node_id, cluster_id]) for cluster_id in range(number_of_clusters)]
                row.append(_format_label(predicted_labels[node_id]))
                if ground_truth_labels is not None:
                    row.append(_format_label(ground_truth_labels[node_id]))
                writer.writerow(row)


def save_report_of_synthetic_runner(
        results_dir: str,
        network_families: list[LFRNetworkFamilyConfig],
        thresholds: dict[str, float] = None,
        affinity_designs: dict[AffinityDesign, Callable[[np.ndarray], np.ndarray]] = None,
        execution_modes: list[ExecutionMode] = None,
        defuzzification_rules: list[DefuzzificationRule] = None,
        output_filename: str = "report"
) -> None:
    """
    Save a report of the experiment configurations to a JSON file in the results' directory.

    Parameters:
        results_dir : (str)
            Path to the results' directory.
        network_families : (list[LFRNetworkFamilyConfig])
            List of network families to be processed.
        thresholds : (dict[str, float] | None)
            Dictionary containing threshold values, keyed by network family name.
        affinity_designs : (dict[AffinityDesign, Callable[[np.ndarray], np.ndarray]] | None)
            Dictionary of affinity designs to be applied, keyed by AffinityDesign.
        execution_modes : (list[ExecutionMode] | None)
            List of execution modes to be applied.
        defuzzification_rules : (list[DefuzzificationRule] | None)
            List of defuzzification rules to be applied.
        output_filename : (str, optional)
            The name of the output JSON file.
            Default is "report.json".

    Saves:
        A JSON file within 'results_dir' named "{output_filename}.json".
    """

    report: dict[str, Any] = {
        "network_families": [asdict(network_family) for network_family in network_families]
    }

    if thresholds is not None:
        report["thresholds"] = thresholds

    if affinity_designs is not None:
        report["affinity_designs"] = [
            design.value
            if isinstance(design, AffinityDesign)
            else str(design)
            for design in affinity_designs
        ]

    if execution_modes is not None:
        report["execution_modes"] = [
            asdict(execution_mode) for execution_mode in execution_modes
        ]

    if defuzzification_rules is not None:
        report["defuzzification_rules"] = [
            asdict(defuzzification_rule) for defuzzification_rule in defuzzification_rules
        ]

    with open(os.path.join(results_dir, f"{output_filename}.json"), "w", encoding="utf-8") as out_file:
        json.dump(report, out_file, indent=2)


def save_report_of_real_world_runner(
        results_dir: str,
        network_families: list[NetworkFamilyConfig],
        thresholds: dict[str, float] = None,
        affinity_designs: dict[AffinityDesign, Callable[[np.ndarray], np.ndarray]] = None,
        execution_modes: list[ExecutionMode] = None,
        defuzzification_rules: list[DefuzzificationRule] = None,
        output_filename: str = "report"
) -> None:
    """
    Save a report of the experiment configurations to a JSON file in the results' directory.

    Parameters:
        results_dir : (str)
            Path to the results' directory.
        network_families : (list[NetworkFamilyConfig])
            List of network families to be processed.
        thresholds : (dict[str, float] | None)
            Dictionary containing threshold values, keyed by network name.
        affinity_designs : (dict[AffinityDesign, Callable[[np.ndarray], np.ndarray]] | None)
            Dictionary of affinity designs to be applied, keyed by AffinityDesign.
        execution_modes : (list[ExecutionMode] | None)
            List of execution modes to be applied.
        defuzzification_rules : (list[DefuzzificationRule] | None)
            List of defuzzification rules to be applied.
        output_filename : (str, optional)
            The name of the output JSON file.
            Default is "report.json".

    Saves:
        A JSON file within 'results_dir' named "{output_filename}.json".
    """

    report: dict[str, Any] = {
        "network_families": [asdict(network_family) for network_family in network_families],
    }

    if thresholds is not None:
        report["thresholds"] = thresholds

    if affinity_designs is not None:
        report["affinity_designs"] = [
            design.value
            if isinstance(design, AffinityDesign)
            else str(design)
            for design in affinity_designs
        ]

    if execution_modes is not None:
        report["execution_modes"] = [
            asdict(execution_mode) for execution_mode in execution_modes
        ]

    if defuzzification_rules is not None:
        report["defuzzification_rules"] = [
            asdict(defuzzification_rule) for defuzzification_rule in defuzzification_rules
        ]

    with open(os.path.join(results_dir, f"{output_filename}.json"), "w", encoding="utf-8") as out_file:
        json.dump(report, out_file, indent=2)


def _count_assigned_nodes(predicted_labels: list, number_of_clusters: int) -> dict[int, int]:
    """
    Count the number of nodes assigned to each predicted cluster.

    Parameters:
        predicted_labels : (list[int] | list[list[int]])
            Predicted node assignments.
        number_of_clusters : (int)
            Number of clusters.

    Returns:
        assigned_nodes_per_cluster : (dict[int, int])
            Number of nodes assigned to each cluster.
    """

    assigned_nodes_per_cluster = {cluster_id: 0 for cluster_id in range(number_of_clusters)}
    for labels in predicted_labels:
        if isinstance(labels, list):
            for label in labels:
                assigned_nodes_per_cluster[label] += 1
        else:
            assigned_nodes_per_cluster[labels] += 1

    return assigned_nodes_per_cluster


def _format_label(label):
    """
    Format a label for saving in CSV.

    Parameters:
        label : (int | np.integer | list[int] | list[np.integer])
            Label to format.

    Returns:
        formatted_label : (str | int)
            Formatted label.
    """

    if isinstance(label, list):
        return str([int(x) if isinstance(x, np.integer) else x for x in label])
    else:
        return int(label)


def _format_value(value: Any) -> str:
    """
    Format a value into a human-readable string.

    Parameters:
        value : (str | int | bool | float)
            Value to be formatted.

    Returns:
        formatted_value : (str)
            Formatted value.
    """

    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (float, np.floating)):
        if value == 0:
            return "0"
        if abs(value) < 1e-4:
            return f"{value:.6e}"
        text = f"{value:.15f}".rstrip("0").rstrip(".")
        if "." in text and len(text.split(".")[1]) > 4:
            return f"{value:.6f}"
        return text
    return value


def _int_to_roman(num: int) -> str:
    """
    Convert an integer to a Roman numeral.

    Parameters:
        num : (int)
            The integer to convert (0 <= num <= 4000).

    Returns:
        roman_num : (str)
            The Roman numeral representation of the integer.

    Exceptions:
        ValueError: If the input is not an integer between 0 and 40000.
    """

    if num < 0 or num > 40000:
        raise ValueError("[ERROR] Input must be an integer between 0 and 40000.")

    if num == 0:
        return "0"

    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    symbols = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]

    roman_num = ""
    i = 0
    while num > 0:
        for _ in range(num // values[i]):
            roman_num += symbols[i]
            num -= values[i]
        i += 1

    return roman_num


def format_mean_and_sample_std_aux(values: list[int]) -> str:
    """
    Format the mean and sample standard deviation of a list of values.

    Invalid values, including ``None`` and non-finite values, are ignored.
    If only one valid value is available, the sample standard deviation is reported as zero.

    Parameters:
        values : (list[int])
            List of values to summarize.

    Returns:
        str
            Formatted string in the form ``"mean ± sample_std"``, or ``None`` if no valid values are available.
    """

    valid_values = [float(value) for value in values if value is not None and np.isfinite(float(value))]

    if not valid_values:
        return None

    mean = float(np.mean(valid_values))
    sample_std = (float(np.std(valid_values, ddof=1)) if len(valid_values) > 1 else 0.0)

    return f"{mean} ± {sample_std}"
