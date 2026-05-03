"""
Implementation based on https://github.com/dmitsf/GOT/blob/master/got/relevance_analysis/faddis.py
"""

import numpy as np
import numpy.linalg as LA

# from scipy.linalg import eigh

# A small value to determine if a number is considered to be zero.
ZERO_BOUND = 10 ** (-9)


def faddis(
        W: np.ndarray,
        epsilon: float = None,
        tau: float = None,
        k_max: int = None,
        desired_k: int = None
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, str]:
    """
    FADDIS: Fuzzy Additive Spectral clustering.
    Stop criterion is ('epsilon', 'tau', 'k_max') or 'desired_k'.

    Parameters:
        W : (np.ndarray, shape[n,n])
            nxn symmetric similarity/affinity matrix.
        epsilon : (float | None)
            Threshold of the individual cluster contribution.
        tau : (float | None)
            Threshold of the total clusters contribution.
        k_max : (int | None)
            Maximum number of clusters.
        desired_k : (int | None)
            Number of clusters to extract.
            If not None, it is used as the stop criterion instead of 'epsilon', 'tau' and 'k_max'.

    Returns:
        membership_matrix : (np.ndarray)
            nxK membership matrix of clustering.
        contributions : (np.ndarray)
            1xK vector of relative contributions to the data scatter.
        intensities : (np.ndarray)
            Kx2 matrix of weights (cluster intensities^0.5) and intensities.
        eigenvalues : (np.ndarray)
            1xK vector of eigenvalues corresponding to clusters.
        number_of_clusters : (int)
            Number of clusters extracted.
        stop_condition : (str)
            The stop condition that caused the algorithm to stop.
    """

    # Validate inputs.
    _validate_inputs(epsilon, tau, k_max, desired_k)

    # Auxiliary variables for comparisons.
    matrix_rows, _ = W.shape
    zeros_vectors = np.zeros((matrix_rows, 1))
    ones_vectors = np.ones((matrix_rows, 1))

    # Auxiliary variables for the stopping conditions.
    residual_data_scatter = 1
    number_of_clusters = 0

    # Auxiliary variables to store results.
    membership_matrix = np.empty((matrix_rows, 0))
    contributions = []
    intensities = []
    eigenvalues = []

    # Sets initial matrix W.
    Wt = (W + W.T) / 2

    # Compute total data scatter.
    data_scatter = np.power(Wt, 2)
    total_data_scatter = np.sum(data_scatter)

    # Stop conditions:
    #      1. Eigenvalues of the residual matrix Wt are not positives;
    #   or 2. Individual cluster contribution is less or equal than 'epsilon';
    #   or 3. 'residual_data_scatter' is less or equal than 'tau';
    #   or 4. 'number_of_clusters' is equal to 'k_max'.
    while True:
        # Compute eigenvalues and eigenvectors of Wt.
        curr_eigenvalues, curr_eigenvectors = LA.eigh(Wt)

        # curr_eigenvalues, curr_eigenvectors = eigh(
        #    Wt,
        #    lower=True,
        #    driver="evd",
        #    overwrite_a=False,
        #    check_finite=False,
        # )

        # curr_eigenvalues, curr_eigenvectors = eigh(
        #    Wt,
        #    lower=True,
        #    driver="evr",
        #    overwrite_a=False,
        #    check_finite=False,
        #    subset_by_value=(ZERO_BOUND, np.inf)
        # )

        eigenvalues_pos = np.argwhere(curr_eigenvalues > ZERO_BOUND).ravel()
        size_positive_eigenvalues = eigenvalues_pos.size

        # size_positive_eigenvalues = curr_eigenvalues.size

        if size_positive_eigenvalues == 0:
            stop_condition = "W"
            # print("[INFO] No positive weights at spectral clusters.")
            break

        # eigenvalues_pos = np.argsort(curr_eigenvalues)[::-1]

        # Store intensities and corresponding membership vectors.
        curr_intensities = np.zeros((size_positive_eigenvalues, 1))
        curr_membership_vectors = np.zeros((matrix_rows, size_positive_eigenvalues))

        # For each positive eigenvalue, compute the corresponding fuzzy cluster.
        for k in range(size_positive_eigenvalues):
            # lt = curr_eigenvalues_diagonal[eigenvalues_pos[k]]

            # Compute the cluster membership vector.
            vf = np.asarray(curr_eigenvectors[:, eigenvalues_pos[k]]).reshape(-1, 1)

            # Calculate normalized membership vector belonging to [0, 1] by projection on the space.
            # The normalization factor is the Euclidean length of the vector.
            bf = np.maximum(zeros_vectors, vf)
            uf = np.minimum(bf, ones_vectors)

            # Normalize uf if its norm is greater than zero.
            if LA.norm(uf) > 0:
                uf = uf / LA.norm(uf)

            vt = uf.T.dot(Wt).dot(uf)
            uf = np.squeeze(np.asarray(uf))
            wt = uf.T.dot(uf)

            # Calculates the intensity lambda (la) of the cluster, which is defined almost as the Rayleigh quotient.
            if wt > 0:
                la = vt.item() / (wt ** 2)
            else:
                la = 0

            # Since lt*vf =(-lt)*(-vf), try symmetric version using -vf.
            vf1 = -vf

            # Calculate normalized membership vector belonging to [0, 1] by projection on the space.
            # The normalization factor is the Euclidean length of the vector.
            bf1 = np.maximum(zeros_vectors, vf1)
            uf1 = np.minimum(bf1, ones_vectors)
            uf1 = np.squeeze(np.asarray(uf1))

            # Normalize uf1 if its norm is greater than zero.
            if LA.norm(uf1) > 0:
                uf1 = uf1 / LA.norm(uf1)

            vt1 = uf1.T.dot(Wt).dot(uf1)
            wt1 = uf1.T.dot(uf1)

            # Calculates the intensity Lambda1 (la1) of the cluster, which is defined almost as the Rayleigh quotient.
            if wt1 > 0:
                la1 = vt1.item() / (wt1 ** 2)
            else:
                la1 = 0

            # Choose the maximum intensity and corresponding membership vector.
            if la > la1:
                curr_intensities[k] = la
                curr_membership_vectors[:, k] = uf.ravel()
            else:
                curr_intensities[k] = la1
                curr_membership_vectors[:, k] = uf1.ravel()

        # Get the maximum intensity and corresponding index.
        max_contribution, max_contribution_index = curr_intensities.max(), curr_intensities.argmax()

        # Check stop condition 1: Eigenvalues of the residual matrix Wt are not positives.
        if max_contribution <= ZERO_BOUND:
            stop_condition = "W"
            # print("[INFO] No positive weights at spectral clusters.")
            break

        # Compute square root and value of lambda intensity of cluster.
        # Compute square root shows the value of fuzziness.
        uf = curr_membership_vectors[:, max_contribution_index]
        vt = uf.T.dot(Wt).dot(uf)
        wt = uf.T.dot(uf)

        # Compute the individual contribution of the cluster to the data scatter.
        individual_cluster_contribution = (vt / wt) ** 2
        individual_cluster_contribution /= total_data_scatter

        # Check stop condition 2: Individual cluster contribution is less or equal than 'epsilon'.
        if desired_k is None and individual_cluster_contribution <= epsilon:
            stop_condition = 'epsilon'
            # print("[INFO] Cluster contribution is too small.")
            break

        # Update the total clusters' contribution.
        residual_data_scatter -= individual_cluster_contribution

        # Check stop condition 3: 'residual_scatter' is less or equal than tau.
        if desired_k is None and residual_data_scatter <= tau:
            stop_condition = 'tau'
            # print("[INFO] Residual is too small.")
            break

        # Append the membership vector, contribution, intensity and eigenvalue of the cluster to the results.
        membership_matrix = np.append(membership_matrix, uf.reshape(-1, 1), axis=1)
        contributions.append(individual_cluster_contribution)
        intensities.append([np.sqrt(max_contribution), max_contribution])
        eigenvalues.append(curr_eigenvalues[eigenvalues_pos[max_contribution_index]])
        number_of_clusters += 1
        print(f"[DEBUG] K' = {number_of_clusters}")

        # Check stop condition 4: 'number_of_clusters' is equal to 'k_max'.
        if desired_k is None and number_of_clusters == k_max:
            stop_condition = 'Kmax'
            # print("[INFO] Maximum number of clusters reached.")
            break

        if desired_k is not None and number_of_clusters == desired_k:
            stop_condition = 'desiredK'
            # print("[INFO] Desired number of clusters reached.")
            break

        # Compute residual similarity matrix, removing the present cluster (i.e. intensity* membership) from similarity matrix.
        Wt = Wt - max_contribution * np.outer(uf, uf)
        Wt = (Wt + Wt.T) / 2

    return membership_matrix, \
        np.asarray(contributions), \
        np.asarray(intensities), \
        np.asarray(eigenvalues), \
        number_of_clusters, \
        stop_condition


def _validate_inputs(
        epsilon: float,
        tau: float,
        k_max: int,
        desired_k: int,
) -> None:
    """
    Validate the inputs.

    Parameters:
        epsilon : (float | None)
            Threshold of the individual cluster contribution.
        tau : (float | None)
            Threshold of the total clusters contribution.
        k_max : (int | None)
            Maximum number of clusters.
        desired_k : (int | None)
            Number of clusters to extract.

    Exceptions:
        ValueError : If one of the following restrictions is not met:
            - When 'desired_k' is provided, 'epsilon', 'tau', and 'k_max' must all be None.
            - When 'desired_k' is None, 'epsilon', 'tau', and 'k_max' must all be provided.
            - 'desired_k' must be a positive integer.
            - 'k_max' must be a positive integer.
    """

    if desired_k is not None and any(v is not None for v in (epsilon, tau, k_max)):
        raise ValueError("[ERROR] When 'desired_k' is provided, 'epsilon', 'tau', and 'k_max' must all be None.")
    if desired_k is None and not all(v is not None for v in (epsilon, tau, k_max)):
        raise ValueError("[ERROR] When 'desired_k' is None, 'epsilon', 'tau', and 'k_max' must all be provided.")
    if desired_k is not None and desired_k <= 0:
        raise ValueError("[ERROR] 'desired_k' must be a positive integer.")
    if k_max is not None and k_max <= 0:
        raise ValueError("[ERROR] 'k_max' must be a positive integer.")
