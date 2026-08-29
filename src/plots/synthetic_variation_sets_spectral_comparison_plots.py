import json
import os.path
import re
from itertools import cycle
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
    'synthetic',
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
ONMI_COL = "ONMI"
OMEGA_COL = "Omega"
CONDUCTANCE_BN_COL = "Conductance-BN"
FUZZY_MODULARITY_COL = "Fuzzy-Modularity"

# The current comparison results file uses "FADDIS Runtime" for both
# algorithms. "Runtime" is also accepted to support a corrected label.
RUNTIME_INPUT_COLS = ("Runtime", "FADDIS Runtime")
RUNTIME_COL = "Runtime"

METRIC_COLS = (
    ONMI_COL,
    OMEGA_COL,
    CONDUCTANCE_BN_COL,
    FUZZY_MODULARITY_COL,
    RUNTIME_COL,
)

# Metrics shown in the figures. Runtime is retained in the generated CSV files
# but intentionally omitted from the plots.
PLOT_METRIC_COLS = (
    ONMI_COL,
    OMEGA_COL,
    FUZZY_MODULARITY_COL,
    CONDUCTANCE_BN_COL,
)

# Algorithm order used in summaries and plots.
ALGORITHM_ORDER = ("FADDIS", "NJW+FCM")

# Plot limits for each variation parameter.
VARIATION_PARAMETER_LIMITS = {
    NETWORK_PROPERTY_N: (500 - 20, 1000 + 20),
    # NETWORK_PROPERTY_N: (1000 - 200, 10000 + 200),
    NETWORK_PROPERTY_MU: (0.1 - 0.02, 0.8 + 0.02),
    NETWORK_PROPERTY_ON: (100 - 20, 600 + 20),
    NETWORK_PROPERTY_OM: (1 - 0.2, 8 + 0.2),
}

VARIATION_PARAMETER_LABELS = {
    NETWORK_PROPERTY_N: r"$n$",
    NETWORK_PROPERTY_MU: r"$\mu$",
    NETWORK_PROPERTY_ON: r"$o_n$",
    NETWORK_PROPERTY_OM: r"$o_m$",
}

# Example network name: n1000mu0.1on200om2inst1
NETWORK_RE = re.compile(
    r"n(?P<n>\d+)"
    r"mu(?P<mu>\d*\.?\d+)"
    r"on(?P<on>\d+)"
    r"om(?P<om>\d+)"
    r"inst(?P<inst>\d+)"
)


def plot_spectral_comparison_variation_set_results(
        results_dir: str,
        variation_parameter: str,
        input_filename: str = "_comparison_results.csv",
) -> None:
    """
    Process spectral-comparison results for a variation set and generate summary plots.

    FADDIS scalar metric values and the mean component of NJW+FCM
    "mean ± sample standard deviation" values are aggregated across network
    instances for each value of the variation parameter. Sample standard
    deviations across network instances and reported within-instance standard
    deviations across stochastic executions, when available, are both shown
    as error bars in the figures.

    Parameters:
        results_dir : (str)
            Directory containing the experiment results, organized in
            subdirectories for each network instance.
        variation_parameter : (str)
            Network property varied in the experiment.
        input_filename : (str, optional)
            Name of the comparison CSV file in each network directory.
            Default is "_comparison_results.csv".

    Saves:
        - A CSV file containing the parsed per-network algorithm results:
          "{variation_parameter}_spectral_comparison_results.csv".
        - A CSV file containing the aggregated results by variation parameter
          and algorithm:
          "{variation_parameter}_spectral_comparison_summary.csv".
        - A PDF containing plots of mean ONMI, mean Omega,
          mean Fuzzy-Modularity, and mean Conductance-BN:
          "{variation_parameter}_spectral_algorithms.pdf".
    """

    _validate_variation_parameter(variation_parameter)

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
            CONDUCTANCE_BN_COL,
            FUZZY_MODULARITY_COL,
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
                    CONDUCTANCE_BN_COL,
                    FUZZY_MODULARITY_COL,
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
                ALGORITHM_COL,
                NETWORK_PROPERTY_INST,
                NETWORK_COL,
            ]
        )
        .reset_index(drop=True)
    )
    raw_df[ALGORITHM_COL] = raw_df[ALGORITHM_COL].astype(str)

    summary_df = _compute_summary(raw_df, variation_parameter)

    raw_df.to_csv(
        os.path.join(
            results_dir,
            f"{variation_parameter}_spectral_comparison_results.csv",
        ),
        index=False,
    )

    summary_df.to_csv(
        os.path.join(
            results_dir,
            f"{variation_parameter}_spectral_comparison_summary.csv",
        ),
        index=False,
    )

    _plot_results(
        results_dir=results_dir,
        summary_df=summary_df,
        variation_parameter=variation_parameter,
    )


def _compute_summary(
        raw_df: pd.DataFrame,
        variation_parameter: str,
) -> pd.DataFrame:
    """
    Aggregate the per-network metric means by variation parameter and algorithm.

    For NJW+FCM, each source CSV cell can already represent a mean and sample
    standard deviation across seeds. Only the source mean is used in the
    algorithm curve. The sample standard deviation across network instances
    and the reported within-network standard deviation across stochastic
    executions are retained separately and both used as figure error bars when
    available.
    """

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
            [variation_parameter, ALGORITHM_COL],
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
        .sort_values([variation_parameter, ALGORITHM_COL])
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
) -> None:
    """Plot the four aggregated spectral-comparison metrics."""

    algorithms = _ordered_algorithms(summary_df[ALGORITHM_COL])
    algorithm_markers = {
        algorithm: marker
        for algorithm, marker in zip(
            algorithms,
            cycle(["x", "^", "s", "*", "D", "o", "v", "P", ">", "<", "h", "+"]),
        )
    }

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(7.2, 5.4),
        squeeze=False,
    )

    metric_axes = [
        (axes[0, 0], "Mean ONMI", "Mean ONMI", ONMI_COL),
        (axes[0, 1], "Mean Omega", "Mean Omega", OMEGA_COL),
        (
            axes[1, 0],
            f"Mean {FUZZY_MODULARITY_COL}",
            "Mean Fuzzy-Modularity",
            FUZZY_MODULARITY_COL,
        ),
        (
            axes[1, 1],
            f"Mean {CONDUCTANCE_BN_COL}",
            "Mean Conductance-BN",
            CONDUCTANCE_BN_COL,
        ),
    ]

    for algorithm in algorithms:
        algorithm_df = (
            summary_df[summary_df[ALGORITHM_COL] == algorithm]
            .sort_values(variation_parameter)
        )
        marker = algorithm_markers[algorithm]

        for axis, metric_column, _, metric_col in metric_axes:
            if metric_column not in algorithm_df.columns:
                continue

            sample_std_col = f"Sample Std {metric_col}"
            reported_std_col = f"Mean Reported Std {metric_col}"

            sample_std_values = None
            reported_std_values = None

            if sample_std_col in algorithm_df.columns:
                sample_std_values = pd.to_numeric(
                    algorithm_df[sample_std_col],
                    errors="coerce",
                ).to_numpy(dtype=float)

                if np.isnan(sample_std_values).all():
                    sample_std_values = None
                else:
                    sample_std_values = np.nan_to_num(
                        sample_std_values,
                        nan=0.0,
                    )

            if reported_std_col in algorithm_df.columns:
                reported_std_values = pd.to_numeric(
                    algorithm_df[reported_std_col],
                    errors="coerce",
                ).to_numpy(dtype=float)

                if np.isnan(reported_std_values).all():
                    reported_std_values = None
                else:
                    reported_std_values = np.nan_to_num(
                        reported_std_values,
                        nan=0.0,
                    )

            line, = axis.plot(
                algorithm_df[variation_parameter],
                algorithm_df[metric_column],
                marker=marker,
                linewidth=1.2,
                markersize=4.5,
                label=algorithm,
            )
            line_color = line.get_color()

            if sample_std_values is not None:
                axis.errorbar(
                    algorithm_df[variation_parameter],
                    algorithm_df[metric_column],
                    yerr=sample_std_values,
                    fmt="none",
                    ecolor=line_color,
                    elinewidth=1.0,
                    capsize=4,
                    alpha=0.45,
                    zorder=2,
                )

            if reported_std_values is not None:
                axis.errorbar(
                    algorithm_df[variation_parameter],
                    algorithm_df[metric_column],
                    yerr=reported_std_values,
                    fmt="none",
                    ecolor=line_color,
                    elinewidth=0.8,
                    capsize=2,
                    alpha=0.9,
                    zorder=3,
                )

    x_limits = VARIATION_PARAMETER_LIMITS[variation_parameter]
    x_label = VARIATION_PARAMETER_LABELS.get(
        variation_parameter,
        variation_parameter,
    )

    for axis, _, y_label, _ in metric_axes:
        axis.set_xlabel(x_label, fontsize=7)
        axis.set_ylabel(y_label, fontsize=7)
        axis.set_xlim(x_limits[0], x_limits[1])
        axis.tick_params(axis="both", labelsize=6)
        axis.margins(x=0.03)
        axis.grid(True, alpha=0.3)

        handles, labels = axis.get_legend_handles_labels()
        if handles:
            axis.legend(
                loc="upper right",
                fontsize=5.5,
                framealpha=0.3,
                ncol=1,
                columnspacing=0.6,
                handletextpad=0.3,
            )

    axes[0, 0].set_ylim(0, 1.0)
    axes[0, 1].set_ylim(0, 1.0)
    axes[1, 1].set_ylim(bottom=0)

    fig.tight_layout(
        pad=0.8,
        h_pad=1.0,
        w_pad=1.0,
    )
    fig.savefig(
        os.path.join(
            results_dir,
            f"{variation_parameter}_spectral_algorithms.pdf",
        ),
        dpi=300,
        bbox_inches="tight",
    )

    fig.savefig(
        os.path.join(
            results_dir,
            f"{variation_parameter}_spectral_algorithms.png",
        ),
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


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


def _parse_network_name(network_name: str) -> dict[str, int | float] | None:
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
    """Read a result CSV and normalize its column names."""

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
    """
    Parse either a scalar value or a "mean ± sample standard deviation" value.

    Returns:
        mean : (float)
            Parsed scalar or mean component.
        sample_std : (float)
            Parsed sample-standard-deviation component, or NaN when the input
            contains only one scalar value.
    """

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
    """Create a categorical algorithm column with a deterministic order."""

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


def _validate_variation_parameter(variation_parameter: str) -> None:
    """Validate that the requested variation parameter is supported."""

    if variation_parameter not in VARIATION_PARAMETER_LIMITS:
        raise ValueError(
            "[ERROR] Unsupported variation parameter: "
            f"'{variation_parameter}'."
        )


if __name__ == "__main__":
    # Boundary variation set.
    for folders in [
        ("spectral-baseline", "results_2026-07-28_01-15-27-987757"),
        ("spectral-baseline", "results_2026-08-23_22-59-23-685832")
    ]:
        plot_spectral_comparison_variation_set_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR,
                "boundary_variation_set",
                folders[0],
                folders[1],
            ),
            variation_parameter=NETWORK_PROPERTY_MU,
        )

    # Membership variation set.
    for folders in [
        ("spectral-baseline", "results_2026-07-28_03-11-14-484538"),
        ("spectral-baseline", "results_2026-08-24_01-42-24-752338")
    ]:
        plot_spectral_comparison_variation_set_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR,
                "membership_variation_set",
                folders[0],
                folders[1],
            ),
            variation_parameter=NETWORK_PROPERTY_OM,
        )

    # Overlap variation set.
    for folders in [
        ("spectral-baseline", "results_2026-07-28_05-06-56-584925"),
        ("spectral-baseline", "results_2026-08-24_08-08-27-013832")
    ]:
        plot_spectral_comparison_variation_set_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR,
                "overlap_variation_set",
                folders[0],
                folders[1],
            ),
            variation_parameter=NETWORK_PROPERTY_ON,
        )
