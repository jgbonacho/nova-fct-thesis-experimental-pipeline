import numpy as np

from pipeline.components.loaders.adjacency_matrix import ensure_binary_matrix, ensure_symmetric_matrix, \
    ensure_square_matrix, ensure_zero_diagonal_matrix


def compute_kul(A: np.ndarray) -> np.ndarray:
    """
    Compute the affinity matrix using the Kulczynski binary similarity coefficient.
    The symmetry and zero diagonal properties are ensured by design.

    Formula: Wij_Kul = 1/2 * (aij/di + aij/dj),
    where aij = |N(i) ∩ N(j)| for i != j, di = |N(i)|, dj = |N(j)|, N(i) = {u ∈ V : Aiu = 1}, N(j) = {u ∈ V : Aju = 1}.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.

    Returns:
        W_kul : (np.ndarray, shape[n,n])
            nxn symmetric zero diagonal affinity matrix.
    """

    ensure_square_matrix(A)
    ensure_binary_matrix(A)
    ensure_symmetric_matrix(A)
    ensure_zero_diagonal_matrix(A)

    n = A.shape[0]
    degrees = A.sum(axis=1)

    W_kul = np.zeros((n, n), dtype=float)
    for i in range(n):
        di = degrees[i]
        for j in range(i + 1, n):  # upper triangle only
            dj = degrees[j]
            aij = np.minimum(A[i], A[j]).sum()
            val = 0.5 * (aij / di + aij / dj)
            W_kul[i, j] = val
            W_kul[j, i] = val  # mirror

    return W_kul


def compute_dice(A: np.ndarray) -> np.ndarray:
    """
    Compute the affinity matrix using the Dice binary similarity coefficient.
    The symmetry and zero diagonal properties are ensured by design.

    Formula: Wij = 2aij / (di + dj),
    where aij = |N(i) ∩ N(j)| for i != j, di = |N(i)|, dj = |N(j)|, N(i) = {u ∈ V : Aiu = 1}, N(j) = {u ∈ V : Aju = 1}.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.

    Returns:
        W_dice : (np.ndarray, shape[n,n])
            nxn symmetric zero diagonal affinity matrix.
    """

    ensure_square_matrix(A)
    ensure_binary_matrix(A)
    ensure_symmetric_matrix(A)
    ensure_zero_diagonal_matrix(A)

    n = A.shape[0]
    degrees = A.sum(axis=1)

    W_dice = np.zeros((n, n), dtype=float)
    for i in range(n):
        di = degrees[i]
        for j in range(i + 1, n):  # upper triangle only
            dj = degrees[j]
            aij = np.minimum(A[i], A[j]).sum()
            val = (2.0 * aij) / (di + dj)
            W_dice[i, j] = val
            W_dice[j, i] = val  # mirror

    return W_dice


def compute_ochiai(A: np.ndarray) -> np.ndarray:
    """
    Compute the affinity matrix using the Ochiai binary similarity coefficient.
    The symmetry and zero diagonal properties are ensured by design.

    Formula: Wij = aij / sqrt(di * dj),
    where aij = |N(i) ∩ N(j)| for i != j, di = |N(i)|, dj = |N(j)|, N(i) = {u ∈ V : Aiu = 1}, N(j) = {u ∈ V : Aju = 1}.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.

    Returns:
        W_ochiai : (np.ndarray, shape[n,n])
            nxn symmetric zero diagonal affinity matrix.
    """

    ensure_square_matrix(A)
    ensure_binary_matrix(A)
    ensure_symmetric_matrix(A)
    ensure_zero_diagonal_matrix(A)

    n = A.shape[0]
    degrees = A.sum(axis=1)

    W_ochiai = np.zeros((n, n), dtype=float)
    for i in range(n):
        di = degrees[i]
        for j in range(i + 1, n):  # upper triangle only
            dj = degrees[j]
            aij = np.minimum(A[i], A[j]).sum()
            val = aij / np.sqrt(di * dj)
            W_ochiai[i, j] = val
            W_ochiai[j, i] = val  # mirror

    return W_ochiai
