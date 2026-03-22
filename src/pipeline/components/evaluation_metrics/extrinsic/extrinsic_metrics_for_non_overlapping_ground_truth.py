"""
Evaluation Metrics - Extrinsic: Compute extrinsic metrics for non-overlapping ground-truth.
"""

import numpy as np
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score, normalized_mutual_info_score, \
    fowlkes_mallows_score, mutual_info_score

from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics


def compute_extrinsic_metrics_for_non_overlapping_ground_truth(
        ground_truth_labels,
        predicted_labels,
        k,
        k_predicted
):
    """
    Compute extrinsic metrics for non-overlapping ground-truth.

    Parameters:
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

    return ExtrinsicMetrics(
        diff_of_k=f"{k_predicted} | {k}",
        relative_error_of_k=abs(k_predicted - k) / k,
        ami=_compute_ami(ground_truth_labels, predicted_labels),
        f_measure=_compute_f_measure(ground_truth_labels, predicted_labels),
        ari=_compute_ari(ground_truth_labels, predicted_labels),
        fmi=_compute_fmi(ground_truth_labels, predicted_labels),
        nmi=_compute_nmi(ground_truth_labels, predicted_labels),
        vi=_compute_vi(ground_truth_labels, predicted_labels),
    )


def _compute_ami(ground_truth_labels, predicted_labels):
    """
    Compute the Adjusted Mutual Information (AMI) between ground truth labels and predicted labels.
    AMI ranges from _ to 1. The higher, the better.

    Parameters:
        ground_truth_labels : (list[int], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n)
            Predicted labels.

    Returns:
        ami_score : (float)
            Adjusted Mutual Information score.
    """

    return adjusted_mutual_info_score(ground_truth_labels, predicted_labels)


def _compute_f_measure(ground_truth_labels, predicted_labels):
    """
    Compute the F-measure between ground truth labels and predicted labels.
    F-measure ranges from 0 to 1. The higher, the better.

    Parameters:
        ground_truth_labels : (list[int], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n)
            Predicted labels.

    Returns:
        f_measure_score : (float)
            F-measure score.
    """

    purity = _compute_purity(predicted_labels, ground_truth_labels)
    inverse_purity = _compute_purity(ground_truth_labels, predicted_labels)
    denominator = purity + inverse_purity

    return ((2.0 * purity * inverse_purity) / denominator) if denominator > 0 else 0.0


def _compute_ari(ground_truth_labels, predicted_labels):
    """
    Compute the Adjusted Rand Index (ARI) between ground truth labels and predicted labels.
    ARI ranges from -0.5 to 1. The higher, the better.

    Parameters:
        ground_truth_labels : (list[int], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n)
            Predicted labels.

    Returns:
        ari_score : (float)
            Adjusted Rand Index score.
    """

    return adjusted_rand_score(ground_truth_labels, predicted_labels)


def _compute_fmi(ground_truth_labels, predicted_labels):
    """
    Compute the Fowlkes-Mallows Index (FMI) between ground truth labels and predicted labels.
    FMI ranges from 0 to 1. The higher, the better.

    Parameters:
        ground_truth_labels : (list[int], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n)
            Predicted labels.

    Returns:
        fmi_score : (float)
            Fowlkes-Mallows Index score.
    """

    return fowlkes_mallows_score(ground_truth_labels, predicted_labels)


def _compute_nmi(ground_truth_labels, predicted_labels):
    """
    Compute the Normalized Mutual Information (NMI) between ground truth labels and predicted labels.
    NMI ranges from 0 to 1. The higher, the better.

    Parameters:
        ground_truth_labels : (list[int], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n)
            Predicted labels.

    Returns:
        nmi_score : (float)
            Normalized Mutual Information score.
    """

    return normalized_mutual_info_score(ground_truth_labels, predicted_labels)


def _compute_vi(ground_truth_labels, predicted_labels):
    """
    Compute the Variation of Information (VI) between ground truth labels and predicted labels.
    VI ranges from 0 to log(n). The lower, the better.

    Parameters:
        ground_truth_labels : (list[int], length n)
            Ground truth labels.
        predicted_labels : (list[int], length n)
            Predicted labels.

    Returns:
        vi_score : (float)
            Variation of Information score.
    """

    ground_truth_labels_entropy = _compute_entropy(ground_truth_labels)
    predicted_labels_entropy = _compute_entropy(predicted_labels)
    mutual_information = mutual_info_score(ground_truth_labels, predicted_labels)

    return predicted_labels_entropy + ground_truth_labels_entropy - (2 * mutual_information)


def _compute_purity(labels_a, labels_b):
    """
    Compute the purity between two partitions of the same set of elements.

    Parameters:
        labels_a : (list[int], length n)
            First partition of the elements.
        labels_b : (list[int], length n)
            Second partition of the elements.

    Returns:
        purity_score : (float)
            Purity score.
    """

    labels_a = np.asarray(labels_a)
    labels_b = np.asarray(labels_b)

    purity_sum = 0
    for label in np.unique(labels_a):
        indices = np.where(labels_a == label)[0]
        _, counts = np.unique(labels_b[indices], return_counts=True)
        purity_sum += counts.max()

    return purity_sum / labels_a.size


def _compute_entropy(labels):
    """
    Compute the entropy of a partition of the elements.

    Parameters:
        labels : (list[int], length n)
            Partition of the elements.

    Returns:
        entropy_score : (float)
            Entropy score.
    """

    _, counts = np.unique(labels, return_counts=True)
    p = counts / counts.sum()

    return -(p * np.log(p)).sum()
