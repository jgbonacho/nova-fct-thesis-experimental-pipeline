"""
Implementation based on https://github.com/dmitsf/GOT/blob/master/got/relevance_analysis/lapin.py
"""

import numpy as np
import numpy.linalg as LA

# Zero threshold for eigenvalues.
ZERO_BOUND = 10 ** (-8)

# Entity threshold for sums of rows/columns.
ENTITY_BOUND = 10 ** (-4)


def lapin(W, laplacian_variant='symmetric_normalized_laplacian'):
    """
    LAPIN: Laplacian Pseudo-Inverse transformation.

    Parameters:
        W : (np.ndarray, shape[n,n])
            nxn symmetric similarity/affinity matrix.
        laplacian_variant : (str, optional)
            Variant of Laplacian to use.
            Default is 'symmetric_normalized_laplacian'.
            Other options are 'random_walk_normalized_laplacian' or 'unnormalized_laplacian'.

    Returns:
        Ln+ : (np.matrix)
            nxn Laplacian pseudo-inverse transformed matrix.

    Exceptions:
        ValueError : If laplacian_variant is not supported.
    """

    if (laplacian_variant not in
            ['symmetric_normalized_laplacian', 'random_walk_normalized_laplacian', 'unnormalized_laplacian']
    ):
        raise ValueError(f"[ERROR] Laplacian variant {laplacian_variant} not supported.")

    # W = (W + W.T) / 2
    w_sums = np.ravel(abs(sum(W)))
    nonzero_sums_condition = np.array(w_sums > ENTITY_BOUND)

    if not nonzero_sums_condition.all():
        print('[INFO] These entities are no good - remove them first.')
        print([i for i, j in enumerate(nonzero_sums_condition, 1) if not j])
        W = W[:, nonzero_sums_condition][nonzero_sums_condition, :]
        w_sums = w_sums[nonzero_sums_condition]

    matrix_rows, _ = W.shape

    if laplacian_variant == 'unnormalized_laplacian':
        # L = D - W
        L = np.diag(w_sums) - W
    else:
        is_symmetric_normalized_laplacian = laplacian_variant == 'symmetric_normalized_laplacian'
        C = np.empty((matrix_rows, matrix_rows))
        for i in range(matrix_rows):
            for j in range(matrix_rows):
                if is_symmetric_normalized_laplacian:
                    C[i, j] = W[i, j] / np.sqrt(w_sums[i] * w_sums[j])
                else:
                    C[i, j] = W[i, j] / w_sums[i]
        # L = I - D^(-1/2) * W * D^(-1/2) or L = I - D^(-1) * W
        L = np.eye(matrix_rows) - C

    eigenvalues, eigenvectors = LA.eig(L)
    eigenvalues_diagonal = np.diag(eigenvalues)
    nonzero_condition = np.array(eigenvalues > ZERO_BOUND)
    nonzero_eigenvalues_diagonal = eigenvalues_diagonal[nonzero_condition, :][:, nonzero_condition]
    nonzero_eigenvectors = eigenvectors[:, nonzero_condition]

    return nonzero_eigenvectors.dot(LA.inv(nonzero_eigenvalues_diagonal)).dot(nonzero_eigenvectors.T)
