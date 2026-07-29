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
    Dataclass for baseline comparison results.

    Attributes:
        algorithm_name : (str)
            The name of the community detection algorithm.
        network : (str)
            The name of the network.
        overlapping : (bool)
            Whether the predicted community structure is overlapping.
        seeds : (tuple[int, ...] | None)
            The random seeds used in the experiment, if applicable.
        affinity_design : (str | None)
            The affinity design label used in the experiment, if applicable.
        execution_mode : (str | None)
            The execution mode used in the experiment, if applicable.
        faddis_epsilon : (float | None)
            The epsilon parameter used by FADDIS, if applicable.
        faddis_tau : (float | None)
            The tau parameter used by FADDIS, if applicable.
        faddis_k_max : (int | None)
            The maximum number of clusters used by FADDIS, if applicable.
        faddis_gamma : (float | None)
            The gamma parameter used by the FADDIS defuzzification rule, if applicable.
        njw_fcm_m : (float | None)
            The fuzzifier parameter used by Fuzzy C-Means, if applicable.
        njw_fcm_error : (float | None)
            The convergence tolerance used by Fuzzy C-Means, if applicable.
        njw_fcm_max_iter : (int | None)
            The maximum number of Fuzzy C-Means iterations, if applicable.
        njw_fcm_fi : (float | None)
            The fi threshold used by the NJW+FCM defuzzification rule, if applicable.
        slpa_t : (int | None)
            The number of SLPA iterations, if applicable.
        slpa_r : (float | None)
            The SLPA post-processing threshold, if applicable.
        cfinder_clique_size : (int | None)
            The minimum clique size used by CFinder, if applicable.
        extrinsic_results : (ExtrinsicMetrics | None)
            The extrinsic metrics results, if computed.
        intrinsic_results : (IntrinsicMetrics | None)
            The intrinsic metrics results, if computed.
        computational_results : (ComputationalMetrics | None)
            The computational metrics results, if computed.
    """

    algorithm_name: str = field(metadata={"label": "Algorithm"})
    network: str = field(metadata={"label": "Network"})
    overlapping: bool = field(metadata={"label": "Overlapping?"})
    seeds: tuple[int, ...] = field(metadata={"label": "Seeds"}, default=None)
    affinity_design: str = field(metadata={"label": "Affinity Design"}, default=None)
    execution_mode: str = field(metadata={"label": "Execution Mode"}, default=None)
    faddis_epsilon: float = field(metadata={"label": "epsilon (FADDIS)"}, default=None)
    faddis_tau: float = field(metadata={"label": "tau (FADDIS)"}, default=None)
    faddis_k_max: int = field(metadata={"label": "k_max (FADDIS)"}, default=None)
    faddis_gamma: float = field(metadata={"label": "gamma (FADDIS)"}, default=None)
    njw_fcm_m: float = field(metadata={"label": "m (NJW+FCM)"}, default=None)
    njw_fcm_error: float = field(metadata={"label": "e (NJW+FCM)"}, default=None)
    njw_fcm_max_iter: int = field(metadata={"label": "t_max (NJW+FCM)"}, default=None)
    njw_fcm_fi: float = field(metadata={"label": "fi (NJW+FCM)"}, default=None)
    slpa_t: float = field(metadata={"label": "t (SLPA)"}, default=None)
    slpa_r: float = field(metadata={"label": "r (SLPA)"}, default=None)
    cfinder_clique_size: float = field(metadata={"label": "k (CFinder)"}, default=None)
    extrinsic_results: ExtrinsicMetrics = field(default=None)
    intrinsic_results: IntrinsicMetrics = field(default=None)
    computational_results: ComputationalMetrics = field(default=None)


def initialize_comparison_results_file(
        results_dir: str,
        output_filename: str = "_comparison_results"
) -> Callable[[ComparisonResult], None]:
    """
    Initialize the comparison results file and write it to the output directory.

    Parameters:
        results_dir : (str)
            Path to the created results' directory.
        output_filename : (str, optional)
            The name of the output CSV file.
            Default is "_comparison_results".

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
