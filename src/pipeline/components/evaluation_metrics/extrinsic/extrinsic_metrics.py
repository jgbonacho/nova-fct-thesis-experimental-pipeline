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

    Nodes without community labels are removed from both the ground-truth labels and the predicted labels before computing the metrics.

    Parameters:
        graph : (nx.Graph)
            The graph.
        ground_truth_labels : (list[int], length n | list[list[int]], length n)
            Ground-truth labels.
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

    filtered_graph, filtered_ground_truth_labels, filtered_predicted_labels, k, filtered_k_predicted = _remove_nodes_without_community_labels(
        graph,
        ground_truth_labels,
        predicted_labels,
        k,
        k_predicted,
        overlapping
    )

    if not overlapping:
        evaluation_scores = compute_extrinsic_metrics_for_non_overlapping_ground_truth(
            filtered_ground_truth_labels,
            filtered_predicted_labels,
            k,
            k_predicted
        )
    else:
        evaluation_scores = compute_extrinsic_metrics_for_overlapping_ground_truth(
            filtered_graph,
            filtered_ground_truth_labels,
            filtered_predicted_labels,
            k,
            k_predicted
        )

    return evaluation_scores


def _remove_nodes_without_community_labels(
        graph: nx.Graph,
        ground_truth_labels: list,
        predicted_labels: list,
        k: int,
        k_predicted: int,
        overlapping: bool
) -> tuple[nx.Graph, list, list, int, int]:
    """
    Remove nodes without community labels from the graph, ground-truth labels, and predicted labels.

    Parameters:
        graph : (nx.Graph)
            The graph.
        ground_truth_labels : (list[int] | list[list[int]])
            Ground-truth labels.
        predicted_labels : (list[int] | list[list[int]])
            Predicted labels.
        k : (int)
            The number of communities in the ground truth.
        k_predicted : (int)
            The number of communities predicted.
        overlapping : (bool)
            Whether the ground truth is overlapping.

    Returns:
        graph : (nx.Graph)
            Filtered graph.
        ground_truth_labels : (list[int] | list[list[int]])
            Filtered ground-truth labels.
        predicted_labels : (list[int] | list[list[int]])
            Filtered predicted labels.
        k : (int)
            Number of communities in the filtered ground truth.
        k_predicted : (int)
            Number of communities in the filtered predicted labels.
    """

    if len(ground_truth_labels) != len(predicted_labels):
        raise ValueError("[ERROR] Ground-truth labels and predicted labels must have the same length.")

    if len(ground_truth_labels) != graph.number_of_nodes():
        raise ValueError(f"[ERROR] Number of labels must match the number of graph nodes.")

    graph_nodes = sorted(graph.nodes())

    valid_indices = [
        idx
        for idx, ground_truth_label in enumerate(ground_truth_labels)
        if _has_ground_truth_label(ground_truth_label, overlapping)
    ]

    if len(valid_indices) == 0:
        raise ValueError("[ERROR] There are no nodes with community labels.")

    if len(valid_indices) == len(ground_truth_labels):
        print(f"[DEBUG] Original Labels = ({len(ground_truth_labels)}, {len(predicted_labels)})")
        return graph, ground_truth_labels, predicted_labels, k, k_predicted

    filtered_graph = graph.subgraph([graph_nodes[idx] for idx in valid_indices]).copy()
    filtered_ground_truth_labels = [ground_truth_labels[idx] for idx in valid_indices]
    filtered_predicted_labels = [predicted_labels[idx] for idx in valid_indices]

    filtered_k_predicted = _count_communities(filtered_predicted_labels, overlapping)

    print(f"[DEBUG] Reduced Labels = ({len(filtered_ground_truth_labels)}, {len(filtered_predicted_labels)})")

    return filtered_graph, filtered_ground_truth_labels, filtered_predicted_labels, k, filtered_k_predicted


def _has_ground_truth_label(label, overlapping: bool) -> bool:
    """
    Check whether a node has a valid community label (!= -1 or != [-1]).

    Parameters:
        label : (int | list[int])
            Ground-truth label or labels of a node.
        overlapping : (bool)
            Whether the ground truth is overlapping.

    Returns:
        has_label : (bool)
            True if the node has at least one valid ground-truth label.
    """

    return label != -1 if not overlapping else any(community != -1 for community in label)


def _count_communities(labels: list, overlapping: bool) -> int:
    """
    Count the number of valid communities in a label list.

    Parameters:
        labels : (list[int] | list[list[int]])
            Labels.
        overlapping : (bool)
            Whether the labels are overlapping.

    Returns:
        k : (int)
            Number of valid communities.
    """

    if not overlapping:
        return len({label for label in labels})
    else:
        return len({community for node_labels in labels for community in node_labels})
