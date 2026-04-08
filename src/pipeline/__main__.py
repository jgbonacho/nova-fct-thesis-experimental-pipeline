"""
Entry point.
"""

from pipeline.config.config import SYNTHETIC_NETWORKS_BASE_DIR, CONFIG_DIR, RESULTS_BASE_DIR, load_network_families, \
    load_thresholds, AFFINITY_DESIGNS, EXECUTION_MODES, DEFUZZIFICATION_RULES
from pipeline.scripts.plots.plots import draw_line_plots_per_network, draw_line_plots_per_network_family, \
    draw_global_line_plots_per_network_family
from pipeline.scripts.synthetic_networks_runner import run_synthetic_networks_experiments


def main():
    results_path = run_synthetic_networks_experiments(
        networks_base_dir=SYNTHETIC_NETWORKS_BASE_DIR,
        results_base_dir=RESULTS_BASE_DIR,
        network_families=load_network_families(CONFIG_DIR),
        thresholds=load_thresholds(CONFIG_DIR),
        affinity_designs=AFFINITY_DESIGNS,
        execution_modes=EXECUTION_MODES,
        defuzzification_rules=DEFUZZIFICATION_RULES
    )

    draw_line_plots_per_network(results_dir=results_path)
    draw_line_plots_per_network_family(results_dir=results_path)
    draw_global_line_plots_per_network_family(results_dir=results_path)

    # import os

    # Experience 1
    # results_path = os.path.join(RESULTS_BASE_DIR, "experience1_cluster", "results_2026-04-04_18-01-39-080614")
    # draw_line_plots_per_network(results_dir=results_path)
    # draw_line_plots_per_network_family(results_dir=results_path)
    # draw_global_line_plots_per_network_family(results_dir=results_path)

    # Experience 2
    # results_path = os.path.join(RESULTS_BASE_DIR, "experience2_cluster", "results_2026-04-05_09-07-19-011166")
    # draw_line_plots_per_network(results_dir=results_path)
    # draw_line_plots_per_network_family(results_dir=results_path)
    # draw_global_line_plots_per_network_family(results_dir=results_path)

    # Experience 3
    # results_path = os.path.join(RESULTS_BASE_DIR, "experience3_cluster", "results_2026-04-06_22-28-25-819274")
    # draw_line_plots_per_network(results_dir=results_path)
    # draw_line_plots_per_network_family(results_dir=results_path)
    # draw_global_line_plots_per_network_family(results_dir=results_path)

    # Experience 4
    # results_path = os.path.join(RESULTS_BASE_DIR, "experience4_cluster", "results_2026-04-07_07-18-02-169177")
    # draw_line_plots_per_network(results_dir=results_path)
    # draw_line_plots_per_network_family(results_dir=results_path)
    # draw_global_line_plots_per_network_family(results_dir=results_path)

    # Experience 5_1
    # results_path = os.path.join(RESULTS_BASE_DIR, "experience5_cluster", "results_2026-04-07_13-30-38-630965")
    # draw_line_plots_per_network(results_dir=results_path)
    # draw_line_plots_per_network_family(results_dir=results_path)
    # draw_global_line_plots_per_network_family(results_dir=results_path)

    # Experience 5_2
    # results_path = os.path.join(RESULTS_BASE_DIR, "experience5_cluster", "results_2026-04-07_18-15-06-081553")
    # draw_line_plots_per_network(results_dir=results_path)
    # draw_line_plots_per_network_family(results_dir=results_path)
    # draw_global_line_plots_per_network_family(results_dir=results_path)


if __name__ == "__main__":
    main()
