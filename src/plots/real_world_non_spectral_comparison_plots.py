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
    'stage2',
)

# Result CSV column names.
ALGORITHM_COL = "Algorithm"
NETWORK_COL = "Network"
OVERLAPPING_COL = "Overlapping?"
KERR_COL = "|K'-K|/K"
ONMI_COL = "ONMI"
OMEGA_COL = "Omega"
FUZZY_MODULARITY_COL = "Fuzzy-Modularity"
CONDUCTANCE_BN_COL = "Conductance-BN"

# The current comparison CSV labels the generic runtime as "FADDIS Runtime"
# for every algorithm. "Runtime" is also accepted for a corrected schema.
RUNTIME_INPUT_COLS = ("Runtime", "FADDIS Runtime")
RUNTIME_COL = "Runtime"

SOURCE_FILE_COL = "Source File"
NETWORK_ORDER_COL = "Network Order"

# Preferred algorithm order in CSV summaries and plots.
ALGORITHM_ORDER = ("FADDIS", "SLPA", "CFinder")

# Non-spectral algorithms are evaluated as community covers for both
# non-overlapping and overlapping ground-truth networks.
METRICS = (
    ONMI_COL,
    OMEGA_COL,
    KERR_COL,
    FUZZY_MODULARITY_COL,
    CONDUCTANCE_BN_COL,
    RUNTIME_COL,
)

# Metrics shown in the figures. Runtime is retained in the generated CSV files
# but intentionally omitted from the plots.
PLOT_METRICS = (
    ONMI_COL,
    OMEGA_COL,
    KERR_COL,
    FUZZY_MODULARITY_COL,
    CONDUCTANCE_BN_COL,
)

# Human-readable y-axis labels.
METRIC_LABELS = {
    ONMI_COL: "Mean ONMI",
    OMEGA_COL: "Mean Omega",
    KERR_COL: r"Mean Relative Error $|K'-K|/K$",
    FUZZY_MODULARITY_COL: "Mean Fuzzy-Modularity",
    CONDUCTANCE_BN_COL: "Mean Conductance-BN",
    RUNTIME_COL: "Mean Runtime (seconds)",
}

# Distinct colours improve readability on screen, while hatches keep the
# algorithms distinguishable when the figures are printed in black and white.
ALGORITHM_COLORS = {
    "FADDIS": "tab:blue",
    "SLPA": "tab:orange",
    "CFinder": "tab:green",
}
ALGORITHM_HATCHES = {
    "FADDIS": r"\\",
    "SLPA": "//",
    "CFinder": "xx",
}


def plot_real_world_non_spectral_comparison_results(
        results_dir: str,
        input_filename: str = "_comparison_results.csv",
) -> None:
    """
    Process and plot non-spectral comparison results for real-world networks.

    Result files are discovered recursively because the real-world runner organizes
    results by network family and then by network name. Metric values can be scalar
    values or strings formatted as "mean ± sample standard deviation". The mean
    component is used as the bar height, while the reported standard deviation,
    when available, is shown using error bars and retained in the generated CSV
    files.

    Results are separated according to the resolved overlap type. The explicit
    "Overlapping?" column is used when available; otherwise, the overlap type is
    inferred from the fuzzy intrinsic metrics. The final comparison figure includes
    the supported metrics available in the input files. Runtime is retained in the
    generated CSV files but omitted from the figure.

    Parameters:
        results_dir : (str)
            Root directory containing the real-world non-spectral comparison
            results. The function searches recursively for each network's
            comparison CSV file.
        input_filename : (str, optional)
            Name of the comparison results file saved in each network directory.
            Default is "_comparison_results.csv".

    Saves:
        - "real_world_non_spectral_comparison_results.csv": parsed raw rows.
        - "real_world_non_spectral_comparison_summary.csv": results grouped by
          ground-truth type, network, and algorithm.
        - "non_overlapping_real_world_non_spectral_algorithms.pdf": grouped bar
          plots for non-overlapping networks, when available.
        - "overlapping_real_world_non_spectral_algorithms.pdf": grouped bar plots
          for overlapping networks, when available.

    Returns:
        None
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
        }
        missing_columns = required_columns - set(results_df.columns)
        if missing_columns:
            raise ValueError(
                f"[ERROR] Missing columns in '{result_file}': "
                f"{sorted(missing_columns)}."
            )

        supported_metric_columns = set(PLOT_METRICS) & set(results_df.columns)
        if not supported_metric_columns:
            raise ValueError(
                f"[ERROR] No supported comparison metrics were found in "
                f"'{result_file}'."
            )

        for _, result in results_df.iterrows():
            network = _resolve_network_name(
                result=result,
                result_file=result_file,
            )
            overlapping = _resolve_overlapping_value(result)

            if network not in network_orders:
                network_orders[network] = len(network_orders)

            row = {
                ALGORITHM_COL: str(result[ALGORITHM_COL]).strip(),
                NETWORK_COL: network,
                OVERLAPPING_COL: overlapping,
                NETWORK_ORDER_COL: network_orders[network],
                SOURCE_FILE_COL: str(result_file),
            }

            for metric_col in METRICS:
                source_col = (
                    runtime_input_col
                    if metric_col == RUNTIME_COL
                    else metric_col
                )

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
            "real_world_non_spectral_comparison_results.csv",
        ),
        index=False,
    )

    summary_df.to_csv(
        os.path.join(
            results_dir,
            "real_world_non_spectral_comparison_summary.csv",
        ),
        index=False,
    )

    _plot_ground_truth_group(
        results_dir=results_dir,
        summary_df=summary_df,
        overlapping="Yes",
        output_filename="overlapping_real_world_non_spectral_algorithms",
        title="Overlapping Real-World Networks",
    )


def _compute_summary(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate parsed rows by ground-truth type, network, and algorithm.

    Normally, each group contains one result row. Grouping also makes the script
    robust to duplicated or repeated comparison rows and gives every plotted value
    an explicit mean.

    Parameters:
        raw_df : (pd.DataFrame)
            Dataframe containing the parsed comparison rows.

    Returns:
        summary_df : (pd.DataFrame)
            Aggregated results grouped by ground-truth type, network, and algorithm.
    """

    aggregation = {
        "#Rows": (ALGORITHM_COL, "size"),
        NETWORK_ORDER_COL: (NETWORK_ORDER_COL, "min"),
    }

    for metric_col in METRICS:
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
        output_filename: str,
        title: str,
) -> None:
    """
    Plot grouped algorithm bars for one ground-truth type.

    Parameters:
        results_dir : (str)
            Directory in which the generated figures are saved.
        summary_df : (pd.DataFrame)
            Aggregated comparison results.
        overlapping : (str)
            Ground-truth overlap indicator used to select the network group.
        output_filename : (str)
            Base filename used for the generated figures.
        title : (str)
            Descriptive title associated with the network group.

    Returns:
        None
    """

    plot_df = summary_df[
        summary_df[OVERLAPPING_COL] == overlapping
        ].copy()

    if plot_df.empty:
        return

    available_metrics = [
        metric_col
        for metric_col in PLOT_METRICS
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

    total_group_width = 0.82
    bar_width = total_group_width / len(algorithms)
    first_offset = -total_group_width / 2.0 + bar_width / 2.0

    fig, flattened_axes = _create_metric_axes(
        number_of_metrics=len(available_metrics),
        row_height=2.7,
    )

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
                color=_algorithm_color(algorithm, algorithm_index),
                hatch=_algorithm_hatch(algorithm, algorithm_index),
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

        _set_metric_limits(axis, metric_col)

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



def _create_metric_axes(
        number_of_metrics: int,
        row_height: float,
) -> tuple:
    """
    Create a balanced figure layout for the requested number of metrics.

    Five-metric figures use two wider plots on the first row and three equal
    plots on the second row. Four-metric figures use a regular 2-by-2 layout.

    Parameters:
        number_of_metrics : (int)
            Number of metric plots to create.
        row_height : (float)
            Height allocated to each figure row.

    Returns:
        fig :
            Matplotlib figure.
        axes : (np.ndarray)
            Flattened array containing the created axes.
    """

    if number_of_metrics == 5:
        fig = plt.figure(figsize=(7.2, row_height * 2))
        grid = fig.add_gridspec(2, 6)

        axes = [
            fig.add_subplot(grid[0, 0:3]),
            fig.add_subplot(grid[0, 3:6]),
            fig.add_subplot(grid[1, 0:2]),
            fig.add_subplot(grid[1, 2:4]),
            fig.add_subplot(grid[1, 4:6]),
        ]

        return fig, np.asarray(axes)

    if number_of_metrics == 4:
        fig, axes = plt.subplots(
            2,
            2,
            figsize=(7.2, row_height * 2),
            squeeze=False,
        )
        return fig, axes.flatten()

    number_of_columns = min(number_of_metrics, 3)
    number_of_rows = math.ceil(number_of_metrics / number_of_columns)

    fig, axes = plt.subplots(
        number_of_rows,
        number_of_columns,
        figsize=(7.2, row_height * number_of_rows),
        squeeze=False,
    )

    return fig, axes.flatten()


def _format_network_label(network: str) -> str:
    """
    Return the original network name for figure labels.

    Parameters:
        network : (str)
            Original network name.

    Returns:
        label : (str)
            Original network name used in figures.
    """

    return network


def _set_metric_limits(axis, metric_col: str) -> None:
    """
    Apply meaningful y-axis limits for a metric.

    Parameters:
        axis :
            Matplotlib axis to update.
        metric_col : (str)
            Metric represented on the axis.

    Returns:
        None
    """

    if metric_col in {ONMI_COL, OMEGA_COL}:
        axis.set_ylim(0.0, 1.0)
    elif metric_col in {KERR_COL, CONDUCTANCE_BN_COL, RUNTIME_COL}:
        axis.set_ylim(bottom=0.0)


def _algorithm_color(algorithm: str, algorithm_index: int) -> str:
    """
    Return a deterministic display colour for an algorithm.

    Parameters:
        algorithm : (str)
            Algorithm name.
        algorithm_index : (int)
            Position of the algorithm in the plotted order.

    Returns:
        color : (str)
            Display colour associated with the algorithm.
    """

    fallback_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    return ALGORITHM_COLORS.get(
        algorithm,
        fallback_colors[algorithm_index % len(fallback_colors)],
    )


def _algorithm_hatch(algorithm: str, algorithm_index: int) -> str:
    """
    Return a deterministic print-friendly hatch for an algorithm.

    Parameters:
        algorithm : (str)
            Algorithm name.
        algorithm_index : (int)
            Position of the algorithm in the plotted order.

    Returns:
        hatch : (str)
            Hatch pattern associated with the algorithm.
    """

    fallback_hatches = [r"\\", "//", "xx", ".."]
    return ALGORITHM_HATCHES.get(
        algorithm,
        fallback_hatches[algorithm_index % len(fallback_hatches)],
    )


def _iter_result_files(
        results_dir: str,
        input_filename: str,
) -> list[Path]:
    """
    Return all comparison result files recursively, sorted by path.

    Parameters:
        results_dir : (str)
            Root directory containing the comparison results.
        input_filename : (str)
            Name of the comparison results file to locate.

    Returns:
        result_files : (list[Path])
            Matching comparison result files sorted by path.
    """

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


def _read_csv(csv_path: str) -> pd.DataFrame:
    """
    Read a result CSV file and normalize its column names.

    Parameters:
        csv_path : (str | Path)
            Path to the input CSV file.

    Returns:
        dataframe : (pd.DataFrame)
            Loaded dataframe with normalized column names.
    """

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
    """
    Resolve the network name from a result row or its parent directory.

    Parameters:
        result : (pd.Series)
            Result row containing the optional network name.
        result_file : (Path)
            Path to the result file.

    Returns:
        network_name : (str)
            Network name from the CSV row, falling back to the parent directory
            name when necessary.
    """

    if NETWORK_COL in result.index:
        network = str(result[NETWORK_COL]).strip()
        if network and network.lower() not in {"nan", "none", "-"}:
            return network

    return result_file.parent.name



def _resolve_overlapping_value(result: pd.Series) -> str:
    """
    Resolve whether a result row represents an overlapping cover.

    The explicit "Overlapping?" value is used when available. If the column is
    absent, the cover is inferred from the fuzzy intrinsic metrics used by the
    non-spectral comparison.

    Parameters:
        result : (pd.Series)
            Result row containing the comparison metrics.

    Returns:
        overlapping : (str)
            Normalized overlap indicator, either "Yes" or "No".
    """

    if (
            OVERLAPPING_COL in result.index
            and _has_result_value(result[OVERLAPPING_COL])
    ):
        return _normalize_overlapping_value(result[OVERLAPPING_COL])

    overlapping_metrics_present = any(
        metric_col in result.index and _has_result_value(result[metric_col])
        for metric_col in (FUZZY_MODULARITY_COL, CONDUCTANCE_BN_COL)
    )

    if overlapping_metrics_present:
        return "Yes"

    raise ValueError(
        "[ERROR] Unable to infer whether the result is overlapping. "
        "Add an 'Overlapping?' column or provide the fuzzy intrinsic metrics."
    )


def _has_result_value(value) -> bool:
    """
    Return whether a result cell contains a usable value.

    Parameters:
        value :
            Result cell value.

    Returns:
        has_value : (bool)
            True when the cell contains a non-missing value.
    """

    if pd.isna(value):
        return False

    return str(value).strip().lower() not in {
        "",
        "-",
        "--",
        "none",
        "nan",
        "n/a",
    }


def _normalize_overlapping_value(value) -> str:
    """
    Normalize a supported boolean-like value to "Yes" or "No".

    Parameters:
        value :
            Value representing whether the ground truth is overlapping.

    Returns:
        normalized_value : (str)
            Normalized overlap indicator, either "Yes" or "No".
    """

    normalized = str(value).strip().lower()

    if normalized in {"yes", "true", "1", "overlapping"}:
        return "Yes"
    if normalized in {"no", "false", "0", "non-overlapping", "nonoverlapping"}:
        return "No"

    raise ValueError(
        f"[ERROR] Invalid value in '{OVERLAPPING_COL}': '{value}'."
    )


def _find_runtime_column(dataframe: pd.DataFrame) -> str:
    """
    Return the first supported runtime column found in the dataframe.

    Parameters:
        dataframe : (pd.DataFrame)
            Dataframe containing the comparison results.

    Returns:
        runtime_column : (str | None)
            Name of the first supported runtime column, or None if no supported
            runtime column is present.
    """

    for runtime_column in RUNTIME_INPUT_COLS:
        if runtime_column in dataframe.columns:
            return runtime_column

    return None


def _parse_mean_and_std(value) -> tuple[float, float]:
    """
    Parse either a scalar value or a "mean ± sample standard deviation" value.

    Parameters:
        value :
            Value to parse.

    Returns:
        mean : (float)
            Parsed scalar value or mean component.
        sample_std : (float)
            Parsed sample standard deviation, or NaN when the input contains only
            one scalar value.
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
    """
    Build the raw-data column name for a reported within-network standard deviation.

    Parameters:
        metric_col : (str)
            Metric column name.

    Returns:
        reported_std_col : (str)
            Column name used to store the reported within-network standard
            deviation.
    """

    return f"Reported Std {metric_col}"


def _results_as_json(series: pd.Series) -> str:
    """
    Convert numeric result values into a JSON list.

    Parameters:
        series : (pd.Series)
            Series containing numeric result values.

    Returns:
        results_json : (str)
            JSON representation of the finite numeric values.
    """

    values = [
        None
        if pd.isna(value)
        else round(float(value), 6)
        for value in series.tolist()
    ]
    return json.dumps(values)


def _algorithm_categorical(series: pd.Series) -> pd.Categorical:
    """
    Create an algorithm categorical with a deterministic order.

    Parameters:
        series : (pd.Series)
            Series containing algorithm names.

    Returns:
        categorical : (pd.Series)
            Categorical series using the preferred deterministic algorithm order.
    """

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
    """
    Return observed algorithms in the preferred deterministic order.

    Parameters:
        series : (pd.Series)
            Series containing algorithm names.

    Returns:
        algorithms : (list[str])
            Observed algorithm names in deterministic order.
    """

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
        ##("non-spectral-baseline", "results_2026-07-28_01-06-56-313643"),
        ##("non-spectral-baseline", "results_2026-07-28_19-12-41-695604"),
        ##("non-spectral-baseline", "results_2026-07-28_19-28-06-901203"),
        ("non-spectral-baseline", "results_2026-09-07_13-31-07-632881"),
        ("non-spectral-baseline", "results_2026-09-07_13-46-48-687558"),
    ]:
        plot_real_world_non_spectral_comparison_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR,
                folders[0],
                folders[1],
            )
        )
