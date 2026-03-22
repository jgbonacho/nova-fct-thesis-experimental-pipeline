from cdlib import NodeClustering
from cdlib import evaluation as ev

from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics


def compute_extrinsic_metrics_for_overlapping_ground_truth(
        graph,
        ground_truth_labels,
        predicted_labels,
        k,
        k_predicted
):
    """
    Compute extrinsic metrics for overlapping ground-truth.

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

    Returns:
        evaluation_scores : (ExtrinsicMetrics)
            Extrinsic metrics.
    """

    ground_truth_node_clustering = _to_node_clustering(ground_truth_labels, graph, method_name="ground_truth")
    predicted_node_clustering = _to_node_clustering(predicted_labels, graph, method_name="predicted")

    return ExtrinsicMetrics(
        diff_of_k=f"{k_predicted} | {k}",
        relative_error_of_k=abs(k_predicted - k) / k,
        onmi=_compute_onmi(ground_truth_node_clustering, predicted_node_clustering),
        omega=_compute_omega_index(ground_truth_node_clustering, predicted_node_clustering)
    )


def _compute_onmi(ground_truth_node_clustering, predicted_node_clustering):
    """
    Compute the Overlapping Normalized Mutual Information (ONMI) between ground truth and predicted node clusterings.
    ONMI ranges from 0 to 1. The higher, the better.

    Parameters:
        ground_truth_node_clustering : (NodeClustering)
            The ground truth node clustering.
        predicted_node_clustering : (NodeClustering)
            The predicted node clustering.

    Returns:
        onmi_score : (float)
            Overlapping Normalized Mutual Information score.
    """

    return (ev.overlapping_normalized_mutual_information_MGH(ground_truth_node_clustering, predicted_node_clustering)
            .score)


def _compute_omega_index(ground_truth_node_clustering, predicted_node_clustering):
    """
    Compute the Omega Index between ground truth and predicted node clusterings.
    Omega Index ranges from 0 to 1. The higher, the better.

    Parameters:
        ground_truth_node_clustering : (NodeClustering)
            The ground truth node clustering.
        predicted_node_clustering : (NodeClustering)
            The predicted node clustering.

    Returns:
        omega_index_score : (float)
            Omega Index score.
    """

    return ev.omega(ground_truth_node_clustering, predicted_node_clustering).score


def _to_node_clustering(labels, graph, method_name):
    """
    Convert labels to NodeClustering format.

    Parameters:
        labels : (list[list[int]], length n)
            Labels to convert.
        graph : (networkx.Graph)
            The graph.
        method_name : (str)
            The name of the method (e.g., "ground_truth" or "predicted").

    Returns:
        node_clustering : (NodeClustering)
            The NodeClustering object representing the clustering.
    """

    return NodeClustering(
        communities=_build_communities_from_labels(graph, labels),
        graph=graph,
        method_name=method_name,
        overlap=True
    )


def _build_communities_from_labels(graph, labels):
    """
    Build communities from labels.

    Parameters:
        graph : (networkx.Graph)
            The graph.
        labels : (list[list[int]], length n)
            Labels to build communities from.

    Returns:
        communities : (list[list[int]], length k)
            List of communities, where each community is a list of node IDs.
    """
    communities_to_nodes = {}
    for node_id, communities in zip(sorted(graph.nodes()), labels):
        for community in communities:
            communities_to_nodes.setdefault(int(community), []).append(node_id)

    return [communities_to_nodes[community] for community in sorted(communities_to_nodes)]
