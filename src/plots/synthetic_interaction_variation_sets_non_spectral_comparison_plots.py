import json
import os.path
import re
from itertools import cycle
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

# Base directory for results.
RESULTS_BASE_DIR = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'archive',
    'results',
    'synthetic',
)

# Suggested base directory for the interaction-variation-set results.
INTERACTION_RESULTS_BASE_DIR = os.path.join(
    RESULTS_BASE_DIR,
    'baselines_test',
    'ivs',
)

# Network property keys.
NETWORK_PROPERTY_N = "n"
NETWORK_PROPERTY_MU = "mu"
NETWORK_PROPERTY_ON = "on"
NETWORK_PROPERTY_OM = "om"
NETWORK_PROPERTY_INST = "inst"

# Result CSV column names.
ALGORITHM_COL = "Algorithm"
NETWORK_COL = "Network"
KERR_COL = "|K'-K|/K"
ONMI_COL = "ONMI"
OMEGA_COL = "Omega"
FUZZY_MODULARITY_COL = "Fuzzy-Modularity"
CONDUCTANCE_BN_COL = "Conductance-BN"

# The current comparison results file uses "FADDIS Runtime" for all algorithms.
# "Runtime" is also accepted to support a corrected label.
RUNTIME_INPUT_COLS = ("Runtime", "FADDIS Runtime")
RUNTIME_COL = "Runtime"

METRIC_COLS = (
    ONMI_COL,
    OMEGA_COL,
    KERR_COL,
    FUZZY_MODULARITY_COL,
    CONDUCTANCE_BN_COL,
    RUNTIME_COL,
)

# Metrics shown in the figures. Runtime is retained in the generated CSV files
# but intentionally omitted from the plots.
PLOT_METRIC_COLS = (
    ONMI_COL,
    OMEGA_COL,
    KERR_COL,
    FUZZY_MODULARITY_COL,
    CONDUCTANCE_BN_COL,
)

# Algorithm order used in summaries and plots.
ALGORITHM_ORDER = ("FADDIS (Default)", "FADDIS (IP_beta0)", "SLPA", "CFinder")

# Labels used for the x-axis and interaction legend.
VARIATION_PARAMETER_LABELS = {
    NETWORK_PROPERTY_N: r"$n$",
    NETWORK_PROPERTY_MU: r"$\mu$",
    NETWORK_PROPERTY_ON: r"$o_n$",
    NETWORK_PROPERTY_OM: r"$o_m$",
}

SUPPORTED_VARIATION_PARAMETERS = tuple(VARIATION_PARAMETER_LABELS.keys())

# Example network name: n1000mu0.4on300om4inst1
NETWORK_RE = re.compile(
    r"n(?P<n>\d+)"
    r"mu(?P<mu>\d*\.?\d+)"
    r"on(?P<on>\d+)"
    r"om(?P<om>\d+)"
    r"inst(?P<inst>\d+)"
)

# The algorithm is encoded by marker/colour; the second LFR parameter is
# encoded by line style.
INTERACTION_LINE_STYLES = ("-", "--", ":", "-.")


def plot_non_spectral_comparison_interaction_variation_set_results(
        results_dir: str,
        variation_parameter: str,
        interaction_parameter: str,
        input_filename: str = "_comparison_results.csv",
) -> None:
    """
    Process non-spectral comparison results for a two-parameter LFR interaction set.

    Metric values are aggregated across network instances for each combination
    of the x-axis variation parameter, interaction parameter, and algorithm.
    The algorithm is represented by marker/colour and the interaction level by
    line style. Sample standard deviations across network instances and
    reported within-instance standard deviations across stochastic executions,
    when available, are both shown as error bars.

    Parameters:
        results_dir : (str)
            Directory containing the experiment results, organized in
            subdirectories for each network instance.
        variation_parameter : (str)
            Network property represented on the x-axis.
        interaction_parameter : (str)
            Second varied network property, represented by line style.
        input_filename : (str, optional)
            Name of the comparison CSV file in each network directory.
            Default is "_comparison_results.csv".

    Saves:
        - Parsed per-network algorithm results:
          "{variation_parameter}_x_{interaction_parameter}_non_spectral_comparison_results.csv".
        - Aggregated interaction summary:
          "{variation_parameter}_x_{interaction_parameter}_non_spectral_comparison_summary.csv".
        - PDF and PNG interaction plots:
          "{variation_parameter}_x_{interaction_parameter}_non_spectral_algorithms.*".

    Returns:
        None
    """

    _validate_interaction_parameters(
        variation_parameter=variation_parameter,
        interaction_parameter=interaction_parameter,
    )

    rows = []

    for network_dir in _iter_sorted_dirs(results_dir):
        properties = _parse_network_name(network_dir.name)
        if properties is None:
            raise ValueError(
                f"[ERROR] Invalid network directory name: '{network_dir.name}'."
            )

        results_csv_path = os.path.join(network_dir, input_filename)
        results_df = _read_csv(results_csv_path)
        runtime_input_col = _find_runtime_column(results_df)

        required_columns = {
            ALGORITHM_COL,
            ONMI_COL,
            OMEGA_COL,
            KERR_COL,
            FUZZY_MODULARITY_COL,
            CONDUCTANCE_BN_COL,
        }
        missing_columns = required_columns - set(results_df.columns)
        if missing_columns:
            raise ValueError(
                f"[ERROR] Missing columns in '{results_csv_path}': "
                f"{sorted(missing_columns)}."
            )

        for _, result in results_df.iterrows():
            row = {
                ALGORITHM_COL: str(result[ALGORITHM_COL]).strip(),
                NETWORK_COL: network_dir.name,
                NETWORK_PROPERTY_N: properties[NETWORK_PROPERTY_N],
                NETWORK_PROPERTY_MU: properties[NETWORK_PROPERTY_MU],
                NETWORK_PROPERTY_ON: properties[NETWORK_PROPERTY_ON],
                NETWORK_PROPERTY_OM: properties[NETWORK_PROPERTY_OM],
                NETWORK_PROPERTY_INST: properties[NETWORK_PROPERTY_INST],
            }

            for metric_col in (
                    ONMI_COL,
                    OMEGA_COL,
                    KERR_COL,
                    FUZZY_MODULARITY_COL,
                    CONDUCTANCE_BN_COL,
            ):
                metric_mean, metric_reported_std = _parse_mean_and_std(
                    result[metric_col]
                )
                row[metric_col] = metric_mean
                row[_reported_std_col(metric_col)] = metric_reported_std

            if runtime_input_col is not None:
                runtime_mean, runtime_reported_std = _parse_mean_and_std(
                    result[runtime_input_col]
                )
            else:
                runtime_mean, runtime_reported_std = float("nan"), float("nan")

            row[RUNTIME_COL] = runtime_mean
            row[_reported_std_col(RUNTIME_COL)] = runtime_reported_std

            rows.append(row)

    if not rows:
        raise ValueError(
            f"[ERROR] No comparison results were found in '{results_dir}'."
        )

    raw_df = pd.DataFrame(rows)
    raw_df[ALGORITHM_COL] = _algorithm_categorical(raw_df[ALGORITHM_COL])
    raw_df = (
        raw_df
        .sort_values(
            [
                variation_parameter,
                interaction_parameter,
                ALGORITHM_COL,
                NETWORK_PROPERTY_INST,
                NETWORK_COL,
            ]
        )
        .reset_index(drop=True)
    )
    raw_df[ALGORITHM_COL] = raw_df[ALGORITHM_COL].astype(str)

    summary_df = _compute_summary(
        raw_df=raw_df,
        variation_parameter=variation_parameter,
        interaction_parameter=interaction_parameter,
    )

    output_prefix = _interaction_output_prefix(
        variation_parameter=variation_parameter,
        interaction_parameter=interaction_parameter,
    )

    raw_df.to_csv(
        os.path.join(
            results_dir,
            f"{output_prefix}_non_spectral_comparison_results.csv",
        ),
        index=False,
    )

    summary_df.to_csv(
        os.path.join(
            results_dir,
            f"{output_prefix}_non_spectral_comparison_summary.csv",
        ),
        index=False,
    )

    _plot_results(
        results_dir=results_dir,
        summary_df=summary_df,
        variation_parameter=variation_parameter,
        interaction_parameter=interaction_parameter,
    )


def _compute_summary(
        raw_df: pd.DataFrame,
        variation_parameter: str,
        interaction_parameter: str,
) -> pd.DataFrame:
    """Aggregate per-network metric means by both LFR parameters and algorithm."""

    aggregation = {
        "#Instances": (NETWORK_PROPERTY_INST, "nunique"),
    }

    for metric_col in METRIC_COLS:
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
            [variation_parameter, interaction_parameter, ALGORITHM_COL],
            as_index=False,
            observed=True,
        )
        .agg(**aggregation)
    )

    summary_df[ALGORITHM_COL] = _algorithm_categorical(
        summary_df[ALGORITHM_COL]
    )
    summary_df = (
        summary_df
        .sort_values(
            [variation_parameter, interaction_parameter, ALGORITHM_COL]
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


def _plot_results(
        results_dir: str,
        summary_df: pd.DataFrame,
        variation_parameter: str,
        interaction_parameter: str,
) -> None:
    """Plot the aggregated non-spectral interaction-comparison metrics."""

    algorithms = _ordered_algorithms(summary_df[ALGORITHM_COL])
    algorithm_markers = {
        algorithm: marker
        for algorithm, marker in zip(
            algorithms,
            cycle(["x", "^", "s", "*", "D", "o", "v", "P", ">", "<", "h", "+"]),
        )
    }
    algorithm_colors = _algorithm_colors(algorithms)

    interaction_values = sorted(
        summary_df[interaction_parameter].dropna().unique().tolist()
    )
    interaction_line_styles = {
        value: line_style
        for value, line_style in zip(
            interaction_values,
            cycle(INTERACTION_LINE_STYLES),
        )
    }

    fig = plt.figure(figsize=(7.2, 5.0))

    grid = fig.add_gridspec(
        2,
        6,
    )

    flattened_axes = np.asarray([
        fig.add_subplot(grid[0, 0:3]),
        fig.add_subplot(grid[0, 3:6]),
        fig.add_subplot(grid[1, 0:2]),
        fig.add_subplot(grid[1, 2:4]),
        fig.add_subplot(grid[1, 4:6]),
    ])

    metric_axes = [
        (flattened_axes[0], "Mean ONMI", "Mean ONMI", ONMI_COL),
        (flattened_axes[1], "Mean Omega", "Mean Omega", OMEGA_COL),
        (
            flattened_axes[2],
            f"Mean {KERR_COL}",
            "Mean Relative Error |K'-K|/K",
            KERR_COL,
        ),
        (
            flattened_axes[3],
            f"Mean {FUZZY_MODULARITY_COL}",
            "Mean Fuzzy-Modularity",
            FUZZY_MODULARITY_COL,
        ),
        (
            flattened_axes[4],
            f"Mean {CONDUCTANCE_BN_COL}",
            "Mean Conductance-BN",
            CONDUCTANCE_BN_COL,
        ),
    ]

    for algorithm in algorithms:
        algorithm_df = summary_df[summary_df[ALGORITHM_COL] == algorithm]
        marker = algorithm_markers[algorithm]
        color = algorithm_colors[algorithm]

        for interaction_value in interaction_values:
            curve_df = (
                algorithm_df[
                    algorithm_df[interaction_parameter] == interaction_value
                    ]
                .sort_values(variation_parameter)
            )

            if curve_df.empty:
                continue

            line_style = interaction_line_styles[interaction_value]

            for axis, metric_column, _, metric_col in metric_axes:
                if metric_column not in curve_df.columns:
                    continue

                sample_std_values = _numeric_error_values(
                    curve_df,
                    f"Sample Std {metric_col}",
                )
                reported_std_values = _numeric_error_values(
                    curve_df,
                    f"Mean Reported Std {metric_col}",
                )

                axis.plot(
                    curve_df[variation_parameter],
                    curve_df[metric_column],
                    marker=marker,
                    linestyle=line_style,
                    color=color,
                    linewidth=1.2,
                    markersize=4.5,
                    zorder=4,
                )

                if sample_std_values is not None:
                    axis.errorbar(
                        curve_df[variation_parameter],
                        curve_df[metric_column],
                        yerr=sample_std_values,
                        fmt="none",
                        ecolor=color,
                        elinewidth=1.0,
                        capsize=4,
                        alpha=0.45,
                        zorder=2,
                    )

                if reported_std_values is not None:
                    axis.errorbar(
                        curve_df[variation_parameter],
                        curve_df[metric_column],
                        yerr=reported_std_values,
                        fmt="none",
                        ecolor=color,
                        elinewidth=0.8,
                        capsize=2,
                        alpha=0.9,
                        zorder=3,
                    )

    x_label = VARIATION_PARAMETER_LABELS.get(
        variation_parameter,
        variation_parameter,
    )
    x_values = sorted(
        summary_df[variation_parameter].dropna().unique().tolist()
    )
    x_limits = _dynamic_x_limits(x_values)

    for axis, _, y_label, _ in metric_axes:
        axis.set_xlabel(x_label, fontsize=7)
        axis.set_ylabel(y_label, fontsize=7)
        axis.set_xlim(*x_limits)
        axis.set_xticks(x_values)
        axis.tick_params(axis="both", labelsize=6)
        axis.margins(x=0.03)
        axis.grid(True, alpha=0.3)

        _add_interaction_legends(
            axis=axis,
            algorithms=algorithms,
            algorithm_markers=algorithm_markers,
            algorithm_colors=algorithm_colors,
            interaction_parameter=interaction_parameter,
            interaction_values=interaction_values,
            interaction_line_styles=interaction_line_styles,
        )

    flattened_axes[0].set_ylim(0, 1.0)
    flattened_axes[1].set_ylim(0, 1.0)
    flattened_axes[2].set_ylim(bottom=0)
    flattened_axes[4].set_ylim(bottom=0)

    fig.tight_layout(
        pad=0.8,
        h_pad=1.0,
        w_pad=1.0,
    )

    output_prefix = _interaction_output_prefix(
        variation_parameter=variation_parameter,
        interaction_parameter=interaction_parameter,
    )

    fig.savefig(
        os.path.join(
            results_dir,
            f"{output_prefix}_non_spectral_algorithms.pdf",
        ),
        dpi=300,
        bbox_inches="tight",
    )

    fig.savefig(
        os.path.join(
            results_dir,
            f"{output_prefix}_non_spectral_algorithms.png",
        ),
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def _add_interaction_legends(
        axis,
        algorithms: list[str],
        algorithm_markers: dict[str, str],
        algorithm_colors: dict[str, str],
        interaction_parameter: str,
        interaction_values: list,
        interaction_line_styles: dict,
) -> None:
    """Add separate algorithm and interaction-level legends inside one subplot."""

    algorithm_handles = [
        Line2D(
            [0],
            [0],
            color=algorithm_colors[algorithm],
            marker=algorithm_markers[algorithm],
            linestyle="None",
            markersize=4.5,
            label=algorithm,
        )
        for algorithm in algorithms
    ]

    interaction_handles = [
        Line2D(
            [0],
            [0],
            color="black",
            linestyle=interaction_line_styles[value],
            linewidth=1.2,
            label=_format_parameter_value(value),
        )
        for value in interaction_values
    ]

    algorithm_legend = axis.legend(
        handles=algorithm_handles,
        title="Algorithm",
        loc="upper right",
        fontsize=5.2,
        title_fontsize=6,
        framealpha=0.3,
        ncol=1,
        columnspacing=0.6,
        handletextpad=0.3,
    )
    axis.add_artist(algorithm_legend)

    axis.legend(
        handles=interaction_handles,
        title=VARIATION_PARAMETER_LABELS.get(
            interaction_parameter,
            interaction_parameter,
        ),
        loc="upper right",
        bbox_to_anchor=(1.0, 0.70),
        fontsize=5.5,
        title_fontsize=6,
        framealpha=0.3,
        ncol=1,
        columnspacing=0.6,
        handletextpad=0.3,
    )


def _algorithm_colors(algorithms: list[str]) -> dict[str, str]:
    """Map algorithms to colours from Matplotlib's active default colour cycle."""

    colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", [])
    if not colors:
        colors = [f"C{index}" for index in range(max(1, len(algorithms)))]

    return {
        algorithm: colors[index % len(colors)]
        for index, algorithm in enumerate(algorithms)
    }


def _numeric_error_values(
        dataframe: pd.DataFrame,
        column: str,
) -> np.ndarray | None:
    """Return a numeric error array, or None when the column has no values."""

    if column not in dataframe.columns:
        return None

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    ).to_numpy(dtype=float)

    if np.isnan(values).all():
        return None

    return np.nan_to_num(values, nan=0.0)


def _dynamic_x_limits(values: list[float]) -> tuple[float, float]:
    """Return compact x-axis limits around the observed interaction-set values."""

    numeric_values = np.asarray(values, dtype=float)
    minimum = float(np.min(numeric_values))
    maximum = float(np.max(numeric_values))

    if np.isclose(minimum, maximum):
        padding = max(abs(minimum) * 0.05, 0.05)
    else:
        padding = max((maximum - minimum) * 0.08, 0.02)

    return minimum - padding, maximum + padding


def _interaction_output_prefix(
        variation_parameter: str,
        interaction_parameter: str,
) -> str:
    """Build the output prefix for a two-parameter interaction experiment."""

    return f"{variation_parameter}_x_{interaction_parameter}"


def _format_parameter_value(value) -> str:
    """Format one numeric interaction level compactly for the legend."""

    numeric_value = float(value)

    if numeric_value.is_integer():
        return str(int(numeric_value))

    return f"{numeric_value:g}"


def _iter_sorted_dirs(directory: str) -> list[Path]:
    """Return the immediate subdirectories sorted by name."""

    return sorted(
        [
            path
            for path in Path(directory).iterdir()
            if path.is_dir()
        ],
        key=lambda path: path.name,
    )


def _parse_network_name(network_name: str) -> dict[str, float] | None:
    """Parse an LFR network name into its variation properties."""

    match = NETWORK_RE.fullmatch(network_name)
    if match is None:
        return None

    properties = match.groupdict()
    return {
        NETWORK_PROPERTY_N: int(properties[NETWORK_PROPERTY_N]),
        NETWORK_PROPERTY_MU: float(properties[NETWORK_PROPERTY_MU]),
        NETWORK_PROPERTY_ON: int(properties[NETWORK_PROPERTY_ON]),
        NETWORK_PROPERTY_OM: int(properties[NETWORK_PROPERTY_OM]),
        NETWORK_PROPERTY_INST: int(properties[NETWORK_PROPERTY_INST]),
    }


def _read_csv(csv_path: str) -> pd.DataFrame:
    """Read a result CSV file and normalize its column names."""

    dataframe = pd.read_csv(csv_path, sep=",", engine="python")
    dataframe.columns = [
        column.strip()
        for column in dataframe.columns
    ]
    return dataframe


def _find_runtime_column(dataframe: pd.DataFrame) -> str | None:
    """Return the first supported runtime column found in the dataframe."""

    for runtime_column in RUNTIME_INPUT_COLS:
        if runtime_column in dataframe.columns:
            return runtime_column

    return None


def _parse_mean_and_std(value) -> tuple[float, float]:
    """Parse either a scalar value or a 'mean ± sample standard deviation' value."""

    if pd.isna(value):
        return float("nan"), float("nan")

    text = str(value).strip()

    if text in {"", "-", "None", "none"}:
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
    ordered.extend(
        sorted(observed - set(ordered))
    )

    return ordered


def _validate_interaction_parameters(
        variation_parameter: str,
        interaction_parameter: str,
) -> None:
    """Validate the two parameters used in the interaction plot."""

    for parameter_name, parameter in (
            ("variation_parameter", variation_parameter),
            ("interaction_parameter", interaction_parameter),
    ):
        if parameter not in SUPPORTED_VARIATION_PARAMETERS:
            raise ValueError(
                f"[ERROR] Unsupported {parameter_name}: '{parameter}'."
            )

    if variation_parameter == interaction_parameter:
        raise ValueError(
            "[ERROR] variation_parameter and interaction_parameter must differ."
        )


if __name__ == "__main__":
    # 14_nM_uM_onnL_omM: mu x om
    plot_non_spectral_comparison_interaction_variation_set_results(
        results_dir=os.path.join(
            INTERACTION_RESULTS_BASE_DIR,
            "non-spectral",
            "results_2026-09-21_23-00-32-755248",
            "14_nM_uM_onnL_omM",
        ),
        variation_parameter=NETWORK_PROPERTY_MU,
        interaction_parameter=NETWORK_PROPERTY_OM,
    )

    # 15_nM_uM_onnM_omL: mu x on
    plot_non_spectral_comparison_interaction_variation_set_results(
        results_dir=os.path.join(
            INTERACTION_RESULTS_BASE_DIR,
            "non-spectral",
            "results_2026-09-21_23-00-32-755248",
            "15_nM_uM_onnM_omL",
        ),
        variation_parameter=NETWORK_PROPERTY_MU,
        interaction_parameter=NETWORK_PROPERTY_ON,
    )

    # 16_nM_uM_onnM_omM: om x on
    plot_non_spectral_comparison_interaction_variation_set_results(
        results_dir=os.path.join(
            INTERACTION_RESULTS_BASE_DIR,
            "non-spectral",
            "results_2026-09-21_23-00-32-755248",
            "16_nM_uM_onnM_omM",
        ),
        variation_parameter=NETWORK_PROPERTY_OM,
        interaction_parameter=NETWORK_PROPERTY_ON,
    )
