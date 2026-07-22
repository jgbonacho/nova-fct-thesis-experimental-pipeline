import numpy as np
import skfuzzy as fuzz


def njw_fcm(
        W: np.ndarray,
        k: int,
        fcm_m: float = 2.0,
        fcm_error: float = 1e-5,
        fcm_max_iter: int = 300,
        fcm_seed: int = 0,
        # fcm_number_of_initializations: int = 10
) -> np.ndarray:
    """
    Compute NJW spectral clustering followed by Fuzzy C-Means.

    Parameters:
        W : (np.ndarray, shape[n,n])
            nxn symmetric similarity/affinity matrix.
        k : (int)
            Number of clusters.
        fcm_m : (float, optional)
            Fuzzifier parameter of Fuzzy C-Means.
            Default is 2.0.
        fcm_error : (float, optional)
            Convergence tolerance of Fuzzy C-Means.
            Default is 1e-5.
        fcm_max_iter : (int, optional)
            Maximum number of Fuzzy C-Means iterations.
            Default is 300.
        fcm_seed : (int, optional)
            Random seed of Fuzzy C-Means.
            Default is 0.

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

    # Compute Fuzzy C-Means using multiple initializations.
    # best_U = None
    # best_objective = np.inf
    #
    # for initialization in range(fcm_number_of_initializations):
    #    _, U, _, _, objective_history, _, _ = fuzz.cluster.cmeans(
    #        data=X.T,
    #        c=k,
    #        m=fcm_m,
    #        error=fcm_error,
    #        maxiter=fcm_max_iter,
    #        seed=fcm_seed + initialization
    #    )
    #
    #    final_objective = objective_history[-1]
    #
    #    if final_objective < best_objective:
    #        best_objective = final_objective
    #        best_U = U
    #
    # return best_U.T
