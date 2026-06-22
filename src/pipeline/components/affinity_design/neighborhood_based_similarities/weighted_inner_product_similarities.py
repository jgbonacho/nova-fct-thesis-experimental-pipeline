import numpy as np

from pipeline.components.loaders.adjacency_matrix import ensure_square_matrix, ensure_binary_matrix, \
    ensure_symmetric_matrix, ensure_zero_diagonal_matrix


def compute_ip(A: np.ndarray, beta: float = 0.0) -> np.ndarray:
    """
    Compute the affinity matrix using the weighted inner product similarity measure.
    The symmetry and zero diagonal properties are ensured by design.

    Formula: W_ij^(IP) = xi^T * Dw * xj = Σu∈N(i)∩N(j) wu,
    where Dw = diag(w1, ..., wn), xi ∈ {0,1}^n neighbor-incidence vector of i, xj ∈ {0,1}^n neighbor-incidence vector of j.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.
        beta : (float, optional)
            Weight exponent in [0, 1]. beta=0 gives Common Neighbors, beta=1 gives Resource Allocation index.
            Default is 0.

    Returns:
        W_ip : (np.ndarray, shape[n,n])
            nxn symmetric zero diagonal affinity matrix.
    """

    ensure_square_matrix(A)
    ensure_binary_matrix(A)
    ensure_symmetric_matrix(A)
    ensure_zero_diagonal_matrix(A)

    n = A.shape[0]
    degrees = A.sum(axis=1).astype(float)
    weights = _compute_weights_from_degrees(degrees, beta)

    W_ip = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        xi = A[i]
        for j in range(i + 1, n):  # upper triangle only
            xj = A[j]
            val = np.sum(xi.T * weights * xj)
            W_ip[i, j] = val
            W_ip[j, i] = val  # mirror

    return W_ip


def compute_cosip(A: np.ndarray, beta: float = 0.0) -> np.ndarray:
    """
    Compute the affinity matrix using the cosine-normalized weighted inner product similarity.
    The symmetry and zero diagonal properties are ensured by design.

    Formula: W_ij^(CosIP) = (xi^T * Dw * xj) / (sqrt(xi^T * Dw * xi) * sqrt(xj^T * Dw * xj)),
    where Dw = diag(w1, ..., wn), xi ∈ {0,1}^n neighbor-incidence vector of i, xj ∈ {0,1}^n neighbor-incidence vector of j.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.
        beta : (float, optional)
            Weight exponent in [0, 1]. beta=0 gives Common Neighbors, beta=1 gives Resource Allocation index.
            Default is 0.

    Returns:
        W_cosip : (np.ndarray, shape[n,n])
            nxn symmetric zero diagonal affinity matrix.
    """

    ensure_square_matrix(A)
    ensure_binary_matrix(A)
    ensure_symmetric_matrix(A)
    ensure_zero_diagonal_matrix(A)

    n = A.shape[0]
    degrees = A.sum(axis=1).astype(float)
    weights = _compute_weights_from_degrees(degrees, beta)

    W_cosip = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        xi = A[i]
        for j in range(i + 1, n):  # upper triangle only
            xj = A[j]
            numerator = np.sum(xi.T * weights * xj)
            denominator = np.sqrt(np.sum(xi.T * weights * xi)) * np.sqrt(np.sum(xj.T * weights * xj))
            val = numerator / denominator
            W_cosip[i, j] = val
            W_cosip[j, i] = val  # mirror

    return W_cosip


def _compute_weights_from_degrees(degrees: np.ndarray, beta: float) -> np.ndarray:
    """
    Compute weights from degrees.

    Formula: w_i = degree(i)^(-beta).

    Parameters:
        degrees : (np.ndarray, shape[n])
            Degree vector where degrees[i] = |N(i)| = sum of the i-th row of A.
        beta : (float)
            Weight exponent in [0, 1]. beta=0 gives Common Neighbors, beta=1 gives Resource Allocation index.

    Returns:
        w : (np.ndarray, shape[n])
            Weight vector where w[i] = degree(i)^(-beta) for degree(i) > 0, w[i] = 0 for degree(i) = 0.

    Exceptions:
        ValueError: If beta is not in [0, 1].
    """

    if not (0.0 <= beta <= 1.0):
        raise ValueError("[ERROR] Beta must be in [0, 1].")

    w = np.zeros_like(degrees, dtype=float)
    mask = degrees > 0
    w[mask] = degrees[mask] ** (-beta)

    return w
