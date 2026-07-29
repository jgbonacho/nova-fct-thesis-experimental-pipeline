"""
Implementation based on https://github.com/dmitsf/GOT/blob/master/got/relevance_analysis/lapin.py
"""

import numpy as np
import numpy.linalg as LA

# Zero threshold for eigenvalues.
ZERO_BOUND = 10 ** (-8)

# Entity threshold for sums of rows/columns.
ENTITY_BOUND = 10 ** (-4)


def lapin(W: np.ndarray) -> np.ndarray:
    """
    LAPIN: Laplacian Pseudo-Inverse transformation.

    Parameters:
        W : (np.ndarray, shape[n,n])
            nxn symmetric similarity/affinity matrix.

    Returns:
        Ln+ : (np.ndarray)
            nxn Laplacian pseudo-inverse transformed matrix.

    Exceptions:
        Exception : If the sums of rows/columns of W are not greater than ENTITY_BOUND.
    """

    W = (W + W.T) / 2
    w_sums = np.ravel(abs(sum(W)))
    nonzero_sums_condition = np.array(w_sums > ENTITY_BOUND)

    if not nonzero_sums_condition.all():
        # W = W[:, nonzero_sums_condition][nonzero_sums_condition, :]
        # w_sums = w_sums[nonzero_sums_condition]
        raise Exception('[ERROR] Entities are no good - remove them first.')

    matrix_rows, _ = W.shape
    C = np.empty((matrix_rows, matrix_rows))
    for i in range(matrix_rows):
        for j in range(matrix_rows):
            C[i, j] = W[i, j] / np.sqrt(w_sums[i] * w_sums[j])
    L = np.eye(matrix_rows) - C

    eigenvalues, eigenvectors = LA.eig(L)
    eigenvalues_diagonal = np.diag(eigenvalues)
    nonzero_condition = np.array(eigenvalues > ZERO_BOUND)
    nonzero_eigenvalues_diagonal = eigenvalues_diagonal[nonzero_condition, :][:, nonzero_condition]
    nonzero_eigenvectors = eigenvectors[:, nonzero_condition]

    Ln = nonzero_eigenvectors.dot(LA.inv(nonzero_eigenvalues_diagonal)).dot(nonzero_eigenvectors.T)
    return np.asarray(Ln, dtype=np.float64)
