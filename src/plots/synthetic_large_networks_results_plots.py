import json
import os.path
import re
from itertools import cycle
from pathlib import Path

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
NETWORK_PROPERTY_K = "K"
NETWORK_PROPERTY_F = "f"
NETWORK_PROPERTY_OM = "om"
NETWORK_PROPERTY_INST = "inst"

# Result CSV column names.
ID_COL = "ID"
NETWORK_COL = "Network"
AFFINITY_DESIGN_COL = "Affinity Design"
EXECUTION_MODE_COL = "Execution Mode"
LAPLACIAN_COL = "Laplacian"
GAMMA_COL = "Gamma"
KERR_COL = "|K'-K|/K"
ONMI_COL = "ONMI"
OMEGA_COL = "Omega"
FADDIS_RUNTIME_COL = "FADDIS Runtime"

# Variant name column.
VARIANT_COL = "Variation"

# Network setting column, without the instance number.
NETWORK_SETTING_COL = "Network Setting"

# Example network name: n2000_K50_f0.1_om3_inst2
NETWORK_RE = re.compile(
    r"n(?P<n>\d+)_K(?P<K>\d+)_f(?P<f>\d*\.?\d+)_om(?P<om>\d+)_inst(?P<inst>\d+)"
)


def plot_results_by_network(results_dir: str, input_filename: str = "_results.csv"):
    """
    Process the results by network setting and generate plots.

    The x-axis is the network configuration without the instance number.
    The instance number is used to compute mean and sample standard deviation.

    Parameters:
        results_dir : (str)
            Directory containing the experiment results.
            It can contain network folders directly or family/network folders.
        input_filename : (str, optional)
            The name of the CSV file containing the results for each network instance.
            Default is "_results.csv".

    Saves:
        - A CSV file with the raw results for all instances and variants, named "network_results.csv".
        - A CSV file with summary statistics for each network setting and variant, named "network_results_summary.csv".
        - Plots of ONMI, Omega, relative error of K and FADDIS Runtime, saved as PDF files.
    """

    rows = []

    for network_dir in _iter_network_result_dirs(results_dir, input_filename):
        properties = _parse_network_name(network_dir.name)

        if properties is None:
            continue

        network_setting = _build_network_setting(properties)

        results_csv_path = os.path.join(network_dir, input_filename)
        results_df = _read_csv(results_csv_path)

        has_faddis_runtime = FADDIS_RUNTIME_COL in results_df.columns

        for col in [GAMMA_COL, KERR_COL, ONMI_COL, OMEGA_COL]:
            results_df[col] = pd.to_numeric(results_df[col], errors="coerce")

        if has_faddis_runtime:
            results_df[FADDIS_RUNTIME_COL] = pd.to_numeric(results_df[FADDIS_RUNTIME_COL], errors="coerce")

        results_df[VARIANT_COL] = results_df.apply(lambda r: _build_variant_name(r.to_dict()), axis=1)

        for _, res in results_df.iterrows():
            row = {
                VARIANT_COL: res[VARIANT_COL],
                NETWORK_SETTING_COL: network_setting,
                NETWORK_PROPERTY_N: properties[NETWORK_PROPERTY_N],
                NETWORK_PROPERTY_K: properties[NETWORK_PROPERTY_K],
                NETWORK_PROPERTY_F: properties[NETWORK_PROPERTY_F],
                NETWORK_PROPERTY_OM: properties[NETWORK_PROPERTY_OM],
                NETWORK_PROPERTY_INST: properties[NETWORK_PROPERTY_INST],
                ONMI_COL: pd.to_numeric(res[ONMI_COL], errors="coerce"),
                OMEGA_COL: pd.to_numeric(res[OMEGA_COL], errors="coerce"),
                KERR_COL: pd.to_numeric(res[KERR_COL], errors="coerce"),
            }

            if has_faddis_runtime:
                row[FADDIS_RUNTIME_COL] = pd.to_numeric(res[FADDIS_RUNTIME_COL], errors="coerce")

            rows.append(row)

    raw_df = pd.DataFrame(rows)

    if raw_df.empty:
        raise ValueError("[ERROR] No valid network result directories were found.")

    raw_df = (
        raw_df
        .sort_values([
            NETWORK_PROPERTY_N,
            NETWORK_PROPERTY_K,
            NETWORK_PROPERTY_F,
            NETWORK_PROPERTY_OM,
            VARIANT_COL,
            NETWORK_PROPERTY_INST
        ])
        .reset_index(drop=True)
    )

    agg_dict = {
        "#Instances": (NETWORK_PROPERTY_INST, "nunique"),

        "ONMI Results": (ONMI_COL, results_as_json),
        "Mean ONMI": (ONMI_COL, "mean"),
        "Sample Std ONMI": (ONMI_COL, lambda s: s.std(ddof=1)),

        "Omega Results": (OMEGA_COL, results_as_json),
        "Mean Omega": (OMEGA_COL, "mean"),
        "Sample Std Omega": (OMEGA_COL, lambda s: s.std(ddof=1)),

        "Relative Error |K'-K|/K Results": (KERR_COL, results_as_json),
        "Mean Relative Error |K'-K|/K": (KERR_COL, "mean"),
        "Sample Std Relative Error |K'-K|/K": (KERR_COL, lambda s: s.std(ddof=1)),
    }

    if FADDIS_RUNTIME_COL in raw_df.columns:
        agg_dict.update({
            "FADDIS Runtime Results": (FADDIS_RUNTIME_COL, results_as_json),
            "Mean FADDIS Runtime": (FADDIS_RUNTIME_COL, "mean"),
            "Sample Std FADDIS Runtime": (FADDIS_RUNTIME_COL, lambda s: s.std(ddof=1)),
        })

    summary_df = (
        raw_df
        .groupby([NETWORK_SETTING_COL, VARIANT_COL], as_index=False)
        .agg(**agg_dict)
    )

    for col in [
        "Mean ONMI",
        "Sample Std ONMI",
        "Mean Omega",
        "Sample Std Omega",
        "Mean Relative Error |K'-K|/K",
        "Sample Std Relative Error |K'-K|/K",
        "Mean FADDIS Runtime",
        "Sample Std FADDIS Runtime",
    ]:
        if col in summary_df.columns:
            summary_df[col] = summary_df[col].round(6)

    raw_df.to_csv(os.path.join(results_dir, "network_results.csv"), index=False)
    summary_df.to_csv(os.path.join(results_dir, "network_results_summary.csv"), index=False)

    _plot_results_by_network(results_dir, summary_df)


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

    return sorted(
        [path.parent for path in Path(results_dir).rglob(input_filename)],
        key=lambda path: path.name,
    )


def _parse_network_name(network_name: str):
    """
    Parse a network name to extract its properties.

    Example:
        n2000_K50_f0.1_om3_inst2

    Parameters:
        network_name : (str)
            The name of the network.

    Returns:
        properties : (dict | None)
            A dictionary containing the network properties, or None if the name does not match.
    """

    m = NETWORK_RE.fullmatch(network_name)
    if not m:
        return None

    d = m.groupdict()
    return {
        NETWORK_PROPERTY_N: int(d[NETWORK_PROPERTY_N]),
        NETWORK_PROPERTY_K: int(d[NETWORK_PROPERTY_K]),
        NETWORK_PROPERTY_F: float(d[NETWORK_PROPERTY_F]),
        NETWORK_PROPERTY_OM: int(d[NETWORK_PROPERTY_OM]),
        NETWORK_PROPERTY_INST: int(d[NETWORK_PROPERTY_INST]),
    }


def _build_network_setting(properties: dict) -> str:
    """
    Build the network setting name without the instance number.

    Example:
        n2000_K50_f0.1_om3

    Parameters:
        properties : (dict)
            Parsed network properties.

    Returns:
        network_setting : (str)
            Network setting without instance number.
    """

    return (
        f"n{properties[NETWORK_PROPERTY_N]}_"
        f"K{properties[NETWORK_PROPERTY_K]}_"
        f"f{properties[NETWORK_PROPERTY_F]}_"
        f"om{properties[NETWORK_PROPERTY_OM]}"
    )


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

    variant_id = str(row[ID_COL]).strip().zfill(3)
    affinity_design = str(row[AFFINITY_DESIGN_COL]).strip().lower()
    execution_mode = str(row[EXECUTION_MODE_COL]).strip().lower()
    gamma = f"g{str(row[GAMMA_COL]).strip().lower()}"

    return f"{variant_id}_{affinity_design}_{execution_mode}_{gamma}"


def results_as_json(series: pd.Series) -> str:
    """
    Convert a pandas Series of results to a JSON string, handling NaN values appropriately.

    Parameters:
        series : (pd.Series)
            A pandas Series containing the results.

    Returns:
        json_str : (str)
            A JSON string representation of the results.
    """

    values = [None if pd.isna(x) else round(float(x), 6) for x in series.tolist()]
    return json.dumps(values)


def _plot_results_by_network(results_dir: str, df: pd.DataFrame):
    """
    Generate plots using the network setting as the x-axis.

    Parameters:
        results_dir : (str)
            Directory where the plots will be saved.
        df : (pd.DataFrame)
            DataFrame containing summary results.

    Saves:
        PDF plots in the results directory.
    """

    plot_variants = [
        None
    ]

    for idx, selected_variants in enumerate(plot_variants):
        plot_df = df.copy()

        if selected_variants is not None:
            plot_df = plot_df[plot_df[VARIANT_COL].isin(selected_variants)].copy()

        if plot_df.empty:
            continue

        network_settings = list(plot_df[NETWORK_SETTING_COL].drop_duplicates())
        x_positions = {network: i for i, network in enumerate(network_settings)}

        variants = list(plot_df[VARIANT_COL].drop_duplicates())

        has_faddis_runtime = "Mean FADDIS Runtime" in df.columns

        fig, axes = plt.subplots(2, 2, figsize=(15.5, 9.0))

        ax1 = axes[0, 0]
        ax2 = axes[0, 1]
        ax3 = axes[1, 0]
        ax4 = axes[1, 1]

        variant_markers = cycle(["x", "^", "s", "*", "D", "o", "v", "P", ">", "<", "h", "+"])
        variant_colors = {variant: plt.cm.tab20(i % 20) for i, variant in enumerate(variants)}

        for variant in variants:
            d = plot_df[plot_df[VARIANT_COL] == variant].copy()
            d["_x"] = d[NETWORK_SETTING_COL].map(x_positions)
            d = d.sort_values("_x")

            marker = next(variant_markers)
            color = variant_colors[variant]

            ax1.plot(
                d["_x"],
                d["Mean ONMI"],
                marker=marker,
                color=color,
                linewidth=1.8,
                markersize=7,
                label=variant,
            )

            ax2.plot(
                d["_x"],
                d["Mean Omega"],
                marker=marker,
                color=color,
                linewidth=1.8,
                markersize=7,
                label=variant,
            )

            ax3.plot(
                d["_x"],
                d["Mean Relative Error |K'-K|/K"],
                marker=marker,
                color=color,
                linewidth=1.8,
                markersize=7,
                label=variant,
            )

            if has_faddis_runtime:
                ax4.plot(
                    d["_x"],
                    d["Mean FADDIS Runtime"],
                    marker=marker,
                    color=color,
                    linewidth=1.8,
                    markersize=7,
                    label=variant,
                )

        if not has_faddis_runtime:
            ax4.axis("off")

        for ax in [ax1, ax2, ax3, ax4]:
            if not ax.axison:
                continue

            ax.set_xlabel("Network")
            ax.set_xticks(range(len(network_settings)))
            ax.set_xticklabels(network_settings, rotation=45, ha="right")
            ax.margins(x=0.03)
            ax.grid(True, alpha=0.3)

            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(
                    loc="upper right",
                    fontsize=8,
                    framealpha=0.3,
                    ncol=2,
                    columnspacing=0.8,
                    handletextpad=0.4,
                )

        ax1.set_ylabel("Mean ONMI")
        ax1.set_ylim(0, 1.0)

        ax2.set_ylabel("Mean Omega")
        ax2.set_ylim(0, 1.0)

        ax3.set_ylabel("Mean Relative Error |K'-K|/K")
        ax3.set_ylim(bottom=0)

        if has_faddis_runtime:
            ax4.set_ylabel("Mean FADDIS Runtime (seconds)")
            ax4.set_ylim(bottom=0)

        fig.tight_layout()
        fig.savefig(
            os.path.join(results_dir, f"network_results_all_variants.pdf"),
            dpi=300,
            bbox_inches="tight",
        )
        fig.savefig(
            os.path.join(results_dir, f"network_results_all_variants.png"),
            dpi=300,
            bbox_inches="tight",
        )

        plt.close(fig)


if __name__ == "__main__":
    # n2000
    plot_results_by_network(
        results_dir=os.path.join(
            RESULTS_BASE_DIR,
            "updated_size_variation_set",
            "experience9_cluster",
            "results_2026-05-06_17-17-41-795974"
        )
    )

    # n3000
    plot_results_by_network(
        results_dir=os.path.join(
            RESULTS_BASE_DIR,
            "updated_size_variation_set",
            "experience9_cluster",
            "results_2026-05-07_00-32-30-551860"
        )
    )

    # n4000
    plot_results_by_network(
        results_dir=os.path.join(
            RESULTS_BASE_DIR,
            "updated_size_variation_set",
            "experience9_cluster",
            "results_2026-05-09_00-35-20-804381"
        )
    )
