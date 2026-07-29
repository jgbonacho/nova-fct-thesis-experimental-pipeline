import networkx as nx
import numpy as np


def compute_adjacency_matrix(graph: nx.Graph) -> np.ndarray:
    """
    Compute the adjacency matrix of a graph and ensure it is symmetric, binary and has a zero diagonal.

    Parameters:
        graph : (nx.Graph)
            The unweighted and undirected input graph.

    Returns:
        A : (np.ndarray, shape[n,n])
            nxn symmetric binary zero diagonal adjacency matrix.
    """

    A = nx.to_numpy_array(graph, nodelist=sorted(graph.nodes()))

    ensure_square_matrix(A)
    ensure_binary_matrix(A)
    ensure_symmetric_matrix(A)

    set_zero_diagonal_matrix(A)

    return A


def ensure_square_matrix(A: np.ndarray) -> None:
    """
    Ensure the adjacency matrix is square.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn adjacency matrix.

    Exceptions:
        ValueError : If the adjacency matrix is not square.
    """

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("[ERROR] Adjacency matrix is not square.")


def ensure_symmetric_matrix(A: np.ndarray) -> None:
    """
    Ensure the adjacency matrix is symmetric.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn adjacency matrix.

    Exceptions:
        ValueError : If the adjacency matrix is not symmetric.
    """

    if not np.all(A == A.T):
        raise ValueError("[ERROR] Adjacency matrix is not symmetric.")


def ensure_binary_matrix(A: np.ndarray) -> None:
    """
     Ensure the adjacency matrix is binary.

     Parameters:
         A : (np.ndarray, shape[n,n])
             nxn adjacency matrix.

     Exceptions:
         ValueError : If the adjacency matrix is not binary.
    """

    if not np.all((A == 0) | (A == 1)):
        raise ValueError("[ERROR] Adjacency matrix is not binary.")


def ensure_zero_diagonal_matrix(A: np.ndarray) -> None:
    """
     Ensure the adjacency matrix has a zero diagonal.

     Parameters:
         A : (np.ndarray, shape[n,n])
             nxn adjacency matrix.

     Exceptions:
         ValueError : If the adjacency matrix is not zero diagonal.
    """

    if not np.all(np.diag(A) == 0):
        raise ValueError("[ERROR] Adjacency matrix diagonal is not zero.")


def set_zero_diagonal_matrix(A: np.ndarray) -> None:
    """
    Set in place the diagonal of the adjacency matrix to zero.

    Parameters:
        A : (np.ndarray, shape[n,n])
            nxn adjacency matrix.
    """

    if not np.all(np.diag(A) == 0):
        print("[INFO] Setting adjacency matrix diagonal to zero.")
        np.fill_diagonal(A, 0)
