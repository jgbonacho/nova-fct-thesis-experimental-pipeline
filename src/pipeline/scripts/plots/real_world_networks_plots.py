import math
import os
from itertools import cycle
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

# Base directory for real-world results.
RESULTS_BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'results', 'real-world')

# Result CSV column names.
ID_COL = "ID"
NETWORK_FAMILY_COL = "Network Family"
NETWORK_COL = "Network"
OVERLAPPING_COL = "Overlapping?"
AFFINITY_DESIGN_COL = "Affinity Design"
EXECUTION_MODE_COL = "Execution Mode"
LAPLACIAN_COL = "Laplacian"
GAMMA_COL = "Gamma"
KERR_COL = "|K'-K|/K"

AMI_COL = "AMI"
F_MEASURE_COL = "F-measure"
ARI_COL = "ARI"
FMI_COL = "FMI"
NMI_COL = "NMI"
VI_COL = "VI"
ONMI_COL = "ONMI"
OMEGA_COL = "Omega"

FADDIS_RUNTIME_COL = "FADDIS Runtime"

# Variant name column.
VARIANT_COL = "variant"


def plot_real_world_results_by_network(
        results_dir: str,
        input_filename: str = "_results.csv",
        plot_by_family: bool = True
):
    """
    Process real-world network results and generate plots.

    The x-axis is the real-world network name.
    Since real-world networks do not have instances, no mean or standard deviation is computed.
    The plotted values are the direct results from each network and variant.

    Parameters:
        results_dir : (str)
            Directory containing the experiment results.
            It can contain network folders directly or family/network folders.
        input_filename : (str, optional)
            The name of the CSV file containing the results for each network.
            Default is "_results.csv".
        plot_by_family : (bool, optional)
            Whether to also save plots inside each network family folder.
            Default is True.

    Saves:
        At the root of results_dir:
            - network_results_summary.csv
            - non_overlapping_networks.pdf or overlapping_networks.pdf

        Inside each network family folder, if plot_by_family=True:
            - network_family_results_summary.csv
            - non_overlapping_networks.pdf
            - overlapping_networks.pdf
    """

    rows = []

    for network_dir in _iter_network_result_dirs(results_dir, input_filename):
        results_csv_path = os.path.join(network_dir, input_filename)
        results_df = _read_csv(results_csv_path)

        # Convert available metric columns to numeric.
        numeric_cols = [
            GAMMA_COL,
            KERR_COL,
            AMI_COL,
            F_MEASURE_COL,
            ARI_COL,
            FMI_COL,
            NMI_COL,
            VI_COL,
            ONMI_COL,
            OMEGA_COL,
            FADDIS_RUNTIME_COL,
        ]

        for col in numeric_cols:
            if col in results_df.columns:
                results_df[col] = pd.to_numeric(results_df[col], errors="coerce")

        results_df[VARIANT_COL] = results_df.apply(lambda r: _build_variant_name(r.to_dict()), axis=1)

        for _, res in results_df.iterrows():
            network_name = str(res[NETWORK_COL]).strip() if NETWORK_COL in results_df.columns else network_dir.name

            network_family = (
                str(res[NETWORK_FAMILY_COL]).strip()
                if NETWORK_FAMILY_COL in results_df.columns
                else network_dir.parent.name
            )

            overlapping = _to_bool(res[OVERLAPPING_COL]) if OVERLAPPING_COL in results_df.columns else False

            row = {
                VARIANT_COL: res[VARIANT_COL],
                NETWORK_FAMILY_COL: network_family,
                NETWORK_COL: network_name,
                OVERLAPPING_COL: overlapping,
                KERR_COL: _get_numeric_value(res, KERR_COL),
                AMI_COL: _get_numeric_value(res, AMI_COL),
                F_MEASURE_COL: _get_numeric_value(res, F_MEASURE_COL),
                ARI_COL: _get_numeric_value(res, ARI_COL),
                FMI_COL: _get_numeric_value(res, FMI_COL),
                NMI_COL: _get_numeric_value(res, NMI_COL),
                VI_COL: _get_numeric_value(res, VI_COL),
                ONMI_COL: _get_numeric_value(res, ONMI_COL),
                OMEGA_COL: _get_numeric_value(res, OMEGA_COL),
            }

            if FADDIS_RUNTIME_COL in results_df.columns:
                row[FADDIS_RUNTIME_COL] = _get_numeric_value(res, FADDIS_RUNTIME_COL)

            rows.append(row)

    summary_df = pd.DataFrame(rows)

    if summary_df.empty:
        raise ValueError("[ERROR] No valid real-world network result directories were found.")

    summary_df = (
        summary_df
        .sort_values([
            NETWORK_FAMILY_COL,
            NETWORK_COL,
            VARIANT_COL,
        ])
        .reset_index(drop=True)
    )

    for col in [
        KERR_COL,
        AMI_COL,
        F_MEASURE_COL,
        ARI_COL,
        FMI_COL,
        NMI_COL,
        VI_COL,
        ONMI_COL,
        OMEGA_COL,
        FADDIS_RUNTIME_COL,
    ]:
        if col in summary_df.columns:
            summary_df[col] = summary_df[col].round(6)

    # Global summary CSV file.
    summary_df.to_csv(
        os.path.join(results_dir, "network_family_results_summary.csv"),
        index=False
    )

    # Global plots with all real-world networks.
    _plot_real_world_results_by_network(results_dir, summary_df)

    # Family-level summary CSV files and plots.
    if plot_by_family:
        for network_family, family_df in summary_df.groupby(NETWORK_FAMILY_COL):
            family_results_dir = os.path.join(results_dir, network_family)
            os.makedirs(family_results_dir, exist_ok=True)

            family_df = (
                family_df
                .sort_values([
                    NETWORK_COL,
                    VARIANT_COL,
                ])
                .reset_index(drop=True)
            )

            family_df.to_csv(
                os.path.join(family_results_dir, "network_family_results_summary.csv"),
                index=False
            )

            _plot_real_world_results_by_network(family_results_dir, family_df)


def _iter_network_result_dirs(results_dir: str, input_filename: str) -> list[Path]:
    """
    Find all network result directories containing the input results CSV.

    This works both when:
        - results_dir directly contains network folders;
        - results_dir contains family/network folders.

    Parameters:
        results_dir : (str)
            Directory containing the experiment results.
        input_filename : (str)
            Results CSV filename.

    Returns:
        network_result_dirs : (list[Path])
            List of network result directories.
    """

    results_path = Path(results_dir)

    if not results_path.exists():
        raise FileNotFoundError(f"[ERROR] Results directory does not exist: {results_dir}")

    network_result_dirs = sorted(
        [path.parent for path in results_path.rglob(input_filename)],
        key=lambda path: path.name,
    )

    if not network_result_dirs:
        print(f"[DEBUG] No '{input_filename}' files found inside: {results_dir}")

    return network_result_dirs


def _read_csv(csv_path: str) -> pd.DataFrame:
    """
    Read a CSV file.

    Parameters:
        csv_path : (str)
            The path to the CSV file.

    Returns:
        df : (pd.DataFrame)
            A DataFrame containing the CSV data.
    """

    df = pd.read_csv(csv_path, sep=",", engine="python")
    df.columns = [c.strip() for c in df.columns]
    return df


def _build_variant_name(row: dict[str, str]) -> str:
    """
    Build a variant name from the row dictionary.

    Parameters:
        row : (dict[str, str])
            A dictionary representing a row from the CSV file.

    Returns:
        variant_name : (str)
            The variant name.
    """

    variant_id = _format_variant_id(row.get(ID_COL, ""))
    affinity_design = str(row.get(AFFINITY_DESIGN_COL, "")).strip().lower()
    execution_mode = str(row.get(EXECUTION_MODE_COL, "")).strip().lower()
    laplacian = str(row.get(LAPLACIAN_COL, "")).strip().lower()

    gamma_value = row.get(GAMMA_COL, "")
    gamma_value = "" if pd.isna(gamma_value) else str(gamma_value).strip().lower()

    if gamma_value == "":
        gamma = "-"
    else:
        gamma = f"g{gamma_value}"

    return f"{variant_id}_{affinity_design}_{execution_mode}_{laplacian}_{gamma}"


def _format_variant_id(value) -> str:
    """
    Format the result ID as a three-digit string.

    Parameters:
        value : (object)
            ID value.

    Returns:
        variant_id : (str)
            Formatted ID.
    """

    if pd.isna(value):
        return "000"

    try:
        return f"{int(value):03d}"
    except ValueError:
        return str(value).strip().zfill(3)


def _to_bool(value) -> bool:
    """
    Convert a CSV value to bool.

    Parameters:
        value : (object)
            Value to convert.

    Returns:
        converted_value : (bool)
            Converted boolean value.
    """

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"true", "1", "yes"}


def _get_numeric_value(row, col: str):
    """
    Get a numeric value from a row.

    Parameters:
        row : (pd.Series)
            Row from the results DataFrame.
        col : (str)
            Column name.

    Returns:
        value : (float)
            Numeric value or NaN.
    """

    if col not in row:
        return float("nan")

    return pd.to_numeric(row[col], errors="coerce")


def _plot_real_world_results_by_network(results_dir: str, df: pd.DataFrame):
    """
    Generate separate plots for non-overlapping and overlapping real-world networks.

    For non-overlapping networks, plots AMI, F-measure, ARI, FMI, NMI and VI.
    For overlapping networks, plots ONMI and Omega.
    For both cases, also plots relative error of K and FADDIS runtime when available.

    Parameters:
        results_dir : (str)
            Directory where the plots will be saved.
        df : (pd.DataFrame)
            DataFrame containing direct results.

    Saves:
        PDF plots in the results directory.
    """

    non_overlapping_df = df[df[OVERLAPPING_COL] == False].copy()
    overlapping_df = df[df[OVERLAPPING_COL] == True].copy()

    non_overlapping_metrics = [
        (AMI_COL, "AMI", (0, 1)),
        (F_MEASURE_COL, "F-measure", (0, 1)),
        (ARI_COL, "ARI", (-1, 1)),
        (FMI_COL, "FMI", (0, 1)),
        (NMI_COL, "NMI", (0, 1)),
        (VI_COL, "VI", (0, None)),
        (KERR_COL, "Relative Error |K'-K|/K", (0, None)),
    ]

    overlapping_metrics = [
        (ONMI_COL, "ONMI", (0, 1)),
        (OMEGA_COL, "Omega", (0, 1)),
        (KERR_COL, "Relative Error |K'-K|/K", (0, None)),
    ]

    if FADDIS_RUNTIME_COL in df.columns:
        non_overlapping_metrics.append(
            (FADDIS_RUNTIME_COL, "FADDIS Runtime (in seconds)", (0, None))
        )
        overlapping_metrics.append(
            (FADDIS_RUNTIME_COL, "FADDIS Runtime (in seconds)", (0, None))
        )

    if not non_overlapping_df.empty:
        _plot_metric_grid(
            results_dir=results_dir,
            df=non_overlapping_df,
            metric_plots=non_overlapping_metrics,
            output_prefix="non_overlapping_networks"
        )

    if not overlapping_df.empty:
        _plot_metric_grid(
            results_dir=results_dir,
            df=overlapping_df,
            metric_plots=overlapping_metrics,
            output_prefix="overlapping_networks"
        )


def _plot_metric_grid(
        results_dir: str,
        df: pd.DataFrame,
        metric_plots: list[tuple[str, str, tuple]],
        output_prefix: str
) -> None:
    """
    Generate metric plots using the real-world network name as the x-axis.

    Parameters:
        results_dir : (str)
            Directory where the plots will be saved.
        df : (pd.DataFrame)
            DataFrame containing direct results.
        metric_plots : (list[tuple[str, str, tuple]])
            List of metrics to plot, as (column, label, y_limits).
        output_prefix : (str)
            Prefix used for the output plot filenames.

    Saves:
        PDF plots in the results directory.
    """

    plot_df = df.copy()

    if plot_df.empty:
        return

    networks = list(plot_df[NETWORK_COL].drop_duplicates())
    x_positions = {network: i for i, network in enumerate(networks)}
    variants = list(plot_df[VARIANT_COL].drop_duplicates())

    n_cols = 2
    n_rows = math.ceil(len(metric_plots) / n_cols)

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(15.5, 6.0 * n_rows),
        squeeze=False
    )

    axes_flat = axes.ravel()

    marker_cycle = cycle(["x", "^", "s", "*", "D", "o", "v", "P", ">", "<", "h", "+"])
    variant_markers = {variant: next(marker_cycle) for variant in variants}
    variant_colors = {variant: plt.cm.tab20(i % 20) for i, variant in enumerate(variants)}

    for metric_idx, (metric_col, metric_label, y_limits) in enumerate(metric_plots):
        ax = axes_flat[metric_idx]

        for variant in variants:
            d = plot_df[plot_df[VARIANT_COL] == variant].copy()

            if metric_col not in d.columns:
                continue

            if d[metric_col].isna().all():
                continue

            d["_x"] = d[NETWORK_COL].map(x_positions)
            d = d.sort_values("_x")

            ax.plot(
                d["_x"],
                d[metric_col],
                marker=variant_markers[variant],
                color=variant_colors[variant],
                linewidth=1.8,
                markersize=7,
                label=variant,
            )

        ax.set_xlabel("Network")
        ax.set_ylabel(metric_label)
        ax.set_xticks(range(len(networks)))
        ax.set_xticklabels(networks, rotation=45, ha="right")
        ax.grid(True, alpha=0.3)

        if y_limits is not None:
            ymin, ymax = y_limits
            ax.set_ylim(bottom=ymin)
            if ymax is not None:
                ax.set_ylim(top=ymax)

        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc="best", fontsize=8)

    for empty_idx in range(len(metric_plots), len(axes_flat)):
        axes_flat[empty_idx].axis("off")

    fig.tight_layout(pad=2.0, h_pad=3.5, w_pad=1.5)

    fig.savefig(
        os.path.join(results_dir, f"{output_prefix}.pdf"),
        dpi=300,
        bbox_inches="tight",
    )

    fig.savefig(
        os.path.join(results_dir, f"{output_prefix}.png"),
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


if __name__ == "__main__":
    results_dirs = [
        os.path.join(RESULTS_BASE_DIR, "baseline", "results_2026-05-13_23-39-13-447632"),

        os.path.join(RESULTS_BASE_DIR, "experience1", "results_2026-05-13_23-52-22-951933"),
        os.path.join(RESULTS_BASE_DIR, "experience1", "results_2026-05-13_23-59-16-802069"),
        os.path.join(RESULTS_BASE_DIR, "experience1", "results_2026-05-14_00-10-12-245299"),
        os.path.join(RESULTS_BASE_DIR, "experience1", "results_2026-05-14_00-18-47-225354"),

        os.path.join(RESULTS_BASE_DIR, "experience2", "results_2026-05-14_10-39-26-010867"),
        os.path.join(RESULTS_BASE_DIR, "experience2", "results_2026-05-14_10-45-38-104210"),
        os.path.join(RESULTS_BASE_DIR, "experience2", "results_2026-05-14_10-56-02-985059"),
        os.path.join(RESULTS_BASE_DIR, "experience2", "results_2026-05-14_11-04-15-844508"),

        os.path.join(RESULTS_BASE_DIR, "experience3", "results_2026-05-14_11-18-43-724134"),
        os.path.join(RESULTS_BASE_DIR, "experience3", "results_2026-05-14_11-23-46-815439"),
        os.path.join(RESULTS_BASE_DIR, "experience3", "results_2026-05-14_11-33-29-613869"),
        os.path.join(RESULTS_BASE_DIR, "experience3", "results_2026-05-14_11-39-51-255386"),

        os.path.join(RESULTS_BASE_DIR, "experience4", "results_2026-05-14_11-52-11-686062"),
        os.path.join(RESULTS_BASE_DIR, "experience4", "results_2026-05-14_11-58-40-374031"),
        os.path.join(RESULTS_BASE_DIR, "experience4", "results_2026-05-14_12-08-32-563204"),
        os.path.join(RESULTS_BASE_DIR, "experience4", "results_2026-05-14_12-18-20-912820"),

        os.path.join(RESULTS_BASE_DIR, "experience5", "results_2026-05-14_12-32-25-330204"),
        os.path.join(RESULTS_BASE_DIR, "experience5", "results_2026-05-14_12-41-51-363988"),
        os.path.join(RESULTS_BASE_DIR, "experience5", "results_2026-05-14_12-52-28-621268"),
        os.path.join(RESULTS_BASE_DIR, "experience5", "results_2026-05-14_13-02-32-182253"),

        os.path.join(RESULTS_BASE_DIR, "experience6", "results_2026-05-14_13-17-59-894947"),
        os.path.join(RESULTS_BASE_DIR, "experience6", "results_2026-05-14_13-27-26-954044"),
        os.path.join(RESULTS_BASE_DIR, "experience6", "results_2026-05-14_14-42-09-654746"),
        os.path.join(RESULTS_BASE_DIR, "experience6", "results_2026-05-14_14-50-59-277172"),

        os.path.join(RESULTS_BASE_DIR, "experience7", "results_2026-05-18_08-57-04-357791"),
        os.path.join(RESULTS_BASE_DIR, "experience7", "results_2026-05-18_09-05-00-419889"),
        os.path.join(RESULTS_BASE_DIR, "experience7", "results_2026-05-18_09-14-56-020795"),
        os.path.join(RESULTS_BASE_DIR, "experience7", "results_2026-05-18_09-20-51-445538"),
        os.path.join(RESULTS_BASE_DIR, "experience7", "results_2026-05-18_09-34-47-258253"),
        os.path.join(RESULTS_BASE_DIR, "experience7", "results_2026-05-18_09-42-04-813215"),

        os.path.join(RESULTS_BASE_DIR, "experience8", "results_2026-05-18_16-06-16-595831"),
        os.path.join(RESULTS_BASE_DIR, "experience8", "results_2026-05-18_16-18-42-834794"),
        os.path.join(RESULTS_BASE_DIR, "experience8", "results_2026-05-18_18-22-28-308135"),
        os.path.join(RESULTS_BASE_DIR, "experience8", "results_2026-05-18_18-35-06-093050"),
        os.path.join(RESULTS_BASE_DIR, "experience8", "results_2026-05-18_18-48-07-522086"),
        os.path.join(RESULTS_BASE_DIR, "experience8", "results_2026-05-18_18-59-49-412756"),
    ]

    for results_dir in results_dirs:
        plot_real_world_results_by_network(
            results_dir=results_dir,
            plot_by_family=True
        )
