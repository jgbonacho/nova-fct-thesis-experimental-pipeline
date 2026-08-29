import json
import math
import os.path
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# Base directory for results.
RESULTS_BASE_DIR = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'archive',
    'results',
    'real-world',
    'stage2'
)

# Result CSV column names.
ALGORITHM_COL = "Algorithm"
NETWORK_COL = "Network"
OVERLAPPING_COL = "Overlapping?"
KERR_COL = "|K'-K|/K"

AMI_COL = "AMI"
F_MEASURE_COL = "F-measure"
ARI_COL = "ARI"
FMI_COL = "FMI"
NMI_COL = "NMI"
VI_COL = "VI"
ONMI_COL = "ONMI"
OMEGA_COL = "Omega"

MODULARITY_COL = "Modularity"
CONDUCTANCE_COL = "Conductance"
FUZZY_MODULARITY_COL = "Fuzzy-Modularity"
CONDUCTANCE_BN_COL = "Conductance-BN"

# The current comparison CSV labels the generic runtime as "FADDIS Runtime"
# for every algorithm. "Runtime" is also accepted for a corrected schema.
RUNTIME_INPUT_COLS = ("Runtime", "FADDIS Runtime")
RUNTIME_COL = "Runtime"

SOURCE_FILE_COL = "Source File"
NETWORK_ORDER_COL = "Network Order"

# Preferred algorithm order in CSV summaries and plots.
ALGORITHM_ORDER = ("FADDIS", "NJW+FCM")

# Metrics applicable to each ground-truth type.
NON_OVERLAPPING_METRICS = (
    KERR_COL,
    AMI_COL,
    F_MEASURE_COL,
    ARI_COL,
    FMI_COL,
    NMI_COL,
    VI_COL,
    MODULARITY_COL,
    CONDUCTANCE_COL,
    RUNTIME_COL,
)

OVERLAPPING_METRICS = (
    KERR_COL,
    ONMI_COL,
    OMEGA_COL,
    FUZZY_MODULARITY_COL,
    CONDUCTANCE_BN_COL,
    RUNTIME_COL,
)

# Metrics shown in the figures. The relative error of K is retained in the
# generated CSV files but intentionally omitted from the plots.
NON_OVERLAPPING_PLOT_METRICS = (
    AMI_COL,
    NMI_COL,
    MODULARITY_COL,
    CONDUCTANCE_COL,
)

OVERLAPPING_PLOT_METRICS = (
    ONMI_COL,
    OMEGA_COL,
    FUZZY_MODULARITY_COL,
    CONDUCTANCE_BN_COL,
)

ALL_METRICS = tuple(dict.fromkeys(
    NON_OVERLAPPING_METRICS + OVERLAPPING_METRICS
))

# Human-readable y-axis labels.
METRIC_LABELS = {
    KERR_COL: r"Mean Relative Error $|K'-K|/K$",
    AMI_COL: "Mean AMI",
    F_MEASURE_COL: "Mean F-measure",
    ARI_COL: "Mean ARI",
    FMI_COL: "Mean FMI",
    NMI_COL: "Mean NMI",
    VI_COL: "Mean VI",
    ONMI_COL: "Mean ONMI",
    OMEGA_COL: "Mean Omega",
    MODULARITY_COL: "Mean Modularity",
    CONDUCTANCE_COL: "Mean Conductance",
    FUZZY_MODULARITY_COL: "Mean Fuzzy-Modularity",
    CONDUCTANCE_BN_COL: "Mean Conductance-BN",
    RUNTIME_COL: "Mean Runtime (seconds)",
}


def plot_real_world_spectral_comparison_results(
        results_dir: str,
        input_filename: str = "_comparison_results.csv",
) -> None:
    """
    Process and plot spectral-comparison results for real-world networks.

    The result files are discovered recursively because the real-world runner
    organizes them by network family and then by network name. Metric values
    can be either scalar values (e.g., FADDIS) or strings formatted as
    "mean ± sample standard deviation" (e.g., NJW+FCM). The mean component is
    used as the bar height, while the reported standard deviation, when
    available, is shown using error bars and retained in the generated CSV
    files.

    Results are separated by the value of the "Overlapping?" column:
        - Non-overlapping networks use crisp extrinsic and intrinsic metrics.
        - Overlapping networks use overlapping extrinsic and fuzzy intrinsic
          metrics.

    Parameters:
        results_dir : (str)
            Root directory containing the real-world spectral-comparison
            results. The function searches recursively for each network's
            comparison CSV file.
        input_filename : (str, optional)
            Name of the comparison results file saved in each network
            directory.
            Default is "_comparison_results.csv".

    Saves:
        - "real_world_spectral_comparison_results.csv": parsed raw rows.
        - "real_world_spectral_comparison_summary.csv": results grouped by
          ground-truth type, network, and algorithm.
        - "non_overlapping_real_world_spectral_algorithms.pdf": grouped bar plots
          for non-overlapping networks, when available.
        - "overlapping_real_world_spectral_algorithms.pdf": grouped bar plots for
          overlapping networks, when available.
    """

    result_files = _iter_result_files(
        results_dir=results_dir,
        input_filename=input_filename,
    )

    if not result_files:
        raise ValueError(
            f"[ERROR] No '{input_filename}' files were found in "
            f"'{results_dir}'."
        )

    rows = []
    network_orders = {}

    for result_file in result_files:
        results_df = _read_csv(result_file)
        runtime_input_col = _find_runtime_column(results_df)

        required_columns = {
            ALGORITHM_COL,
            OVERLAPPING_COL,
        }
        missing_columns = required_columns - set(results_df.columns)
        if missing_columns:
            raise ValueError(
                f"[ERROR] Missing columns in '{result_file}': "
                f"{sorted(missing_columns)}."
            )

        for _, result in results_df.iterrows():
            network = _resolve_network_name(
                result=result,
                result_file=result_file,
            )
            overlapping = _normalize_overlapping_value(
                result[OVERLAPPING_COL]
            )

            if network not in network_orders:
                network_orders[network] = len(network_orders)

            row = {
                ALGORITHM_COL: str(result[ALGORITHM_COL]).strip(),
                NETWORK_COL: network,
                OVERLAPPING_COL: overlapping,
                NETWORK_ORDER_COL: network_orders[network],
                SOURCE_FILE_COL: str(result_file),
            }

            applicable_metrics = (
                OVERLAPPING_METRICS
                if overlapping == "Yes"
                else NON_OVERLAPPING_METRICS
            )

            for metric_col in applicable_metrics:
                if metric_col == RUNTIME_COL:
                    source_col = runtime_input_col
                else:
                    source_col = metric_col

                if source_col is None or source_col not in results_df.columns:
                    metric_mean = float("nan")
                    metric_reported_std = float("nan")
                else:
                    metric_mean, metric_reported_std = _parse_mean_and_std(
                        result[source_col]
                    )

                row[metric_col] = metric_mean
                row[_reported_std_col(metric_col)] = metric_reported_std

            rows.append(row)

    if not rows:
        raise ValueError(
            f"[ERROR] No comparison rows were found in '{results_dir}'."
        )

    raw_df = pd.DataFrame(rows)

    # Ensure every metric column exists, even when the uploaded result set
    # contains only one ground-truth type.
    for metric_col in ALL_METRICS:
        if metric_col not in raw_df.columns:
            raw_df[metric_col] = float("nan")
        reported_std_col = _reported_std_col(metric_col)
        if reported_std_col not in raw_df.columns:
            raw_df[reported_std_col] = float("nan")

    raw_df[ALGORITHM_COL] = _algorithm_categorical(raw_df[ALGORITHM_COL])
    raw_df = (
        raw_df
        .sort_values(
            [
                OVERLAPPING_COL,
                NETWORK_ORDER_COL,
                ALGORITHM_COL,
            ]
        )
        .reset_index(drop=True)
    )
    raw_df[ALGORITHM_COL] = raw_df[ALGORITHM_COL].astype(str)

    summary_df = _compute_summary(raw_df)

    raw_df.to_csv(
        os.path.join(
            results_dir,
            "real_world_spectral_comparison_results.csv",
        ),
        index=False,
    )

    summary_df.to_csv(
        os.path.join(
            results_dir,
            "real_world_spectral_comparison_summary.csv",
        ),
        index=False,
    )

    _plot_ground_truth_group(
        results_dir=results_dir,
        summary_df=summary_df,
        overlapping="No",
        metrics=NON_OVERLAPPING_PLOT_METRICS,
        output_filename="non_overlapping_real_world_spectral_algorithms",
        title="Non-overlapping Real-World Networks",
    )

    _plot_ground_truth_group(
        results_dir=results_dir,
        summary_df=summary_df,
        overlapping="Yes",
        metrics=OVERLAPPING_PLOT_METRICS,
        output_filename="overlapping_real_world_spectral_algorithms",
        title="Overlapping Real-World Networks",
    )


def _compute_summary(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate parsed rows by ground-truth type, network, and algorithm.

    Normally each group contains one result row. Grouping also makes the
    script robust to duplicated or repeated comparison rows and gives every
    plotted value an explicit mean.
    """

    aggregation = {
        "#Rows": (ALGORITHM_COL, "size"),
        NETWORK_ORDER_COL: (NETWORK_ORDER_COL, "min"),
    }

    for metric_col in ALL_METRICS:
        aggregation.update({
            f"{metric_col} Results": (metric_col, _results_as_json),
            f"Mean {metric_col}": (metric_col, "mean"),
            f"Sample Std {metric_col}": (
                metric_col,
                lambda series: series.std(ddof=1),
            ),
            f"Reported Std {metric_col} Results": (
                _reported_std_col(metric_col),
                _results_as_json,
            ),
            f"Mean Reported Std {metric_col}": (
                _reported_std_col(metric_col),
                "mean",
            ),
        })

    summary_df = (
        raw_df
        .groupby(
            [OVERLAPPING_COL, NETWORK_COL, ALGORITHM_COL],
            as_index=False,
            observed=True,
            dropna=False,
        )
        .agg(**aggregation)
    )

    summary_df[ALGORITHM_COL] = _algorithm_categorical(
        summary_df[ALGORITHM_COL]
    )
    summary_df = (
        summary_df
        .sort_values(
            [
                OVERLAPPING_COL,
                NETWORK_ORDER_COL,
                ALGORITHM_COL,
            ]
        )
        .reset_index(drop=True)
    )
    summary_df[ALGORITHM_COL] = summary_df[ALGORITHM_COL].astype(str)

    numeric_summary_columns = [
        column
        for column in summary_df.columns
        if (
                   column.startswith("Mean ")
                   or column.startswith("Sample Std ")
           )
           and not column.endswith(" Results")
    ]

    summary_df[numeric_summary_columns] = (
        summary_df[numeric_summary_columns]
        .round(6)
    )

    return summary_df


def _plot_ground_truth_group(
        results_dir: str,
        summary_df: pd.DataFrame,
        overlapping: str,
        metrics: tuple[str, ...],
        output_filename: str,
        title: str,
) -> None:
    """Plot grouped algorithm bars for one ground-truth type."""

    plot_df = summary_df[
        summary_df[OVERLAPPING_COL] == overlapping
        ].copy()

    if plot_df.empty:
        return

    available_metrics = [
        metric_col
        for metric_col in metrics
        if (
                f"Mean {metric_col}" in plot_df.columns
                and plot_df[f"Mean {metric_col}"].notna().any()
        )
    ]

    if not available_metrics:
        return

    network_order_df = (
        plot_df[[NETWORK_COL, NETWORK_ORDER_COL]]
        .drop_duplicates()
        .sort_values(NETWORK_ORDER_COL)
    )
    networks = network_order_df[NETWORK_COL].tolist()
    display_networks = [_format_network_label(network) for network in networks]
    x_positions = np.arange(len(networks), dtype=float)

    algorithms = _ordered_algorithms(plot_df[ALGORITHM_COL])
    if not algorithms:
        return

    # Distinct colours improve readability on screen, while opposite hatch
    # directions keep the algorithms distinguishable in black-and-white print.
    algorithm_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    algorithm_hatches = [r"\\", "//", "xx", ".."]

    total_group_width = 0.82
    bar_width = total_group_width / len(algorithms)
    first_offset = -total_group_width / 2.0 + bar_width / 2.0

    number_of_columns = 2
    number_of_rows = math.ceil(len(available_metrics) / number_of_columns)

    fig, axes = plt.subplots(
        number_of_rows,
        number_of_columns,
        figsize=(7.2, 2.7 * number_of_rows),
        squeeze=False,
    )
    flattened_axes = axes.flatten()

    for axis, metric_col in zip(flattened_axes, available_metrics):
        mean_metric_col = f"Mean {metric_col}"

        for algorithm_index, algorithm in enumerate(algorithms):
            algorithm_df = (
                plot_df[plot_df[ALGORITHM_COL] == algorithm]
                .set_index(NETWORK_COL)
            )
            values = (
                pd.to_numeric(
                    algorithm_df[mean_metric_col],
                    errors="coerce",
                )
                .reindex(networks)
                .to_numpy(dtype=float)
            )

            std_metric_col = f"Mean Reported Std {metric_col}"

            if std_metric_col in algorithm_df.columns:
                std_values = (
                    pd.to_numeric(
                        algorithm_df[std_metric_col],
                        errors="coerce",
                    )
                    .reindex(networks)
                    .to_numpy(dtype=float)
                )

                if np.isnan(std_values).all():
                    std_values = None
                else:
                    std_values = np.nan_to_num(std_values, nan=0.0)
            else:
                std_values = None

            offset = first_offset + algorithm_index * bar_width
            axis.bar(
                x_positions + offset,
                values,
                width=bar_width,
                yerr=std_values,
                capsize=2 if std_values is not None else 0,
                label=algorithm,
                color=algorithm_colors[algorithm_index % len(algorithm_colors)],
                hatch=algorithm_hatches[algorithm_index % len(algorithm_hatches)],
                edgecolor="black",
                linewidth=0.8,
                zorder=3,
            )

        axis.set_xlabel("Network", fontsize=7)
        axis.set_ylabel(
            METRIC_LABELS.get(metric_col, mean_metric_col),
            fontsize=7,
        )
        axis.set_xticks(x_positions)
        axis.set_xticklabels(
            display_networks,
            rotation=30,
            ha="right",
            fontsize=5.5,
        )
        axis.tick_params(axis="y", labelsize=6)
        axis.margins(x=0.01)
        axis.grid(True, axis="y", alpha=0.3, zorder=0)

        _set_metric_limits(axis, metric_col, plot_df[mean_metric_col])

        handles, labels = axis.get_legend_handles_labels()
        if handles:
            axis.legend(
                loc="best",
                fontsize=5.5,
                framealpha=0.3,
                ncol=1,
                columnspacing=0.6,
                handletextpad=0.3,
            )

    for axis in flattened_axes[len(available_metrics):]:
        axis.axis("off")

    fig.tight_layout(
        rect=(0.0, 0.0, 1.0, 0.96),
        pad=0.8,
        h_pad=1.0,
        w_pad=1.0,
    )
    fig.savefig(
        os.path.join(results_dir, f"{output_filename}.pdf"),
        dpi=300,
        bbox_inches="tight",
    )

    fig.savefig(
        os.path.join(results_dir, f"{output_filename}.png"),
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def _format_network_label(network: str) -> str:
    """Return a compact network label for figures without changing stored names."""

    if network.startswith("facebook-network-"):
        return network.removeprefix("facebook-network-")

    return network


def _set_metric_limits(
        axis,
        metric_col: str,
        values: pd.Series,
) -> None:
    """Apply meaningful y-axis limits without clipping negative metrics."""

    metrics_bounded_between_zero_and_one = {
        F_MEASURE_COL,
        FMI_COL,
        NMI_COL,
        ONMI_COL,
        OMEGA_COL,
        CONDUCTANCE_COL,
    }

    metrics_with_nonnegative_values = {
        KERR_COL,
        VI_COL,
        CONDUCTANCE_BN_COL,
        RUNTIME_COL,
    }

    if metric_col in metrics_bounded_between_zero_and_one:
        axis.set_ylim(0.0, 1.0)
    elif metric_col in metrics_with_nonnegative_values:
        axis.set_ylim(bottom=0.0)
    elif metric_col in {AMI_COL, ARI_COL, MODULARITY_COL, FUZZY_MODULARITY_COL}:
        finite_values = pd.to_numeric(values, errors="coerce").dropna()
        if not finite_values.empty and finite_values.min() >= 0.0:
            axis.set_ylim(bottom=0.0)


def _iter_result_files(
        results_dir: str,
        input_filename: str,
) -> list[Path]:
    """Return all comparison result files recursively, sorted by path."""

    root_path = Path(results_dir)
    if not root_path.exists():
        raise FileNotFoundError(
            f"[ERROR] Results directory does not exist: '{results_dir}'."
        )
    if not root_path.is_dir():
        raise NotADirectoryError(
            f"[ERROR] Results path is not a directory: '{results_dir}'."
        )

    return sorted(
        root_path.rglob(input_filename),
        key=lambda path: str(path).lower(),
    )


def _read_csv(csv_path: str | Path) -> pd.DataFrame:
    """Read a comparison CSV file and normalize its column names."""

    dataframe = pd.read_csv(csv_path, sep=",", engine="python")
    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]
    return dataframe


def _resolve_network_name(
        result: pd.Series,
        result_file: Path,
) -> str:
    """Use the CSV network value, falling back to the parent folder name."""

    if NETWORK_COL in result.index:
        network = str(result[NETWORK_COL]).strip()
        if network and network.lower() not in {"nan", "none", "-"}:
            return network

    return result_file.parent.name


def _normalize_overlapping_value(value) -> str:
    """Normalize supported boolean-like values to 'Yes' or 'No'."""

    normalized = str(value).strip().lower()

    if normalized in {"yes", "true", "1", "overlapping"}:
        return "Yes"
    if normalized in {"no", "false", "0", "non-overlapping", "nonoverlapping"}:
        return "No"

    raise ValueError(
        f"[ERROR] Invalid value in '{OVERLAPPING_COL}': '{value}'."
    )


def _find_runtime_column(dataframe: pd.DataFrame) -> str | None:
    """Return the first supported runtime column found in the dataframe."""

    for runtime_column in RUNTIME_INPUT_COLS:
        if runtime_column in dataframe.columns:
            return runtime_column

    return None


def _parse_mean_and_std(value) -> tuple[float, float]:
    """
    Parse either a scalar or a "mean ± sample standard deviation" value.

    Returns:
        mean : (float)
            Parsed scalar value or mean component.
        sample_std : (float)
            Parsed sample standard deviation, or NaN for scalar input.
    """

    if pd.isna(value):
        return float("nan"), float("nan")

    text = str(value).strip()

    if text in {"", "-", "None", "none", "nan", "NaN"}:
        return float("nan"), float("nan")

    if "±" in text:
        mean_text, std_text = text.split("±", maxsplit=1)
        mean = pd.to_numeric(mean_text.strip(), errors="coerce")
        sample_std = pd.to_numeric(std_text.strip(), errors="coerce")
        return float(mean), float(sample_std)

    mean = pd.to_numeric(text, errors="coerce")
    return float(mean), float("nan")


def _reported_std_col(metric_col: str) -> str:
    """Build the raw-data column name for a reported within-network std."""

    return f"Reported Std {metric_col}"


def _results_as_json(series: pd.Series) -> str:
    """Convert numeric result values into a JSON list."""

    values = [
        None
        if pd.isna(value)
        else round(float(value), 6)
        for value in series.tolist()
    ]
    return json.dumps(values)


def _algorithm_categorical(series: pd.Series) -> pd.Categorical:
    """Create an algorithm categorical with a deterministic order."""

    observed_algorithms = [
        str(algorithm)
        for algorithm in series.dropna().unique()
    ]
    categories = list(ALGORITHM_ORDER)
    categories.extend(
        algorithm
        for algorithm in observed_algorithms
        if algorithm not in categories
    )

    return pd.Categorical(
        series,
        categories=categories,
        ordered=True,
    )


def _ordered_algorithms(series: pd.Series) -> list[str]:
    """Return observed algorithms in the preferred deterministic order."""

    observed = {
        str(algorithm)
        for algorithm in series.dropna().unique()
    }

    ordered = [
        algorithm
        for algorithm in ALGORITHM_ORDER
        if algorithm in observed
    ]
    ordered.extend(sorted(observed - set(ordered)))

    return ordered


if __name__ == "__main__":
    for folders in [
        ("spectral-baseline", "results_2026-07-28_00-19-10-252503"),
        ("spectral-baseline", "results_2026-07-28_19-09-24-292455"),
        ("spectral-baseline", "results_2026-07-28_19-24-47-069592"),
    ]:
        plot_real_world_spectral_comparison_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR,
                folders[0],
                folders[1],
            )
        )
