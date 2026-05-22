import numpy as np


def apply_defuzzification_rule(
        U: np.ndarray,
        gamma: float = 0.5,
        conditionally_discard_first_cluster: bool = True,
        overlapping: bool = True
) -> tuple[list, int, bool]:
    """
    Apply a defuzzification rule to map fuzzy memberships to a binary [overlapping] community cover.

    Parameters:
        U : (np.ndarray, shape[n,k])
            Fuzzy memberships per node per community.
        gamma : (float, optional)
            Hyperparameter for the defuzzification rule.
            Default is 0.5.
        conditionally_discard_first_cluster : (bool, optional)
            If True, discard the first cluster if all membership values in the first column are positive.
            If False, include all clusters in the defuzzification process.
            Default is True.
        overlapping : (bool, optional)
            If True, apply node-wise alpha-cut thresholding.
            If False, apply maximum membership assignment.
            Default is True.

    Returns:
        predicted_labels : (list[list[int]], length n | list[int], length n)
            List of predicted labels for each node.
        k_predicted : (int)
            Number of predicted communities.
        first_cluster_discarded : (bool)
            Whether the first cluster was discarded.

    Exceptions:
        ValueError : If gamma is not in the range [0, 1], when overlapping is True.
    """

    if conditionally_discard_first_cluster and np.all(U[:, 0] > 0) and U.shape[1] > 1:
        U_copy = np.asarray(U)[:, 1:]
        first_cluster_discarded = True
        labels_offset = 1
        # print("[INFO] Defuzzification discarding the first extracted cluster.")
    else:
        U_copy = np.asarray(U)
        first_cluster_discarded = False
        labels_offset = 0
        # print("[INFO] Defuzzification including the first extracted cluster.")

    if not overlapping:
        # Maximum membership assignment.
        predicted_labels = np.argmax(U_copy, axis=1) + labels_offset
        predicted_labels = predicted_labels.tolist()
        k_predicted = len(set(predicted_labels))
        return predicted_labels, k_predicted, first_cluster_discarded
    else:
        if not (0.0 <= gamma <= 1.0):
            raise ValueError("[ERROR] Gamma must be in the range [0, 1].")

        # Node-wise alpha-cut thresholding.
        max_membership_per_node = np.max(U_copy, axis=1, keepdims=True)
        threshold_per_node = gamma * max_membership_per_node
        B = (U_copy >= threshold_per_node).astype(int)
        predicted_labels = [list(np.flatnonzero(B[i]) + labels_offset) for i in range(B.shape[0])]
        k_predicted = len({label for labels in predicted_labels for label in labels})
        return predicted_labels, k_predicted, first_cluster_discarded
