import json
import os.path
import re
from itertools import cycle
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

# Base directory for results.
RESULTS_BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'results', 'synthetic')

# Network property keys.
NETWORK_PROPERTY_N = "n"
NETWORK_PROPERTY_MU = "mu"
NETWORK_PROPERTY_ON = "on"
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

# Variant name column and limits for plots.
VARIANT_COL = "Variation"
VARIANT_LIMITS = {
    NETWORK_PROPERTY_N: (1000 - 200, 10000 + 200),
    NETWORK_PROPERTY_MU: (0.1 - 0.02, 0.8 + 0.02),
    NETWORK_PROPERTY_ON: (100 - 20, 600 + 20),
    NETWORK_PROPERTY_OM: (1 - 0.2, 8 + 0.2),
}

# Example network name: n1000mu0.1on200om2inst1
NETWORK_RE = re.compile(r"n(?P<n>\d+)mu(?P<mu>\d*\.?\d+)on(?P<on>\d+)om(?P<om>\d+)inst(?P<inst>\d+)")


def plot_variation_set_results(results_dir: str, variation_parameter: str, input_filename: str = "_results.csv"):
    """
    Processes the results of a variation set experiment, computes summary statistics, and generates plots.

    Parameters:
        results_dir : (str)
            Directory containing the experiment results, organized in subdirectories for each network instance.
        variation_parameter : (str)
            The network property to vary in the experiment.
        input_filename : (str, optional)
            The name of the CSV file containing the results for each network instance. 
            Default is "_results.csv".

    Saves:
        - A CSV file with the raw results for all instances and variants, named "{variation_parameter}_variation_set.csv".
        - A CSV file with summary statistics for each variant, named "{variation_parameter}_variation_set_summary.csv".
        - Plots of ONMI and Omega against the variation parameter for each variant, saved as PDF files in the results directory, named "{variation_parameter}_variation_set_{idx}.pdf".
    """

    rows = []
    for network_dir in _iter_sorted_dirs(results_dir):
        properties = _parse_network_name(network_dir.name)

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
                NETWORK_PROPERTY_N: properties[NETWORK_PROPERTY_N],
                NETWORK_PROPERTY_MU: properties[NETWORK_PROPERTY_MU],
                NETWORK_PROPERTY_ON: properties[NETWORK_PROPERTY_ON],
                NETWORK_PROPERTY_OM: properties[NETWORK_PROPERTY_OM],
                NETWORK_PROPERTY_INST: properties[NETWORK_PROPERTY_INST],
                ONMI_COL: pd.to_numeric(res[ONMI_COL], errors="coerce"),
                OMEGA_COL: pd.to_numeric(res[OMEGA_COL], errors="coerce"),
            }

            if has_faddis_runtime:
                row[FADDIS_RUNTIME_COL] = pd.to_numeric(res[FADDIS_RUNTIME_COL], errors="coerce")

            rows.append(row)

    raw_df = (pd.DataFrame(rows).sort_values([variation_parameter, VARIANT_COL, NETWORK_PROPERTY_INST])
              .reset_index(drop=True))

    agg_dict = {
        "#Instances": (NETWORK_PROPERTY_INST, "nunique"),
        "ONMI Results": (ONMI_COL, results_as_json),
        "Mean ONMI": (ONMI_COL, "mean"),
        "Sample Std ONMI": (ONMI_COL, lambda s: s.std(ddof=1)),
        "Omega Results": (OMEGA_COL, results_as_json),
        "Mean Omega": (OMEGA_COL, "mean"),
        "Sample Std Omega": (OMEGA_COL, lambda s: s.std(ddof=1)),
    }

    if FADDIS_RUNTIME_COL in raw_df.columns:
        agg_dict.update({
            "Mean FADDIS Runtime": (FADDIS_RUNTIME_COL, "mean"),
            "Sample Std FADDIS Runtime": (FADDIS_RUNTIME_COL, lambda s: s.std(ddof=1)),
        })

    summary_df = (
        raw_df
        .groupby([variation_parameter, VARIANT_COL], as_index=False)
        .agg(**agg_dict)
    )

    for col in [
        "Mean ONMI", "Sample Std ONMI", "Mean Omega", "Sample Std Omega", "Mean FADDIS Runtime",
        "Sample Std FADDIS Runtime"
    ]:
        if col in summary_df.columns:
            summary_df[col] = summary_df[col].round(6)

    raw_df.to_csv(os.path.join(results_dir, f"{variation_parameter}_variation_set.csv"), index=False)
    summary_df.to_csv(os.path.join(results_dir, f"{variation_parameter}_variation_set_summary.csv"), index=False)

    _plot_results(results_dir, summary_df, variation_parameter)


def _iter_sorted_dirs(directory: str) -> list[Path]:
    """
    Iterate over sorted directories in a given directory.

    Parameters:
        directory : (str)
            Directory to iterate over.

    Returns:
        list : (list[Path])
            A list of Path objects representing the sorted directories within the given directory.
    """
    return sorted(
        [path for path in Path(directory).iterdir() if path.is_dir()],
        key=lambda path: path.name,
    )


def _parse_network_name(network_name: str):
    """
    Parse a network name to extract its properties.
    
    Parameters:
        network_name : (str)
            The name of the network.

    Returns:
        dict : (dict)
            A dictionary containing the network properties.
    """

    m = NETWORK_RE.fullmatch(network_name)
    if not m:
        return None

    d = m.groupdict()
    return {
        NETWORK_PROPERTY_N: int(d[NETWORK_PROPERTY_N]),
        NETWORK_PROPERTY_MU: float(d[NETWORK_PROPERTY_MU]),
        NETWORK_PROPERTY_ON: int(d[NETWORK_PROPERTY_ON]),
        NETWORK_PROPERTY_OM: int(d[NETWORK_PROPERTY_OM]),
        NETWORK_PROPERTY_INST: int(d[NETWORK_PROPERTY_INST]),
    }


def _read_csv(csv_path: str) -> pd.DataFrame:
    """
    Read a CSV file.

    Parameters:
        csv_path : (str)
            The path to the CSV file.

    Returns:
        pd.DataFrame : (pd.DataFrame)
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
    laplacian = str(row[LAPLACIAN_COL]).strip().lower()
    gamma = f"g{str(row[GAMMA_COL]).strip().lower()}"

    return f"{variant_id}_{affinity_design}_{execution_mode}_{laplacian}_{gamma}"


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


def _plot_results(results_dir: str, df: pd.DataFrame, variation_parameter: str):
    """
    Generate plots for the variation set results.

    Parameters:
        results_dir : (str)
            Directory where the plots will be saved.
        df : (pd.DataFrame)
            DataFrame containing the summary results for the variation set.
        variation_parameter : (str)
            The network property that was varied in the experiment, used for labeling the plots.
    
    Saves:
        Plots of ONMI, Omega, and FADDIS Runtime against the variation parameter for each variant,
        saved as PDF files in the results directory.
    """

    plot_variants = [
        None,
        ["005_default_lapin-off_-_g0.8", "006_default_lapin-off_-_g0.9"]
    ]

    for idx, selected_variants in enumerate(plot_variants):
        plot_df = df.copy()

        if selected_variants is not None:
            plot_df = plot_df[plot_df[VARIANT_COL].isin(selected_variants)].copy()

        variants = list(plot_df[VARIANT_COL].drop_duplicates())

        has_faddis_runtime = "Mean FADDIS Runtime" in df.columns

        if has_faddis_runtime:
            fig = plt.figure(figsize=(13.5, 9.0))
            gs = fig.add_gridspec(2, 2)

            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            ax3 = fig.add_subplot(gs[1, :])  # Runtime plot below both
        else:
            fig = plt.figure(figsize=(13.5, 4.5))
            gs = fig.add_gridspec(1, 2)

            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            ax3 = None

        variant_markers = cycle(["x", "^", "s", "*", "D", "o", "v", "P", ">", "<", "h", "+"])
        variant_colors = {variant: plt.cm.tab20(i % 20) for i, variant in enumerate(variants)}

        for variant in variants:
            d = plot_df[plot_df[VARIANT_COL] == variant].sort_values(variation_parameter)
            marker = next(variant_markers)
            color = variant_colors[variant]

            ax1.plot(
                d[variation_parameter], d["Mean ONMI"],
                marker=marker, color=color, linewidth=1.8, markersize=7, label=variant
            )
            ax2.plot(
                d[variation_parameter], d["Mean Omega"],
                marker=marker, color=color, linewidth=1.8, markersize=7, label=variant
            )

            if has_faddis_runtime:
                ax3.errorbar(
                    d[variation_parameter],
                    d["Mean FADDIS Runtime"],
                    yerr=d["Sample Std FADDIS Runtime"],
                    marker=marker,
                    color=color,
                    linewidth=1.8,
                    markersize=7,
                    capsize=4,
                    label=variant
                )

        ax1.set_xlabel(variation_parameter)
        ax1.set_xlim(VARIANT_LIMITS[variation_parameter][0], VARIANT_LIMITS[variation_parameter][1])
        ax1.set_ylabel("ONMI")
        ax1.set_ylim(0, 1.0)
        ax1.legend(loc="upper right", fontsize=10)
        ax1.margins(x=0.03)
        ax1.grid(True, alpha=0.3)

        ax2.set_xlabel(variation_parameter)
        ax2.set_xlim(VARIANT_LIMITS[variation_parameter][0], VARIANT_LIMITS[variation_parameter][1])
        ax2.set_ylabel("Omega")
        ax2.set_ylim(0, 1.0)
        ax2.legend(loc="upper right", fontsize=10)
        ax2.margins(x=0.03)
        ax2.grid(True, alpha=0.3)

        if has_faddis_runtime:
            ax3.set_xlabel(variation_parameter)
            ax3.set_xlim(VARIANT_LIMITS[variation_parameter][0], VARIANT_LIMITS[variation_parameter][1])
            ax3.set_ylabel("FADDIS Runtime (in seconds)")
            ax3.legend(loc="upper right", fontsize=10)
            ax3.margins(x=0.03)
            ax3.grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig(
            os.path.join(results_dir, f"{variation_parameter}_variation_set_{idx}.pdf"), dpi=300, bbox_inches="tight"
        )

        plt.close(fig)


if __name__ == "__main__":
    # Boundary variation set.
    for folders in [
        ("experience1_cluster", "results_2026-04-10_13-16-21-594342"),
        ("experience2_cluster", "results_2026-04-10_18-46-27-529048"),
        ("experience3_cluster", "results_2026-04-10_21-39-07-593414"),
        ("experience4_cluster", "results_2026-04-11_00-08-06-619023"),

        ("experience5_cluster_0", "results_2026-04-19_12-06-10-999135"),

        ("experience5_cluster", "results_2026-05-02_09-15-07-970979"),
        ("experience6_cluster", "results_2026-05-02_11-26-20-488782"),
        ("experience7_cluster", "results_2026-05-02_15-23-59-555680"),
        ("experience8_cluster", "results_2026-05-02_16-46-53-100982")
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(RESULTS_BASE_DIR, "boundary_variation_set", folders[0], folders[1]),
            variation_parameter=NETWORK_PROPERTY_MU
        )

    # Membership variation set.
    for folders in [
        ("experience1_cluster", "results_2026-04-11_11-39-05-745642"),
        ("experience2_cluster", "results_2026-04-11_23-31-55-403981"),
        ("experience3_cluster", "results_2026-04-12_09-50-03-559581"),
        ("experience4_cluster", "results_2026-04-12_11-35-17-967624"),

        ("experience5_cluster_0", "results_2026-04-19_18-21-44-389254"),

        ("experience5_cluster", "results_2026-05-02_19-27-44-446056"),
        ("experience6_cluster", "results_2026-05-02_22-55-58-140699"),
        ("experience7_cluster", "results_2026-05-03_00-33-14-635642"),
        ("experience8_cluster", "results_2026-05-03_08-11-41-388440"),
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR, "membership_variation_set", folders[0], folders[1]
            ),
            variation_parameter=NETWORK_PROPERTY_OM
        )

    # Overlap variation set.
    for folders in [
        ("experience1_cluster", "results_2026-04-12_13-46-36-158854"),
        ("experience2_cluster", "results_2026-04-12_15-41-47-330370"),
        ("experience3_cluster", "results_2026-04-12_17-17-12-630419"),
        ("experience4_cluster", "results_2026-04-12_18-47-18-341627"),

        ("experience5_cluster_0", "results_2026-04-19_22-29-26-629180"),

        ("experience5_cluster", "results_2026-05-03_12-11-56-013021"),
        ("experience6_cluster", "results_2026-05-03_14-23-08-858214"),
        ("experience7_cluster", "results_2026-05-03_15-37-47-343899"),
        ("experience8_cluster", "results_2026-05-03_16-44-48-087897"),
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR, "overlap_variation_set", folders[0], folders[1]
            ),
            variation_parameter=NETWORK_PROPERTY_ON
        )

    # Size variation set.
    for folders in [
        # ("experience1_cluster", "results_2026-04-12_20-42-10-997187"),
        # ("experience2_cluster", "results_2026-04-13_19-12-06-974844"),
        # ("experience3_cluster", "results_2026-04-14_10-15-07-924997"),
        # ("experience4_cluster", "results_2026-04-14_17-27-01-073540"),

        ("faddis_version_a_got", "results_2026-04-20_08-40-19-143228"),
        ("faddis_version_m", "results_2026-04-26_00-05-03-708303"),
        ("faddis_version_a_top_10", "results_2026-04-26_08-24-20-677914"),
        ("faddis_version_a_improved", "results_2026-04-30_00-23-38-440972"),

        ("faddis_numpy_eigh", "results_2026-05-01_22-11-08-231496"),
        ("faddis_scipy_eigh_evd", "results_2026-05-01_19-11-52-478180"),
        ("faddis_scipy_eigh_evr", "results_2026-05-01_16-12-18-640998"),

        # ("experience5_cluster", "results_2026-05-03_19-16-46-640640"),
        # ("experience6_cluster", "results_2026-05-03_19-52-19-167434"),
        # ("experience7_cluster", "results_2026-05-03_20-32-31-224707"),
        # ("experience8_cluster", "results_2026-05-03_21-25-59-359439"),
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(
                RESULTS_BASE_DIR, "size_variation_set", folders[0], folders[1]
            ),
            variation_parameter=NETWORK_PROPERTY_N
        )
