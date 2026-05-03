import numpy as np


def default_affinity(A: np.ndarray) -> np.ndarray:
    """
    Default affinity design that returns a copy of the input adjacency matrix A as the affinity matrix W with float64 numerical precision.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.

    Returns:
        W : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal affinity matrix.
    """

    return np.asarray(A, dtype=np.float64)
