import numpy as np
import skfuzzy as fuzz


def njw_fcm(
        W: np.ndarray,
        k: int,
        fcm_m: float,
        fcm_error: float,
        fcm_max_iter: int,
        fcm_seed: int
) -> np.ndarray:
    """
    Compute the NJW spectral clustering followed by Fuzzy C-Means.

    Parameters:
        W : (np.ndarray, shape[n,n])
            nxn symmetric similarity/affinity matrix.
        k : (int)
            Number of clusters.
        fcm_m : (float)
            Fuzzifier parameter of Fuzzy C-Means.
        fcm_error : (float)
            Convergence tolerance of Fuzzy C-Means.
        fcm_max_iter : (int)
            Maximum number of Fuzzy C-Means iterations.
        fcm_seed : (int)
            Random seed of Fuzzy C-Means.

    Returns:
        U : (np.ndarray, shape[n,k])
            Fuzzy membership matrix.
    """

    # Compute NJW spectral clustering.
    D = np.diag(W.sum(axis=1))
    D_inv_sqrt = np.diag(1.0 / np.sqrt(D.diagonal()))
    L = D_inv_sqrt @ W @ D_inv_sqrt

    eigenvalues, eigenvectors = np.linalg.eigh(L)

    X_norm = np.linalg.norm(eigenvectors[:, -k:], axis=1, keepdims=True)
    X_norm[X_norm == 0] = 1
    X = eigenvectors[:, -k:] / X_norm

    # Compute Fuzzy C-Means.
    _, U, _, _, _, _, _ = fuzz.cluster.cmeans(
        data=X.T,
        c=k,
        m=fcm_m,
        error=fcm_error,
        maxiter=fcm_max_iter,
        seed=fcm_seed
    )

    return U.T


def apply_njw_fcm_defuzzification_rule(U: np.ndarray, fi: float, overlapping: bool = True) -> tuple[list, int]:
    """
    Apply a defuzzification rule to map NJW+FCM fuzzy memberships to a binary [overlapping] community cover.

    Parameters:
        U : (np.ndarray, shape[n,k])
            Fuzzy memberships per node per community.
        fi : (float, optional)
            Fixed membership threshold used for overlapping community assignment.
            If no membership reaches the threshold, assign the node to the community with maximum membership.
        overlapping : (bool, optional)
            If True, apply fixed membership thresholding with maximum-membership fallback.
            If False, apply maximum-membership assignment.
            Default is True.

    Returns:
        predicted_labels : (list[list[int]], length n | list[int], length n)
            Predicted labels for each node.
        k_predicted : (int)
            Number of predicted communities.

     Exceptions:
        ValueError : If the membership threshold is not in the range [0, 1] when overlapping is True.
    """

    if not overlapping:
        # Maximum-membership assignment.
        predicted_labels = np.argmax(U, axis=1).tolist()
        k_predicted = len(set(predicted_labels))

        return predicted_labels, k_predicted
    else:
        if not 0.0 <= fi <= 1.0:
            raise ValueError("[ERROR] The membership threshold must be in the range [0, 1].")

        # Fixed membership thresholding with maximum-membership fallback.
        predicted_labels = []
        for node_memberships in U:
            node_labels = np.flatnonzero(node_memberships >= fi).tolist()
            if not node_labels:
                node_labels = [int(np.argmax(node_memberships))]
            predicted_labels.append(node_labels)
        k_predicted = len({label for node_labels in predicted_labels for label in node_labels})

        return predicted_labels, k_predicted
