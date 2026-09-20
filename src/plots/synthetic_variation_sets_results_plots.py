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
SIGNED_KERR_COL = "(K'-K)/K"
NODE_COVERAGE_COL = "Node Coverage"
K_PAIR_COL = "K' | K"
N_SPARSIFIED_N_COL = "N | Sparsified N"
ONMI_COL = "ONMI"
OMEGA_COL = "Omega"
FADDIS_RUNTIME_COL = "FADDIS Runtime"

# Pareto-based acceptability tolerance fractions.
PARETO_TOLERANCE_FRACTION_ONMI = 0.15
PARETO_TOLERANCE_FRACTION_OMEGA = 0.15
PARETO_TOLERANCE_FRACTION_KERR = 0.5

# Variant name column and limits for plots.
VARIANT_COL = "Variant"
VARIANT_LIMITS = {
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
NETWORK_RE = re.compile(r"n(?P<n>\d+)mu(?P<mu>\d*\.?\d+)on(?P<on>\d+)om(?P<om>\d+)inst(?P<inst>\d+)")


def plot_variation_set_results(results_dir: str, variation_parameter: str, input_filename: str = "_results.csv"):
    """
    Process a variation-set experiment, compute summary statistics, and generate plots.

    Parameters:
        results_dir : (str)
            Directory containing one subdirectory per network instance.
        variation_parameter : (str)
            Network property varied in the experiment.
        input_filename : (str, optional)
            Name of the CSV file containing the results for each network instance.
            Default is "_results.csv".

    Saves:
        - Raw results in "{variation_parameter}_results.csv".
        - Summary statistics in "{variation_parameter}_summary.csv".
        - Best variants by parameter in "{variation_parameter}_best_by_param.csv".
        - Best variants by affinity design in "{variation_parameter}_best_by_affinity.csv".
        - Best variants by parameter and affinity design in
          "{variation_parameter}_best_by_param_affinity.csv".
        - ONMI, Omega, relative K error, and FADDIS runtime plots in PDF and PNG formats.

    Notes:
        The signed relative K error is derived from "K' | K". Node coverage is derived
        from "N | Sparsified N" when that source column is available; otherwise it is NaN.
    """

    rows = []
    for network_dir in _iter_sorted_dirs(results_dir):
        properties = _parse_network_name(network_dir.name)

        results_csv_path = os.path.join(network_dir, input_filename)
        results_df = _read_csv(results_csv_path)
        has_faddis_runtime = FADDIS_RUNTIME_COL in results_df.columns

        # Derive the signed K error and, when available, node coverage from the existing paired columns.
        results_df[SIGNED_KERR_COL] = results_df[K_PAIR_COL].apply(_compute_signed_relative_k_error)

        if N_SPARSIFIED_N_COL in results_df.columns:
            results_df[NODE_COVERAGE_COL] = results_df[N_SPARSIFIED_N_COL].apply(_compute_node_coverage)
        else:
            results_df[NODE_COVERAGE_COL] = float("nan")

        for col in [GAMMA_COL, KERR_COL, SIGNED_KERR_COL, NODE_COVERAGE_COL, ONMI_COL, OMEGA_COL]:
            results_df[col] = pd.to_numeric(results_df[col], errors="coerce")

        if has_faddis_runtime:
            results_df[FADDIS_RUNTIME_COL] = pd.to_numeric(results_df[FADDIS_RUNTIME_COL], errors="coerce")

        results_df[VARIANT_COL] = results_df.apply(lambda r: _build_variant_name(r.to_dict()), axis=1)

        for _, res in results_df.iterrows():
            row = {
                VARIANT_COL: res[VARIANT_COL],
                AFFINITY_DESIGN_COL: str(res[AFFINITY_DESIGN_COL]).strip().lower(),
                NETWORK_PROPERTY_N: properties[NETWORK_PROPERTY_N],
                NETWORK_PROPERTY_MU: properties[NETWORK_PROPERTY_MU],
                NETWORK_PROPERTY_ON: properties[NETWORK_PROPERTY_ON],
                NETWORK_PROPERTY_OM: properties[NETWORK_PROPERTY_OM],
                NETWORK_PROPERTY_INST: properties[NETWORK_PROPERTY_INST],
                ONMI_COL: pd.to_numeric(res[ONMI_COL], errors="coerce"),
                OMEGA_COL: pd.to_numeric(res[OMEGA_COL], errors="coerce"),
                KERR_COL: pd.to_numeric(res[KERR_COL], errors="coerce"),
                SIGNED_KERR_COL: pd.to_numeric(res[SIGNED_KERR_COL], errors="coerce"),
                NODE_COVERAGE_COL: pd.to_numeric(res[NODE_COVERAGE_COL], errors="coerce"),
            }

            if has_faddis_runtime:
                row[FADDIS_RUNTIME_COL] = pd.to_numeric(res[FADDIS_RUNTIME_COL], errors="coerce")

            rows.append(row)

    raw_df = (
        pd.DataFrame(rows)
        .sort_values([variation_parameter, AFFINITY_DESIGN_COL, VARIANT_COL, NETWORK_PROPERTY_INST])
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

        "Signed Relative Error (K'-K)/K Results": (SIGNED_KERR_COL, results_as_json),
        "Mean Signed Relative Error (K'-K)/K": (SIGNED_KERR_COL, "mean"),
        "Sample Std Signed Relative Error (K'-K)/K": (SIGNED_KERR_COL, lambda s: s.std(ddof=1)),

        "Node Coverage Results": (NODE_COVERAGE_COL, results_as_json),
        "Mean Node Coverage": (NODE_COVERAGE_COL, "mean"),
        "Sample Std Node Coverage": (NODE_COVERAGE_COL, lambda s: s.std(ddof=1)),
    }

    if FADDIS_RUNTIME_COL in raw_df.columns:
        agg_dict.update({
            "FADDIS Runtime Results": (FADDIS_RUNTIME_COL, results_as_json),
            "Mean FADDIS Runtime": (FADDIS_RUNTIME_COL, "mean"),
            "Sample Std FADDIS Runtime": (FADDIS_RUNTIME_COL, lambda s: s.std(ddof=1)),
        })

    summary_df = (
        raw_df
        .groupby([variation_parameter, AFFINITY_DESIGN_COL, VARIANT_COL], as_index=False)
        .agg(**agg_dict)
    )

    for col in [
        "Mean ONMI",
        "Sample Std ONMI",
        "Mean Omega",
        "Sample Std Omega",
        "Mean Relative Error |K'-K|/K",
        "Sample Std Relative Error |K'-K|/K",
        "Mean Signed Relative Error (K'-K)/K",
        "Sample Std Signed Relative Error (K'-K)/K",
        "Mean Node Coverage",
        "Sample Std Node Coverage",
        "Mean FADDIS Runtime",
        "Sample Std FADDIS Runtime",
    ]:
        if col in summary_df.columns:
            summary_df[col] = summary_df[col].round(6)

    best_variants_affinity_design_df = _select_best_variants_by_affinity_design(summary_df)
    best_variation_parameter_variants_df = _select_best_variants_by_variation_parameter(
        summary_df,
        variation_parameter,
    )
    best_variation_parameter_affinity_variants_df = _select_best_variants_by_variation_parameter_and_affinity_design(
        summary_df,
        variation_parameter,
    )

    raw_df.to_csv(
        os.path.join(results_dir, f"{variation_parameter}_results.csv"),
        index=False,
    )
    summary_df.to_csv(
        os.path.join(results_dir, f"{variation_parameter}_summary.csv"),
        index=False,
    )
    best_variation_parameter_variants_df.to_csv(
        os.path.join(results_dir, f"{variation_parameter}_best_by_param.csv"),
        index=False,
    )
    best_variants_affinity_design_df.to_csv(
        os.path.join(results_dir, f"{variation_parameter}_best_by_affinity.csv"),
        index=False,
    )
    best_variation_parameter_affinity_variants_df.to_csv(
        os.path.join(results_dir, f"{variation_parameter}_best_by_param_affinity.csv"),
        index=False,
    )

    _plot_results(results_dir, summary_df, variation_parameter)


def _iter_sorted_dirs(directory: str) -> list[Path]:
    """
    Return the immediate subdirectories of a directory in sorted order.

    Parameters:
        directory : (str)
            Directory whose subdirectories will be listed.

    Returns:
        directories : (list[Path])
            Sorted list of immediate subdirectories.
    """
    return sorted(
        [path for path in Path(directory).iterdir() if path.is_dir()],
        key=lambda path: path.name,
    )


def _parse_network_name(network_name: str):
    """
    Parse a network directory name into its network properties.

    Parameters:
        network_name : (str)
            Name of the network directory.

    Returns:
        properties : (dict | None)
            Parsed n, mu, on, om, and instance values, or None when the name does not
            match the expected format.

    Notes:
        Expected format example: "n1000mu0.1on200om2inst1".
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
    Read a results CSV file and normalize its column names.

    Parameters:
        csv_path : (str)
            Path to the CSV file.

    Returns:
        df : (pd.DataFrame)
            DataFrame containing the CSV data with stripped column names.
    """

    df = pd.read_csv(csv_path, sep=",", engine="python")
    df.columns = [c.strip() for c in df.columns]
    return df


def _compute_signed_relative_k_error(value) -> float:
    """
    Compute the signed relative error of the detected number of communities.

    Parameters:
        value : (object)
            Value formatted as "K' | K", where K' is the detected number of communities
            and K is the ground-truth number of communities.

    Returns:
        signed_relative_error : (float)
            Value of (K' - K) / K, or NaN when the input cannot be parsed or K is zero.
    """
    try:
        k_pred, k_true = [float(v.strip()) for v in str(value).split("|", 1)]
        return (k_pred - k_true) / k_true if k_true != 0 else float("nan")
    except (TypeError, ValueError):
        return float("nan")


def _compute_node_coverage(value) -> float:
    """
    Compute the fraction of original nodes retained after sparsification.

    Parameters:
        value : (object)
            Value formatted as "N | Sparsified N".

    Returns:
        node_coverage : (float)
            Value of Sparsified N / N, or NaN when the input cannot be parsed or N is zero.
    """
    try:
        n, sparsified_n = [float(v.strip()) for v in str(value).split("|", 1)]
        return sparsified_n / n if n != 0 else float("nan")
    except (TypeError, ValueError):
        return float("nan")


def _build_variant_name(row: dict[str, str]) -> str:
    """
    Build the normalized variant name for a results row.

    Parameters:
        row : (dict[str, str])
            Dictionary representing one row from the results CSV.

    Returns:
        variant_name : (str)
            Variant name composed of the zero-padded ID, affinity design, execution mode,
            and gamma value.
    """

    variant_id = str(row[ID_COL]).strip().zfill(3)
    affinity_design = str(row[AFFINITY_DESIGN_COL]).strip().lower()
    execution_mode = str(row[EXECUTION_MODE_COL]).strip().lower()
    # laplacian = str(row[LAPLACIAN_COL]).strip().lower()
    gamma = rf"$\gamma{str(row[GAMMA_COL]).strip().lower()}$"

    # return f"{variant_id}_{affinity_design}_{execution_mode}_{laplacian}_{gamma}"
    return f"{variant_id}_{affinity_design}_{execution_mode}_{gamma}"


def results_as_json(series: pd.Series) -> str:
    """
    Convert a pandas Series of numeric results to a JSON string.

    Parameters:
        series : (pd.Series)
            Series containing the result values.

    Returns:
        json_str : (str)
            JSON string containing values rounded to six decimal places, with NaN values
            represented as null.
    """

    values = [None if pd.isna(x) else round(float(x), 6) for x in series.tolist()]
    return json.dumps(values)


def _select_best_candidate_with_pareto_and_parsimony(
        df: pd.DataFrame,
        onmi_col: str,
        omega_col: str,
        kerr_col: str,
        runtime_col: str = None,
) -> pd.Series:
    """
    Select one candidate using tolerance-based acceptability and runtime parsimony.

    Parameters:
        df : (pd.DataFrame)
            DataFrame containing the candidates in one selection group.
        onmi_col : (str)
            Name of the ONMI column to maximize.
        omega_col : (str)
            Name of the Omega column to maximize.
        kerr_col : (str)
            Name of the absolute relative K error column to minimize.
        runtime_col : (str | None, optional)
            Name of the runtime column used for parsimony. Default is None.

    Returns:
        best_candidate : (pd.Series)
            Selected candidate.

    Notes:
        Candidates within the configured ONMI, Omega, and K-error tolerances are retained.
        Among acceptable candidates, lower runtime is preferred when available, followed
        by ONMI, Omega, K error, and variant name. If no candidate is jointly acceptable,
        the function falls back to ONMI, Omega, K error, and variant-name ordering.
    """

    valid_df = df.dropna(subset=[onmi_col, omega_col, kerr_col]).copy()

    if valid_df.empty:
        return df.sort_values(VARIANT_COL).iloc[0]

    onmi_delta = (
            PARETO_TOLERANCE_FRACTION_ONMI
            * (valid_df[onmi_col].max() - valid_df[onmi_col].min())
    )
    omega_delta = (
            PARETO_TOLERANCE_FRACTION_OMEGA
            * (valid_df[omega_col].max() - valid_df[omega_col].min())
    )
    kerr_delta = (
            PARETO_TOLERANCE_FRACTION_KERR
            * (valid_df[kerr_col].max() - valid_df[kerr_col].min())
    )

    acceptable_df = valid_df[
        (valid_df[onmi_col] >= valid_df[onmi_col].max() - onmi_delta)
        & (valid_df[omega_col] >= valid_df[omega_col].max() - omega_delta)
        & (valid_df[kerr_col] <= valid_df[kerr_col].min() + kerr_delta)
        ].copy()

    if acceptable_df.empty:
        print("[DEBUG] Fallback...")
        return (
            valid_df
            .sort_values(
                by=[onmi_col, omega_col, kerr_col, VARIANT_COL],
                ascending=[False, False, True, True],
            )
            .iloc[0]
        )

    sort_columns = []
    ascending = []

    print("[DEBUG] Acceptable...")
    # Parsimony: among practically indistinguishable candidates, prefer lower runtime.
    if runtime_col is not None and runtime_col in acceptable_df.columns:
        sort_columns.append(runtime_col)
        ascending.append(True)

    sort_columns.extend([onmi_col, omega_col, kerr_col, VARIANT_COL])
    ascending.extend([False, False, True, True])

    return (
        acceptable_df
        .sort_values(
            by=sort_columns,
            ascending=ascending,
            na_position="last",
        )
        .iloc[0]
    )


def _select_best_candidates_by_group(
        df: pd.DataFrame,
        group_columns: list[str],
        onmi_col: str,
        omega_col: str,
        kerr_col: str,
        runtime_col: str = None,
) -> pd.DataFrame:
    """
    Select one candidate per group using the common selection procedure.

    Parameters:
        df : (pd.DataFrame)
            DataFrame containing the candidates.
        group_columns : (list[str])
            Columns defining each independent selection group.
        onmi_col : (str)
            Name of the ONMI column to maximize.
        omega_col : (str)
            Name of the Omega column to maximize.
        kerr_col : (str)
            Name of the absolute relative K error column to minimize.
        runtime_col : (str | None, optional)
            Name of the runtime column used for parsimony. Default is None.

    Returns:
        selected_df : (pd.DataFrame)
            DataFrame containing one selected candidate per group.
    """

    selected_candidates = []

    for _, group_df in df.groupby(group_columns, sort=True, dropna=False):
        selected_candidates.append(
            _select_best_candidate_with_pareto_and_parsimony(
                df=group_df,
                onmi_col=onmi_col,
                omega_col=omega_col,
                kerr_col=kerr_col,
                runtime_col=runtime_col,
            )
        )

    return pd.DataFrame(selected_candidates).reset_index(drop=True)


def _select_best_variants_by_variation_parameter(df: pd.DataFrame, variation_parameter: str) -> pd.DataFrame:
    """
    Select the best variant for each value of the variation parameter.

    Parameters:
        df : (pd.DataFrame)
            DataFrame containing the summary results for the variation set.
        variation_parameter : (str)
            Network property varied in the experiment.

    Returns:
        selected_df : (pd.DataFrame)
            DataFrame containing one selected variant for each variation-parameter value.

    Notes:
        Selection uses mean ONMI, mean Omega, mean absolute relative K error, and mean
        FADDIS runtime through the common acceptability-and-parsimony procedure.
    """

    return _select_best_candidates_by_group(
        df=df,
        group_columns=[variation_parameter],
        onmi_col="Mean ONMI",
        omega_col="Mean Omega",
        kerr_col="Mean Relative Error |K'-K|/K",
        runtime_col="Mean FADDIS Runtime",
    )


def _select_best_variants_by_affinity_design(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select the best variant for each affinity design across the variation set.

    Parameters:
        df : (pd.DataFrame)
            DataFrame containing the summary results for the variation set.

    Returns:
        selected_df : (pd.DataFrame)
            DataFrame containing one selected variant for each affinity design.

    Notes:
        Metrics are first aggregated across variation-parameter values for each affinity
        design and variant. Selection uses overall mean ONMI, Omega, absolute relative
        K error, and FADDIS runtime. Signed K error and node coverage are retained as
        reported statistics but are not used in the selection criterion.
    """

    agg_dict = {
        "Overall Mean ONMI": ("Mean ONMI", "mean"),
        "Overall Sample Std ONMI": ("Mean ONMI", lambda s: s.std(ddof=1)),

        "Overall Mean Omega": ("Mean Omega", "mean"),
        "Overall Sample Std Omega": ("Mean Omega", lambda s: s.std(ddof=1)),

        "Overall Mean Relative Error |K'-K|/K": (
            "Mean Relative Error |K'-K|/K",
            "mean",
        ),
        "Overall Sample Std Relative Error |K'-K|/K": (
            "Mean Relative Error |K'-K|/K",
            lambda s: s.std(ddof=1),
        ),

        "Overall Mean Signed Relative Error (K'-K)/K": (
            "Mean Signed Relative Error (K'-K)/K",
            "mean",
        ),
        "Overall Sample Std Signed Relative Error (K'-K)/K": (
            "Mean Signed Relative Error (K'-K)/K",
            lambda s: s.std(ddof=1),
        ),

        "Overall Mean Node Coverage": ("Mean Node Coverage", "mean"),
        "Overall Sample Std Node Coverage": (
            "Mean Node Coverage",
            lambda s: s.std(ddof=1),
        ),
    }

    if "Mean FADDIS Runtime" in df.columns:
        agg_dict.update({
            "Overall Mean FADDIS Runtime": ("Mean FADDIS Runtime", "mean"),
            "Overall Sample Std FADDIS Runtime": (
                "Mean FADDIS Runtime",
                lambda s: s.std(ddof=1),
            ),
        })

    ranking_df = (
        df
        .groupby([AFFINITY_DESIGN_COL, VARIANT_COL], as_index=False)
        .agg(**agg_dict)
    )

    for col in [
        "Overall Mean ONMI",
        "Overall Sample Std ONMI",
        "Overall Mean Omega",
        "Overall Sample Std Omega",
        "Overall Mean Relative Error |K'-K|/K",
        "Overall Sample Std Relative Error |K'-K|/K",
        "Overall Mean Signed Relative Error (K'-K)/K",
        "Overall Sample Std Signed Relative Error (K'-K)/K",
        "Overall Mean Node Coverage",
        "Overall Sample Std Node Coverage",
        "Overall Mean FADDIS Runtime",
        "Overall Sample Std FADDIS Runtime",
    ]:
        if col in ranking_df.columns:
            ranking_df[col] = ranking_df[col].round(6)

    return _select_best_candidates_by_group(
        df=ranking_df,
        group_columns=[AFFINITY_DESIGN_COL],
        onmi_col="Overall Mean ONMI",
        omega_col="Overall Mean Omega",
        kerr_col="Overall Mean Relative Error |K'-K|/K",
        runtime_col="Overall Mean FADDIS Runtime",
    )


def _select_best_variants_by_variation_parameter_and_affinity_design(
        df: pd.DataFrame,
        variation_parameter: str,
) -> pd.DataFrame:
    """
    Select and order the best variant for each parameter value and affinity design.

    Parameters:
        df : (pd.DataFrame)
            DataFrame containing the summary results for the variation set.
        variation_parameter : (str)
            Network property varied in the experiment.

    Returns:
        selected_df : (pd.DataFrame)
            DataFrame containing one selected variant per parameter-value/affinity-design
            group, ordered within each parameter value by the common ranking procedure.
    """

    selected_df = _select_best_candidates_by_group(
        df=df,
        group_columns=[variation_parameter, AFFINITY_DESIGN_COL],
        onmi_col="Mean ONMI",
        omega_col="Mean Omega",
        kerr_col="Mean Relative Error |K'-K|/K",
        runtime_col="Mean FADDIS Runtime",
    )

    ordered_groups = []

    for _, group_df in selected_df.groupby(
            variation_parameter,
            sort=True,
            dropna=False,
    ):
        ordered_groups.append(
            _order_candidates_with_pareto_and_parsimony(
                df=group_df,
                onmi_col="Mean ONMI",
                omega_col="Mean Omega",
                kerr_col="Mean Relative Error |K'-K|/K",
                runtime_col="Mean FADDIS Runtime",
            )
        )

    return pd.concat(
        ordered_groups,
        ignore_index=True,
    )


def _order_candidates_with_pareto_and_parsimony(
        df: pd.DataFrame,
        onmi_col: str,
        omega_col: str,
        kerr_col: str,
        runtime_col: str = None,
) -> pd.DataFrame:
    """
    Order candidates using tolerance-based acceptability and runtime parsimony.

    Parameters:
        df : (pd.DataFrame)
            DataFrame containing candidates to order.
        onmi_col : (str)
            Name of the ONMI column to maximize.
        omega_col : (str)
            Name of the Omega column to maximize.
        kerr_col : (str)
            Name of the absolute relative K error column to minimize.
        runtime_col : (str | None, optional)
            Name of the runtime column used for parsimony. Default is None.

    Returns:
        ordered_df : (pd.DataFrame)
            Candidates ordered with acceptable candidates first, followed by fallback
            candidates.

    Notes:
        Acceptable candidates are ordered by runtime when available, then ONMI, Omega,
        K error, and variant name. Fallback candidates are ordered by ONMI, Omega,
        K error, and variant name.
    """

    valid_df = df.dropna(subset=[onmi_col, omega_col, kerr_col]).copy()

    if valid_df.empty:
        return df.sort_values(VARIANT_COL).reset_index(drop=True)

    onmi_delta = (
            PARETO_TOLERANCE_FRACTION_ONMI
            * (valid_df[onmi_col].max() - valid_df[onmi_col].min())
    )
    omega_delta = (
            PARETO_TOLERANCE_FRACTION_OMEGA
            * (valid_df[omega_col].max() - valid_df[omega_col].min())
    )
    kerr_delta = (
            PARETO_TOLERANCE_FRACTION_KERR
            * (valid_df[kerr_col].max() - valid_df[kerr_col].min())
    )

    acceptable_mask = (
            (valid_df[onmi_col] >= valid_df[onmi_col].max() - onmi_delta)
            & (valid_df[omega_col] >= valid_df[omega_col].max() - omega_delta)
            & (valid_df[kerr_col] <= valid_df[kerr_col].min() + kerr_delta)
    )

    acceptable_df = valid_df[acceptable_mask].copy()
    fallback_df = valid_df[~acceptable_mask].copy()

    acceptable_sort_columns = []
    acceptable_ascending = []

    if runtime_col is not None and runtime_col in acceptable_df.columns:
        acceptable_sort_columns.append(runtime_col)
        acceptable_ascending.append(True)

    acceptable_sort_columns.extend(
        [onmi_col, omega_col, kerr_col, VARIANT_COL]
    )
    acceptable_ascending.extend(
        [False, False, True, True]
    )

    acceptable_df = acceptable_df.sort_values(
        by=acceptable_sort_columns,
        ascending=acceptable_ascending,
        na_position="last",
    )

    fallback_df = fallback_df.sort_values(
        by=[onmi_col, omega_col, kerr_col, VARIANT_COL],
        ascending=[False, False, True, True],
        na_position="last",
    )

    return pd.concat(
        [acceptable_df, fallback_df],
        ignore_index=True,
    )


def _plot_results(results_dir: str, df: pd.DataFrame, variation_parameter: str):
    """
    Generate metric plots against the selected variation parameter.

    Parameters:
        results_dir : (str)
            Directory where the plots will be saved.
        df : (pd.DataFrame)
            DataFrame containing the summary results for the variation set.
        variation_parameter : (str)
            Network property used on the x-axis.

    Saves:
        - All-variant plots as "{variation_parameter}_all_variants.pdf" and PNG.
        - Best-by-affinity plots as
          "{variation_parameter}_best_variants_by_affinity_design.pdf" and PNG.

    Notes:
        Each figure shows mean ONMI, mean Omega, mean absolute relative K error, and,
        when available, mean FADDIS runtime.
    """

    best_variants_df = _select_best_variants_by_affinity_design(df)
    plot_variants = [
        None,
        best_variants_df[VARIANT_COL].tolist(),
    ]

    plot_names = [
        "all_variants",
        "best_variants_by_affinity_design",
    ]

    for idx, selected_variants in enumerate(plot_variants):
        plot_df = df.copy()

        if selected_variants is not None:
            plot_df = plot_df[plot_df[VARIANT_COL].isin(selected_variants)].copy()

        if plot_df.empty:
            continue

        variants = list(plot_df[VARIANT_COL].drop_duplicates())

        has_faddis_runtime = "Mean FADDIS Runtime" in df.columns

        fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.0))

        ax1 = axes[0, 0]
        ax2 = axes[0, 1]
        ax3 = axes[1, 0]
        ax4 = axes[1, 1]

        variant_markers = cycle(["x", "^", "s", "*", "D", "o", "v", "P", ">", "<", "h", "+"])
        variant_colors = {variant: plt.cm.tab20(i % 20) for i, variant in enumerate(variants)}

        for variant in variants:
            d = plot_df[plot_df[VARIANT_COL] == variant].sort_values(variation_parameter)
            marker = next(variant_markers)
            color = variant_colors[variant]

            ax1.plot(
                d[variation_parameter],
                d["Mean ONMI"],
                marker=marker,
                color=color,
                linewidth=1.8,
                markersize=7,
                label=variant,
            )

            ax2.plot(
                d[variation_parameter],
                d["Mean Omega"],
                marker=marker,
                color=color,
                linewidth=1.8,
                markersize=7,
                label=variant,
            )

            ax3.plot(
                d[variation_parameter],
                d["Mean Relative Error |K'-K|/K"],
                marker=marker,
                color=color,
                linewidth=1.8,
                markersize=7,
                label=variant,
            )

            if has_faddis_runtime:
                ax4.plot(
                    d[variation_parameter],
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

            ax.set_xlabel(VARIATION_PARAMETER_LABELS.get(variation_parameter, variation_parameter))
            ax.set_xlim(VARIANT_LIMITS[variation_parameter][0], VARIANT_LIMITS[variation_parameter][1])
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
            os.path.join(results_dir, f"{variation_parameter}_{plot_names[idx]}.pdf"),
            dpi=300,
            bbox_inches="tight",
        )
        fig.savefig(
            os.path.join(results_dir, f"{variation_parameter}_{plot_names[idx]}.png"),
            dpi=300,
            bbox_inches="tight",
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
        ("experience8_cluster", "results_2026-05-02_16-46-53-100982"),

        ("lapin_and_laplacian", "results_2026-06-17_16-17-14-278377"),

        ("affinity_designs", "results_2026-06-17_23-22-22-871630")
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(RESULTS_BASE_DIR, "validation", "bvs", folders[0], folders[1]),
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

        ("lapin_and_laplacian", "results_2026-06-18_16-51-24-027093"),

        ("affinity_designs", "results_2026-06-18_19-56-33-609075")
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(RESULTS_BASE_DIR, "validation", "mvs", folders[0], folders[1]),
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

        ("lapin_and_laplacian", "results_2026-06-19_21-09-49-051769"),

        ("affinity_designs", "results_2026-06-19_23-01-34-957749")
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(RESULTS_BASE_DIR, "validation", "ovs", folders[0], folders[1]),
            variation_parameter=NETWORK_PROPERTY_ON
        )

    # Size variation set.
    for folders in [
        ("experience1_cluster", "results_2026-04-12_20-42-10-997187"),
        ("experience2_cluster", "results_2026-04-13_19-12-06-974844"),
        ("experience3_cluster", "results_2026-04-14_10-15-07-924997"),
        ("experience4_cluster", "results_2026-04-14_17-27-01-073540"),

        # ("faddis_version_a_got", "results_2026-04-20_08-40-19-143228"),
        # ("faddis_version_m", "results_2026-04-26_00-05-03-708303"),
        # ("faddis_version_a_top_10", "results_2026-04-26_08-24-20-677914"),
        # ("faddis_version_a_improved", "results_2026-04-30_00-23-38-440972"),

        # ("faddis_numpy_eigh", "results_2026-05-01_22-11-08-231496"),
        # ("faddis_scipy_eigh_evd", "results_2026-05-01_19-11-52-478180"),
        # ("faddis_scipy_eigh_evr", "results_2026-05-01_16-12-18-640998"),

        ("experience5_cluster", "results_2026-05-03_19-16-46-640640"),
        ("experience6_cluster", "results_2026-05-03_19-52-19-167434"),
        ("experience7_cluster", "results_2026-05-03_20-32-31-224707"),
        ("experience8_cluster", "results_2026-05-03_21-25-59-359439"),
    ]:
        plot_variation_set_results(
            results_dir=os.path.join(RESULTS_BASE_DIR, "validation", "svs", folders[0], folders[1]),
            variation_parameter=NETWORK_PROPERTY_N
        )
