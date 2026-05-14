import csv
import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import asdict, fields
from datetime import datetime
from typing import get_args, Any

import numpy as np

from pipeline.components.evaluation_metrics.computational.computational_metrics import ComputationalMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.config.synthetic_runner.config import ExecutionMode, DefuzzificationRule
from pipeline.scripts.utils.networks_dataclasses import LFRNetworkFamilyConfig, NetworkFamilyConfig
from pipeline.scripts.utils.result_dataclass import Result


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


def stable_seed(base_seed: int, family_name: str) -> int:
    """
    Generate a random seed for a specific family.

    Parameters:
        base_seed : (int)
            The base seed for generating the seed.
        family_name : (str)
            The name of the family for which to generate the seed.

    Returns:
        seed : (int)
            A stable seed generated from the base seed and family name.
    """

    s = f"{base_seed}::{family_name}"
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16)


def initialize_results_file(results_dir: str, output_filename: str = "_results") -> Callable[[Result], None]:
    """
    Initialize the results file and write it to the output directory.

    Parameters:
        results_dir : (str)
            Path to the created results' directory.
        output_filename : (str, optional)
            The name of the output CSV file.
            Default is "_results".

    Returns:
        append_result : (Callable[[Result], None])
            A function that takes a Result object and appends its data to the results CSV file.

    Saves:
        A new CSV file within 'results_dir' named "{output_filename}.csv" with results.
    """

    file_path = os.path.join(results_dir, f"{output_filename}.csv")

    selected_base_fields = None
    selected_extrinsic_fields = None
    selected_computational_fields = None
    header_written = False

    def _has_excluded_type(dataclass_field, excluded_types):
        annotation = dataclass_field.type
        annotation_args = get_args(annotation)
        if annotation_args:
            return any(arg in excluded_types for arg in annotation_args)
        return annotation in excluded_types

    def _select_fields(obj, cls, excluded_types=()):
        return [
            dataclass_field for dataclass_field in fields(cls)
            if not _has_excluded_type(dataclass_field, excluded_types)
               and getattr(obj, dataclass_field.name) is not None
        ]

    def _get_headers(selected_fields):
        return [dataclass_field.metadata.get("label", dataclass_field.name) for dataclass_field in selected_fields]

    def _get_row_values(obj, selected_fields):
        return [_format_value(getattr(obj, dataclass_field.name)) for dataclass_field in selected_fields]

    def append_result(result: Result) -> None:
        nonlocal selected_base_fields
        nonlocal selected_extrinsic_fields
        nonlocal selected_computational_fields
        nonlocal header_written

        if not header_written:
            selected_base_fields = _select_fields(
                result, Result, (ExtrinsicMetrics, ComputationalMetrics)
            )
            selected_extrinsic_fields = (
                _select_fields(result.extrinsic_results, ExtrinsicMetrics)
                if result.extrinsic_results is not None else []
            )
            selected_computational_fields = (
                _select_fields(result.computational_results, ComputationalMetrics)
                if result.computational_results is not None else []
            )

            headers = (
                    _get_headers(selected_base_fields)
                    + _get_headers(selected_extrinsic_fields)
                    + _get_headers(selected_computational_fields)
            )

            with open(file_path, "w", newline="", encoding="utf-8") as out_file:
                csv.writer(out_file).writerow(headers)

            header_written = True

        row = (
                _get_row_values(result, selected_base_fields)
                + _get_row_values(result.extrinsic_results, selected_extrinsic_fields)
                + _get_row_values(result.computational_results, selected_computational_fields)
        )

        with open(file_path, "a", newline="", encoding="utf-8") as append_file:
            csv.writer(append_file).writerow(row)

    return append_result


def save_faddis_clustering_results(
        results_dir: str,
        results_id: str,
        faddis_results: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, str],
        output_filename: str = "faddis-clusters"
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
        output_filename : (str, optional)
            The name of the output CSV file.
            Default is "results-faddis-clusters.csv".

    Saves:
        A CSV file within 'results_dir' named "{output_filename}_{results_id}.csv" containing the clustering results.
    """

    _, contributions, intensities, eigenvalues, number_of_clusters, _ = faddis_results
    with open(os.path.join(results_dir, f"{output_filename}_{results_id}.csv"), mode="w", newline="",
              encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Cluster", "Contribution", "Eigenvalue", "Intensity", "Weight"])

        for i in range(0, number_of_clusters):
            writer.writerow([
                _int_to_roman(i),
                round((contributions[i] * 100), 4),
                round((eigenvalues[i]), 4),
                round((intensities[i, 0]), 4),
                round((intensities[i, 1]), 4),
            ])


def save_report_of_synthetic_runner(
        results_dir: str,
        network_families: list[LFRNetworkFamilyConfig],
        thresholds: dict[str, float],
        affinity_designs: dict[str, Callable[[np.ndarray], np.ndarray]],
        execution_modes: list[ExecutionMode],
        defuzzification_rules: list[DefuzzificationRule],
        output_filename: str = "report"
) -> None:
    """
    Save a report of the experiment configurations to a JSON file in the results' directory.

    Parameters:
        results_dir : (str)
            Path to the results' directory.
        network_families : (list[LFRNetworkFamilyConfig])
            List of network families to be processed.
        thresholds : (dict[str, float])
            Dictionary containing threshold values, keyed by network family name.
        affinity_designs : (dict[str, Callable[[np.ndarray], np.ndarray]])
            Dictionary of affinity designs to be applied, keyed by design label.
        execution_modes : (list[ExecutionMode])
            List of execution modes to be applied.
        defuzzification_rules : (list[DefuzzificationRule])
            List of defuzzification rules to be applied.
        output_filename : (str, optional)
            The name of the output JSON file.
            Default is "report.json".

    Saves:
        A JSON file within 'results_dir' named "{output_filename}.json".
    """

    report = {
        "network_families": [asdict(network_family) for network_family in network_families],
        "thresholds": thresholds,
        "affinity_designs": list(affinity_designs.keys()),
        "execution_modes": [asdict(execution_mode) for execution_mode in execution_modes],
        "defuzzification_rules": [asdict(defuzzification_rule) for defuzzification_rule in defuzzification_rules],
    }

    with open(os.path.join(results_dir, f"{output_filename}.json"), "w", encoding="utf-8") as out_file:
        json.dump(report, out_file, indent=2)


def save_report_of_real_world_runner(
        results_dir: str,
        network_families: list[NetworkFamilyConfig],
        thresholds: dict[str, float],
        affinity_designs: dict[str, Callable[[np.ndarray], np.ndarray]],
        execution_modes: list[ExecutionMode],
        defuzzification_rules: list[DefuzzificationRule],
        output_filename: str = "report"
) -> None:
    """
    Save a report of the experiment configurations to a JSON file in the results' directory.

    Parameters:
        results_dir : (str)
            Path to the results' directory.
        network_families : (list[NetworkFamilyConfig])
            List of network families to be processed.
        thresholds : (dict[str, float])
            Dictionary containing threshold values, keyed by network family name.
        affinity_designs : (dict[str, Callable[[np.ndarray], np.ndarray]])
            Dictionary of affinity designs to be applied, keyed by design label.
        execution_modes : (list[ExecutionMode])
            List of execution modes to be applied.
        defuzzification_rules : (list[DefuzzificationRule])
            List of defuzzification rules to be applied.
        output_filename : (str, optional)
            The name of the output JSON file.
            Default is "report.json".

    Saves:
        A JSON file within 'results_dir' named "{output_filename}.json".
    """

    report = {
        "network_families": [asdict(network_family) for network_family in network_families],
        "thresholds": thresholds,
        "affinity_designs": list(affinity_designs.keys()),
        "execution_modes": [asdict(execution_mode) for execution_mode in execution_modes],
        "defuzzification_rules": [asdict(defuzzification_rule) for defuzzification_rule in defuzzification_rules],
    }

    with open(os.path.join(results_dir, f"{output_filename}.json"), "w", encoding="utf-8") as out_file:
        json.dump(report, out_file, indent=2)


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
