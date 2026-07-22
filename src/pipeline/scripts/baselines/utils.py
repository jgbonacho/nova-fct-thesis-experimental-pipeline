import csv
import os
from dataclasses import fields
from typing import Callable, get_args

import networkx as nx
import numpy as np

from pipeline.components.evaluation_metrics.computational.computational_metrics_dataclass import ComputationalMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import IntrinsicMetrics
from pipeline.components.faddis.faddis import faddis
from pipeline.scripts.baselines.algorithm_dataclass import Algorithm
from pipeline.scripts.baselines.comparison_result_dataclass import ComparisonResult
from pipeline.scripts.baselines.non_spectral.cfinder import cfinder
from pipeline.scripts.baselines.non_spectral.slpa import slpa
from pipeline.scripts.baselines.spectral.njw_fcm import njw_fcm
from pipeline.scripts.utils.utils import _format_value


def initialize_comparison_results_file(
        results_dir: str,
        output_filename: str = "_comparison_results"
) -> Callable[[ComparisonResult], None]:
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
    selected_intrinsic_fields = None
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

    def append_result(result: ComparisonResult) -> None:
        nonlocal selected_base_fields
        nonlocal selected_extrinsic_fields
        nonlocal selected_intrinsic_fields
        nonlocal selected_computational_fields
        nonlocal header_written

        if not header_written:
            selected_base_fields = _select_fields(
                result, ComparisonResult, (ExtrinsicMetrics, IntrinsicMetrics, ComputationalMetrics)
            )
            selected_extrinsic_fields = (
                _select_fields(result.extrinsic_results, ExtrinsicMetrics)
                if result.extrinsic_results is not None else []
            )
            selected_intrinsic_fields = (
                _select_fields(result.intrinsic_results, IntrinsicMetrics)
                if result.intrinsic_results is not None else []
            )
            selected_computational_fields = (
                _select_fields(result.computational_results, ComputationalMetrics)
                if result.computational_results is not None else []
            )

            headers = (
                    _get_headers(selected_base_fields)
                    + _get_headers(selected_extrinsic_fields)
                    + _get_headers(selected_intrinsic_fields)
                    + _get_headers(selected_computational_fields)
            )

            with open(file_path, "w", newline="", encoding="utf-8") as out_file:
                csv.writer(out_file).writerow(headers)

            header_written = True

        row = (
                _get_row_values(result, selected_base_fields)
                + _get_row_values(result.extrinsic_results, selected_extrinsic_fields)
                + _get_row_values(result.intrinsic_results, selected_intrinsic_fields)
                + _get_row_values(result.computational_results, selected_computational_fields)
        )

        with open(file_path, "a", newline="", encoding="utf-8") as append_file:
            csv.writer(append_file).writerow(row)

    return append_result


def wrapper_spectral_algorithm(
        algorithm_name: Algorithm,
        W: np.ndarray,
        k: int,
        faddis_stopping_criterion: tuple = None
):
    """
    Execute the selected spectral comparison algorithm.

    Parameters:
        algorithm_name : (Algorithm)
            The algorithm to execute.
        W : (np.ndarray, shape[n,n])
            nxn symmetric similarity/affinity matrix.
        k : (int)
            Number of ground-truth communities.
        faddis_stopping_criterion : (tuple)
            The FADDIS stopping criterion.
            Default is None.

    Returns:
        membership_matrix : (np.ndarray, shape[n,k'])
            Fuzzy membership matrix returned by the selected algorithm.

    Exceptions:
        ValueError : If the selected algorithm is not supported.
    """

    if algorithm_name == Algorithm.FADDIS:
        if faddis_stopping_criterion is not None:
            (epsilon, tau, k_max) = faddis_stopping_criterion
            membership_matrix, _, _, _, _, _ = faddis(W=W, epsilon=epsilon, tau=tau, k_max=k_max)
        else:
            membership_matrix, _, _, _, _, _ = faddis(W=W, desired_k=k + 1)
        return membership_matrix
    elif algorithm_name == Algorithm.NJW_FCM:
        return njw_fcm(W=W, k=k)
    else:
        raise ValueError(f"[ERROR] {algorithm_name.value} is not a valid spectral algorithm.")


def wrapper_non_spectral_algorithm(algorithm_name: Algorithm, graph: nx.Graph):
    """
    Execute the selected non-spectral comparison algorithm.

    Parameters:
        algorithm_name : (Algorithm)
            The algorithm to execute.
        graph : (nx.Graph)
            Input NetworkX graph.

    Returns:
        predicted_labels : (list[list[int]])
            List of detected community labels assigned to each node.
        k_predicted : (int)
            Number of detected communities.

    Exceptions:
        ValueError : If the selected algorithm is not supported.
    """

    if algorithm_name == Algorithm.SLPA:
        return slpa(graph=graph, t=100, r=0.45, seed=0)
    elif algorithm_name == Algorithm.CFINDER:
        return cfinder(graph=graph, clique_size=4)
    else:
        raise ValueError(f"[ERROR] {algorithm_name.value} is not a valid non-spectral algorithm.")
