from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_for_non_overlapping_ground_truth import \
    compute_extrinsic_metrics_for_non_overlapping_ground_truth
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_for_overlapping_ground_truth import \
    compute_extrinsic_metrics_for_overlapping_ground_truth


def compute_extrinsic_metrics(graph, ground_truth_labels, predicted_labels, k, k_predicted, overlapping=True):
    """
    Compute extrinsic metrics.

    Parameters:
        graph : (networkx.Graph)
            The graph.
        ground_truth_labels : (list[int], length n) or (list[list[int]], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n) or (list[list[int]], length n)
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
