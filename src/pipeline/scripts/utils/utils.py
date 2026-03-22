import csv
import json
import os
from dataclasses import asdict, fields
from datetime import datetime
from typing import get_args

from pipeline.components.evaluation_metrics.computational.computational_metrics import ComputationalMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.scripts.utils.result_dataclass import Result


def create_results_dir(base_dir):
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


def create_network_results_dir(results_dir, network_family, network):
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


def log_progress(current_step, total_steps, item_label, indent_level, empty_line=False):
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

    print(f"{"\n" if empty_line else ""}{indent_level * '#'} [{current_step}/{total_steps}] '{item_label}'")


def initialize_results_file(results_dir, output_filename="results.csv"):
    """
    Initialize the results file and write it to the output directory.

    Parameters:
        results_dir : (str)
            Path to the created results' directory.
        output_filename : (str, optional)
            The name of the output CSV file.
            Default is "results.csv".

    Returns:
        _append_result : (function)
            A function that takes a Result object and appends its data to the results CSV file.

    Saves:
        A new CSV file within 'results_dir' named "{output_filename}" with results.
    """

    file_path = os.path.join(results_dir, output_filename)

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

    def _append_result(result):
        nonlocal selected_base_fields
        nonlocal selected_extrinsic_fields
        nonlocal selected_computational_fields
        nonlocal header_written

        if not header_written:
            selected_base_fields = _select_fields(result, Result, (ExtrinsicMetrics, ComputationalMetrics))
            selected_extrinsic_fields = (
                _select_fields(result.extrinsic_results, ExtrinsicMetrics)
                if result.extrinsic_results is not None
                else []
            )
            selected_computational_fields = (
                _select_fields(result.computational_results, ComputationalMetrics)
                if result.computational_results is not None
                else []
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

    return _append_result


def save_faddis_clustering_results(results_dir, results_id, faddis_results):
    """
    Save the results of the FADDIS clustering algorithm.

    Parameters:
        results_dir : (str)
            Path to the directory where the results will be saved.
        results_id : (str)
            An identifier for the results, used in the filename.
        faddis_results : (list)
            A list containing the results of the FADDIS algorithm, expected to include:
                - membership_matrix
                - contributions
                - intensities
                - eigenvalues
                - number_of_clusters
                - stop_condition

    Saves:
        A CSV file within 'results_dir' named "id{results_id}.csv" containing the clustering results.
    """

    _, _, contributions, intensities, eigenvalues, number_of_clusters, _ = faddis_results
    with open(os.path.join(results_dir, f"id{results_id}.csv"), mode="w", newline="", encoding="utf-8") as csvfile:
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


def save_report(
        results_dir,
        network_families,
        thresholds,
        affinity_designs,
        execution_modes,
        defuzzification_rules,
        output_filename="report.json"
):
    """
    Save a report of the experiment configurations to a JSON file in the results' directory.

    Parameters:
        results_dir : (str)
            Path to the results directory.
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
        output_filename : (str, optional)
            The name of the output JSON file.
            Default is "report.json".

    Saves:
        A JSON file within 'results_dir' named "{output_filename}".
    """

    report = {
        "network_families": [asdict(network_family) for network_family in network_families],
        "thresholds": thresholds,
        "affinity_designs": list(affinity_designs.keys()),
        "execution_modes": [asdict(execution_mode) for execution_mode in execution_modes],
        "defuzzification_rules": [asdict(defuzzification_rule) for defuzzification_rule in defuzzification_rules],
    }

    with open(os.path.join(results_dir, output_filename), "w", encoding="utf-8") as out_file:
        json.dump(report, out_file, indent=2)


def _format_value(value):
    """
    Format a value into a human-readable string.

    Parameters:
        value : (any)
            Value to be formatted.

    Returns:
        formatted_value : (str)
            Formatted value.
    """

    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        text = f"{value:.15f}".rstrip("0").rstrip(".")
        if "." in text and len(text.split(".")[1]) > 4:
            return f"{value:.6f}"
        return text
    return value


def _int_to_roman(num):
    """
    Convert an integer to a Roman numeral.

    Parameters:
        num : (int)
            The integer to convert (0 <= num < 4000).

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
