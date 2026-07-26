import csv
import os
from dataclasses import dataclass, field, fields
from typing import Callable, get_args

from pipeline.components.evaluation_metrics.computational.computational_metrics_dataclass import ComputationalMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import IntrinsicMetrics
from pipeline.scripts.utils.utils import _format_value


@dataclass
class ComparisonResult:
    """
    Dataclass for comparison results.

    Attributes:
        algorithm_name : (str)
            Name of the algorithm.
        network_family : (str)
            The family of the network.
        network : (str)
            The name of the network.
        overlapping : (bool)
            Whether the ground truth is overlapping.
        affinity_design : (str)
            The affinity design label used in the experiment.
        execution_mode : (str)
            The execution mode used in the experiment.
        gamma : (float)
            The gamma parameter used in the experiment.
        first_cluster_discarded : (bool)
            Whether the first cluster was discarded in the experiment.
        extrinsic_results : (ExtrinsicMetrics | None)
            The extrinsic metrics results, if computed.
        intrinsic_results : (IntrinsicMetrics | None)
            The intrinsic metrics results, if computed.
        computational_results : (ComputationalMetrics | None)
            The computational metrics results, if computed.
    """

    algorithm_name: str = field(metadata={"label": "Algorithm"})
    network_family: str = field(metadata={"label": "Network Family"})
    network: str = field(metadata={"label": "Network"})
    overlapping: bool = field(metadata={"label": "Overlapping?"})
    affinity_design: str = field(metadata={"label": "Affinity Design"})
    execution_mode: str = field(metadata={"label": "Execution Mode"})
    gamma: float = field(metadata={"label": "Gamma"})
    first_cluster_discarded: bool = field(metadata={"label": "C0 discarded?"})
    extrinsic_results: ExtrinsicMetrics = field(default=None),
    intrinsic_results: IntrinsicMetrics = field(default=None),
    computational_results: ComputationalMetrics = field(default=None)


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
