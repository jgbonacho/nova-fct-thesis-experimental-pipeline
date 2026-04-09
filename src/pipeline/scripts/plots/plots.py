import csv
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter

RELATIVE_ERROR_METRIC = "|K'-K|/K"

WARNING_Y0 = 0.20
WARNING_Y1 = 0.25
WARNING_Y2 = 0.30
WARNING_ALPHA = 0.28

NORMALIZED_YMIN = 0.00
NORMALIZED_YMAX = 1.00
NORMALIZED_YTICK_STEP = 0.05

MARKER_SIZE = 45
MARKER_LINEWIDTH = 0.6
LEGEND_MARKER_SIZE = 8


def draw_line_plots_per_network(
        results_dir: str,
        input_filename: str = "_results.csv",
        metrics_to_plot: tuple[str, ...] = (RELATIVE_ERROR_METRIC, "ONMI", "Omega"),
        output_filename: str = "_extrinsic_metrics_plots.pdf",
) -> None:
    """
    Draw a line plot per network.

    Parameters:
        results_dir : (str)
            Path to the results' directory.
        input_filename : (str, optional)
            Name of the input csv file.
            Default is "_results.csv".
        metrics_to_plot : (tuple[str, ...], optional)
            Tuple of metrics to plot.
            Default is "(RELATIVE_ERROR_METRIC, "ONMI", "Omega")"
        output_filename : (str, optional)
            Name of the output pdf file.
            Default is "_extrinsic_metrics_plots.pdf"
    """

    for network_family_dir in _iter_sorted_dirs(results_dir):
        for network_dir in _iter_sorted_dirs(network_family_dir):
            input_path = network_dir / input_filename
            if not input_path.is_file():
                continue

            plot_data = _read_network_results(input_path, metrics_to_plot)
            if not plot_data["variant_names"]:
                continue

            _plot_network_metrics(
                network_dir=network_dir,
                output_filename=output_filename,
                metrics_to_plot=metrics_to_plot,
                variant_names=plot_data["variant_names"],
                results_by_metric=plot_data["results_by_metric"],
                k_prime_values=plot_data["k_prime_values"],
                stop_conditions=plot_data["stop_conditions"],
                k_value=plot_data["k_value"],
            )


def _iter_sorted_dirs(directory: str | Path) -> list[Path]:
    """
    Iterate over sorted directories in a given directory.

    Parameters:
        directory : (str | Path)
            Directory to iterate over.

    Returns:
        list : (list[Path])
            A list of Path objects representing the sorted directories within the given directory.
    """

    return sorted(
        [path for path in Path(directory).iterdir() if path.is_dir()],
        key=lambda path: path.name,
    )


def _read_network_results(input_path: Path, metrics_to_plot: tuple[str, ...]) -> dict:
    """
    Read the results.

    Parameters:
        input_path : (Path)
            Path to the results file.
        metrics_to_plot : (tuple[str, ...])
            The metrics to plot, e.g., ("|K'-K|/K", "ONMI", "Omega").

    Returns:
        dict : (dict)
            Dictionary of results.
    """

    variant_names: list[str] = []
    results_by_metric = {metric: [] for metric in metrics_to_plot}
    k_prime_values: list[str] = []
    stop_conditions: list[str] = []
    k_value: str | None = None

    with input_path.open("r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        for row in reader:
            variant_names.append(_build_variant_name(row))

            for metric in metrics_to_plot:
                results_by_metric[metric].append(float(row[metric]))

            k_prime, k = _parse_k_values(row["K' | K"])
            k_prime_values.append(k_prime)
            stop_conditions.append(row["Stop condition"].strip())

            if k_value is None:
                k_value = k

    return {
        "variant_names": variant_names,
        "results_by_metric": results_by_metric,
        "k_prime_values": k_prime_values,
        "stop_conditions": stop_conditions,
        "k_value": k_value,
    }


def _parse_k_values(k_pair: str) -> tuple[str, str]:
    """
    Parse K' and K values from a string in the format "K' | K".

    Parameters:
        k_pair : (str)
            A string containing K' and K values separated by a pipe character, e.g., "5 | 4".

    Returns:
        tuple : (tuple[str, str])
            A tuple containing the K' value and the K value as strings, with leading/trailing whitespace removed.
    """

    k_prime, k = k_pair.strip().split("|")
    return k_prime.strip(), k.strip()


def _plot_network_metrics(
        network_dir: Path,
        output_filename: str,
        metrics_to_plot: tuple[str, ...],
        variant_names: list[str],
        results_by_metric: dict[str, list[float]],
        k_prime_values: list[str],
        stop_conditions: list[str],
        k_value: str,
) -> None:
    """
    Plot network metrics plots.

    Parameters:
        network_dir : (Path)
            The directory of the network for which to plot the metrics.
        output_filename : (str)
            The filename for the output plot PDF.
        metrics_to_plot : (tuple[str, ...])
            The metrics to plot, e.g., ("|K'-K|/K", "ONMI", "Omega").
        variant_names : (list[str])
            The list of variant names corresponding to the results.
        results_by_metric : (dict[str, list[float]])
            A dictionary mapping each metric to a list of its values for each variant.
        k_prime_values : (list[str])
            The list of K' values corresponding to each variant, used for annotation.
        stop_conditions : (list[str])
            The list of stop conditions corresponding to each variant, used for marker styling.
        k_value : (str | None)
            The K value corresponding to the variants, used for annotation in the relative error plot.
    """

    x = np.arange(len(variant_names))
    fig, axes = plt.subplots(
        nrows=len(metrics_to_plot),
        ncols=1,
        figsize=(18, 4.5 * len(metrics_to_plot)),
        sharex=True,
    )

    if len(metrics_to_plot) == 1:
        axes = [axes]

    stop_handles = _build_stop_condition_legend_handles(stop_conditions)

    for ax, metric in zip(axes, metrics_to_plot):
        y = np.array(results_by_metric[metric], dtype=float)

        ax.plot(x, y, zorder=2)
        _plot_stop_condition_markers(ax, x, y, stop_conditions)
        _configure_metric_axis(ax, metric, y, len(variant_names))

        if metric == RELATIVE_ERROR_METRIC:
            _annotate_k_prime(ax, x, y, k_prime_values)
            k_handle = Line2D([], [], linestyle="none", marker=None, label=f"K={k_value}")
            ax.legend(handles=stop_handles + [k_handle], loc="upper right")
        else:
            ax.legend(handles=stop_handles, loc="upper right")

        ax.set_ylabel(metric)
        ax.grid(True, alpha=0.3, zorder=1)

    axes[-1].set_xlabel("Variant")
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(variant_names, rotation=45, ha="right", fontsize=9)

    fig.tight_layout()
    fig.savefig(network_dir / output_filename, dpi=300)
    plt.close(fig)


def _configure_metric_axis(ax: Axes, metric: str, y: np.ndarray, x_count: int) -> None:
    """
    Configure axis labels and tick labels.

    Parameters:
        ax : (matplotlib.axes.Axes)
            Axes to configure.
        metric : (str)
            The metric being plotted, used to determine axis limits and formatting.
        y : (np.ndarray)
            The y values of the metric, used to determine axis limits.
        x_count : (int)
            The number of x-axis points, used for configuring the warning gradient if applicable.
    """

    if metric == RELATIVE_ERROR_METRIC:
        ax.set_ylim(0.0, max(WARNING_Y2, np.nanmax(y) + 0.02))
        _add_warning_gradient(
            ax,
            x_count=x_count,
            y0=WARNING_Y0,
            y1=WARNING_Y1,
            y2=WARNING_Y2,
            alpha=WARNING_ALPHA,
        )
    else:
        ax.set_ylim(NORMALIZED_YMIN, NORMALIZED_YMAX)
        ax.set_yticks(np.arange(NORMALIZED_YMIN, NORMALIZED_YMAX + 0.001, NORMALIZED_YTICK_STEP))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))


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

    variant_id = row["ID"]
    affinity_design = row["Affinity Design"].strip().lower()
    execution_mode = row["Execution Mode"].strip().lower()
    laplacian = row["Laplacian"].strip().lower()
    gamma = f"g{int(round(float(row['Gamma']) * 10)):02d}"
    c0_rule = "cdropC0" if row["Conditionally discard C0?"].strip() == "Yes" else "keepC0"

    return f"{variant_id}_{affinity_design}_{execution_mode}_{laplacian}_{gamma}_{c0_rule}"


def _annotate_k_prime(ax: Axes, x: np.ndarray, y: np.ndarray, k_prime_values: list[str]) -> None:
    """
    Annotate `y` with `k_prime_values`.

    Parameters
        ax : (matplotlib.axes.Axes)
            Axes to annotate.
        x : (np.ndarray)
            Array of x values.
        y : (np.ndarray)
            Array of y values.
        k_prime_values : (list[str])
            List of K' values to annotate at each (x, y) point.
    """

    for xi, yi, k_prime in zip(x, y, k_prime_values):
        ax.annotate(
            f"K'={k_prime}",
            xy=(xi, yi),
            xytext=(0, -10),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=8,
            zorder=4,
        )


def _stop_condition_marker(stop_condition: str) -> str:
    """
    Define a stop condition marker.

    Parameters
        stop_condition : (str)
            The stop condition to determine the marker for.

    Returns
        style : (str)
            A string representing the marker style for the given stop condition.
    """

    marker_map = {
        "w": "^",
        "epsilon": "s",
        "tau": "D",
        "kmax": "v",
    }

    return marker_map.get(stop_condition.strip().lower(), "o")


def _stop_condition_style() -> dict[str, str]:
    """
    Defines the style of the stop condition marker.

    Returns:
        dict : (dict[str, str])
            A dictionary containing the facecolor and edgecolor for the stop condition marker.
    """

    return {
        "facecolor": "grey",
        "edgecolor": "grey",
    }


def _unique_in_order(values: list[str]) -> list[str]:
    """
    Get unique values in order of first occurrence, ignoring leading/trailing whitespace.

    Parameters:
        values: (list[str])
            The list of values to check.

    Returns:
        list : (list[str])
            A list of unique values in the order they first appear, with leading/trailing whitespace removed.
    """

    unique_values: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized not in unique_values:
            unique_values.append(normalized)
    return unique_values


def _plot_stop_condition_markers(ax: Axes, x: np.ndarray, y: np.ndarray, stop_conditions: list[str]) -> None:
    """
    Plot stop condition markers.

    Parameters:
        ax : (matplotlib.axes.Axes)
            The axes on which to plot the markers.
        x: (np.ndarray)
            The x-coordinates of the points.
        y: (np.ndarray)
            The y-coordinates of the points.
        stop_conditions: (list[str])
            The list of stop conditions corresponding to each point.
    """

    for condition in _unique_in_order(stop_conditions):
        idx = [i for i, stop_condition in enumerate(stop_conditions) if stop_condition.strip() == condition]
        style = _stop_condition_style()

        ax.scatter(
            x[idx],
            y[idx],
            s=MARKER_SIZE,
            marker=_stop_condition_marker(condition),
            facecolors=style["facecolor"],
            edgecolors=style["edgecolor"],
            linewidths=MARKER_LINEWIDTH,
            zorder=3,
        )


def _build_stop_condition_legend_handles(stop_conditions: list[str]) -> list[Line2D]:
    """
    Build a stop condition legend handle.

    Parameters:
        stop_conditions: (list[str])
            A list of stop conditions.

    Returns:
        list : (list[Line2D])
            A list of Line2D objects to be used as legend handles for the stop conditions.
    """

    handles: list[Line2D] = []

    for stop_condition in _unique_in_order(stop_conditions):
        style = _stop_condition_style()
        handles.append(
            Line2D(
                [],
                [],
                linestyle="none",
                marker=_stop_condition_marker(stop_condition),
                markersize=LEGEND_MARKER_SIZE,
                markerfacecolor=style["facecolor"],
                markeredgecolor=style["edgecolor"],
                label=f"Stop Condiction: {stop_condition}",
            )
        )

    return handles


def _add_warning_gradient(ax: Axes, x_count: int, y0: float, y1: float, y2: float, alpha: float) -> None:
    """
    Add a warning gradient to the plot.

    Parameters:
        ax : (matplotlib.axes.Axes)
            The axes to which the gradient will be added.
        x_count : (int)
            The number of x-axis points.
        y0 : (float)
            The y-value where the gradient starts (yellow).
        y1 : (float)
            The y-value where the gradient transitions to orange.
        y2 : (float)
            The y-value where the gradient transitions to red.
        alpha : (float)
            The transparency of the gradient (0.0 to 1.0).
    """

    y_min, y_max = ax.get_ylim()
    y_max = max(y_max, y2)
    ax.set_ylim(y_min, y_max)

    cmap = LinearSegmentedColormap.from_list(
        "warning_gradient",
        [(0.0, "yellow"), ((y1 - y0) / (y2 - y0), "orange"), (1.0, "red")],
    )

    n = 512
    y = np.linspace(y0, y_max, n)
    t = (y - y0) / (y2 - y0)
    t = np.clip(t, 0, 1).reshape(-1, 1)

    ax.imshow(
        t,
        aspect="auto",
        cmap=cmap,
        origin="lower",
        extent=[-0.5, x_count - 0.5, y0, y_max],
        alpha=alpha,
        zorder=0,
    )


# ---------------------------------------------------------------------------------------------------------------------


SAMPLE_TRACE_ALPHA = 0.20
SAMPLE_TRACE_LINEWIDTH = 1.0
MEAN_LINEWIDTH = 2.0
MEAN_ERRORBAR_CAPSIZE = 4
MEAN_ERRORBAR_LINEWIDTH = 1.2
MEAN_COLOR = "tab:blue"


def draw_line_plots_per_network_family(
        results_dir: str,
        input_filename: str = "_results.csv",
        metrics_to_plot: tuple[str, ...] = (RELATIVE_ERROR_METRIC, "ONMI", "Omega"),
        output_filename: str = "_family_extrinsic_metrics_plots.pdf",
) -> None:
    """
    Draw a line plot per network family, showing the mean and sample standard deviation across networks in the family.
    
    Parameters:
        results_dir : (str)
            Path to the results' directory.
        input_filename : (str, optional)
            Name of the input CSV file containing the results. Default is "_results.csv".
        metrics_to_plot : (tuple[str, ...], optional)
            Metrics to be plotted. Default is (RELATIVE_ERROR_METRIC, "ONMI", "Omega").
        output_filename : (str, optional)
            Name of the output PDF file for the plots. Default is "_family_extrinsic_metrics_plots.pdf".
    """

    for network_family_dir in _iter_sorted_dirs(results_dir):
        family_data = _read_family_results(network_family_dir, input_filename, metrics_to_plot)
        if not family_data["variant_names"]:
            continue

        _plot_family_metrics(
            network_family_dir=network_family_dir,
            output_filename=output_filename,
            metrics_to_plot=metrics_to_plot,
            variant_names=family_data["variant_names"],
            network_series=family_data["network_series"],
        )


def _read_family_results(
        network_family_dir: Path,
        input_filename: str,
        metrics_to_plot: tuple[str, ...],
) -> dict:
    """
    Read the results for a network family.

    Parameters:
        network_family_dir : (Path)
            Path to the network family directory.
        input_filename : (str)
            Name of the input CSV file containing the results.
        metrics_to_plot : (tuple[str, ...])
            Metrics to be plotted.

    Returns:
        dict : (dict)
            A dictionary containing the variant names and network series data.
    """

    variant_names: list[str] = []
    network_series: list[dict] = []

    for network_dir in _iter_sorted_dirs(network_family_dir):
        input_path = network_dir / input_filename
        if not input_path.is_file():
            continue

        values_by_metric = {metric: {} for metric in metrics_to_plot}

        with input_path.open("r", newline="", encoding="utf-8") as in_file:
            reader = csv.DictReader(in_file)
            for row in reader:
                variant_name = _build_variant_name(row)

                if variant_name not in variant_names:
                    variant_names.append(variant_name)

                for metric in metrics_to_plot:
                    values_by_metric[metric][variant_name] = float(row[metric])

        network_series.append(
            {
                "network_name": network_dir.name,
                "values_by_metric": values_by_metric,
            }
        )

    return {
        "variant_names": variant_names,
        "network_series": network_series,
    }


def _plot_family_metrics(
        network_family_dir: Path,
        output_filename: str,
        metrics_to_plot: tuple[str, ...],
        variant_names: list[str],
        network_series: list[dict],
) -> None:
    """
    Plot the family metrics with mean and sample standard deviation across networks in the family.
    
    Parameters:
        network_family_dir : (Path)
            The directory of the network family for which to plot the metrics.
        output_filename : (str)
            The filename for the output plot PDF.
        metrics_to_plot : (tuple[str, ...])
            The metrics to plot, e.g., ("|K'-K|/K", "ONMI", "Omega").
        variant_names : (list[str])
            The list of variant names corresponding to the results.
        network_series : (list[dict])
            A list of dictionaries, each containing the network name and a dictionary of metric values by variant for that network.
    """

    x = np.arange(len(variant_names))
    fig, axes = plt.subplots(
        nrows=len(metrics_to_plot),
        ncols=1,
        figsize=(18, 4.5 * len(metrics_to_plot)),
        sharex=True,
    )

    if len(metrics_to_plot) == 1:
        axes = [axes]

    for ax, metric in zip(axes, metrics_to_plot):
        metric_matrix = []

        for series in network_series:
            y = np.array(
                [
                    series["values_by_metric"][metric].get(variant_name, np.nan)
                    for variant_name in variant_names
                ],
                dtype=float,
            )

            metric_matrix.append(y)

            ax.plot(
                x,
                y,
                linewidth=SAMPLE_TRACE_LINEWIDTH,
                alpha=SAMPLE_TRACE_ALPHA,
                zorder=2,
            )

        metric_matrix = np.array(metric_matrix, dtype=float)
        mean_y = np.nanmean(metric_matrix, axis=0)
        std_y = _sample_nanstd(metric_matrix, axis=0)

        ax.errorbar(
            x,
            mean_y,
            yerr=std_y,
            fmt="-",
            color=MEAN_COLOR,
            ecolor=MEAN_COLOR,
            linewidth=MEAN_LINEWIDTH,
            capsize=MEAN_ERRORBAR_CAPSIZE,
            elinewidth=MEAN_ERRORBAR_LINEWIDTH,
            zorder=4,
            label="mean ± sample std",
        )

        _configure_metric_axis(ax, metric, mean_y, len(variant_names))

        ax.legend(loc="upper right")
        ax.set_ylabel(metric)
        ax.grid(True, alpha=0.3, zorder=1)

    axes[-1].set_xlabel("Variant")
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(variant_names, rotation=45, ha="right", fontsize=9)

    fig.tight_layout()
    fig.savefig(network_family_dir / output_filename, dpi=300)
    plt.close(fig)


def _sample_nanstd(values: np.ndarray, axis: int = 0) -> np.ndarray | float:
    """
    Calculate the sample standard deviation of an array while ignoring NaN values, and return 0.0 for cases with 1 or fewer valid (non-NaN) values along the specified axis.

    Parameters:
        values : (np.ndarray)
            The input array containing the values for which to calculate the sample standard deviation.
        axis : (int, optional)
            The axis along which to calculate the standard deviation. 
            Default is 0.
    
    Returns:
        result : (np.ndarray | float)
            The sample standard deviation of the input values along the specified axis, ignoring NaN values.
    """

    values = np.asarray(values, dtype=float)
    valid_count = np.sum(~np.isnan(values), axis=axis)

    std = np.nanstd(values, axis=axis, ddof=1)

    if np.isscalar(std):
        return 0.0 if valid_count <= 1 else std

    return np.where(valid_count <= 1, 0.0, std)


# ---------------------------------------------------------------------------------------------------------------------


GLOBAL_MEAN_MARKER = "o"


def draw_global_line_plots_per_network_family(
        results_dir: str,
        input_filename: str = "_results.csv",
        metrics_to_plot: tuple[str, ...] = (RELATIVE_ERROR_METRIC, "ONMI", "Omega"),
        output_filename: str = "_global_family_extrinsic_metrics_plots.pdf",
) -> None:
    """
    Draw a global line plot per network family, showing the mean across networks in the family for each variant, with all variants aligned on the x-axis.

    Parameters:
        results_dir : (str)
            Path to the results' directory.
        input_filename : (str, optional)
            Name of the input CSV file containing the results. 
            Default is "_results.csv".
        metrics_to_plot : (tuple[str, ...], optional)
            Metrics to be plotted. 
            Default is (RELATIVE_ERROR_METRIC, "ONMI", "Omega").
        output_filename : (str, optional)
            Name of the output PDF file for the plots. 
            Default is "_global_family_extrinsic_metrics_plots.pdf".
    """

    family_data_list: list[dict] = []
    global_variant_names: list[str] = []

    for network_family_dir in _iter_sorted_dirs(results_dir):
        family_data = _read_family_results(network_family_dir, input_filename, metrics_to_plot)
        if not family_data["variant_names"]:
            continue

        for variant_name in family_data["variant_names"]:
            if variant_name not in global_variant_names:
                global_variant_names.append(variant_name)

        family_data_list.append(
            {
                "family_name": network_family_dir.name,
                "network_series": family_data["network_series"],
            }
        )

    if not family_data_list:
        return

    x = np.arange(len(global_variant_names))
    fig, axes = plt.subplots(
        nrows=len(metrics_to_plot),
        ncols=1,
        figsize=(18, 4.5 * len(metrics_to_plot)),
        sharex=True,
    )

    if len(metrics_to_plot) == 1:
        axes = [axes]

    colors = plt.get_cmap("tab20")(np.linspace(0, 1, len(family_data_list)))
    for ax, metric in zip(axes, metrics_to_plot):
        plotted_mean_values = []

        for i, family_data in enumerate(family_data_list):
            color = colors[i]
            metric_matrix = []

            for series in family_data["network_series"]:
                y = np.array(
                    [
                        series["values_by_metric"][metric].get(variant_name, np.nan)
                        for variant_name in global_variant_names
                    ],
                    dtype=float,
                )
                metric_matrix.append(y)

            metric_matrix = np.array(metric_matrix, dtype=float)
            mean_y = np.nanmean(metric_matrix, axis=0)
            # std_y = _sample_nanstd(metric_matrix, axis=0)

            plotted_mean_values.append(mean_y)

            # ax.errorbar(
            #    x,
            #    mean_y,
            #    yerr=std_y,
            #    fmt=f"-{GLOBAL_MEAN_MARKER}",
            #    color=color,
            #    ecolor=color,
            #    linewidth=MEAN_LINEWIDTH,
            #    capsize=MEAN_ERRORBAR_CAPSIZE,
            #    elinewidth=MEAN_ERRORBAR_LINEWIDTH,
            #    zorder=3,
            #    label=family_data["family_name"],
            # )

            ax.plot(
                x,
                mean_y,
                f"-{GLOBAL_MEAN_MARKER}",
                color=color,
                linewidth=MEAN_LINEWIDTH,
                zorder=3,
                label=family_data["family_name"],
            )

        if plotted_mean_values:
            all_means = np.concatenate(plotted_mean_values)
        else:
            all_means = np.array([], dtype=float)

        _configure_metric_axis(ax, metric, all_means, len(global_variant_names))

        ax.set_ylabel(metric)
        ax.grid(True, alpha=0.3, zorder=1)
        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.01, 1.0),
            borderaxespad=0.0,
            fontsize=9,
        )

    axes[-1].set_xlabel("Variant")
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(global_variant_names, rotation=45, ha="right", fontsize=9)

    fig.tight_layout()
    fig.savefig(Path(results_dir) / output_filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
