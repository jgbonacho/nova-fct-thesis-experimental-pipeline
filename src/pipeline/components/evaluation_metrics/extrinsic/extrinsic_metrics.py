import networkx as nx
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_for_non_overlapping_ground_truth import \
    compute_extrinsic_metrics_for_non_overlapping_ground_truth
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_for_overlapping_ground_truth import \
    compute_extrinsic_metrics_for_overlapping_ground_truth


def compute_extrinsic_metrics(
        graph: nx.Graph,
        ground_truth_labels: list,
        predicted_labels: list,
        k: int,
        k_predicted: int,
        overlapping: bool = True
) -> ExtrinsicMetrics:
    """
    Compute extrinsic metrics.

    Parameters:
        graph : (nx.Graph)
            The graph.
        ground_truth_labels : (list[int], length n | list[list[int]], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n | list[list[int]], length n)
            Predicted labels.
        k : (int)
            The number of communities in the ground truth.
        k_predicted : (int)
            The number of communities predicted.
        overlapping : (bool, optional)
            Whether the ground truth is overlapping.
            Default is True.

    Returns:
        evaluation_scores : (ExtrinsicMetrics)
            Extrinsic metrics.
    """

    if not overlapping:
        evaluation_scores = compute_extrinsic_metrics_for_non_overlapping_ground_truth(
            ground_truth_labels,
            predicted_labels,
            k,
            k_predicted
        )
    else:
        evaluation_scores = compute_extrinsic_metrics_for_overlapping_ground_truth(
            graph,
            ground_truth_labels,
            predicted_labels,
            k,
            k_predicted
        )

    return evaluation_scores
