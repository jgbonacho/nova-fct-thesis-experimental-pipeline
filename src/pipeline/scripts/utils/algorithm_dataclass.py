from enum import Enum

import networkx as nx
import numpy as np

from pipeline.baselines.non_spectral.cfinder import cfinder
from pipeline.baselines.non_spectral.slpa import slpa
from pipeline.baselines.spectral.njw_fcm import njw_fcm
from pipeline.components.faddis.faddis import faddis


class Algorithm(Enum):
    FADDIS = "FADDIS"
    NJW_FCM = "NJW+FCM"
    SLPA = "SLPA (t=100, r=0.45)"
    CFINDER = "CFinder (clique_size=4)"


def wrapper_spectral_algorithm(
        algorithm_name: Algorithm,
        W: np.ndarray,
        k: int,
        faddis_stopping_criterion: tuple = None
):
    """
    Execute the selected spectral comparison algorithm.

    Parameters:
        algorithm_name : (Algorithm)
            The algorithm to execute.
        W : (np.ndarray, shape[n,n])
            nxn symmetric similarity/affinity matrix.
        k : (int)
            Number of ground-truth communities.
        faddis_stopping_criterion : (tuple)
            The FADDIS stopping criterion.
            Default is None.

    Returns:
        membership_matrix : (np.ndarray, shape[n,k'])
            Fuzzy membership matrix returned by the selected algorithm.

    Exceptions:
        ValueError : If the selected algorithm is not supported.
    """

    if algorithm_name == Algorithm.FADDIS:
        if faddis_stopping_criterion is not None:
            (epsilon, tau, k_max) = faddis_stopping_criterion
            membership_matrix, _, _, _, _, _ = faddis(W=W, epsilon=epsilon, tau=tau, k_max=k_max)
        else:
            membership_matrix, _, _, _, _, _ = faddis(W=W, desired_k=k + 1)
        return membership_matrix
    elif algorithm_name == Algorithm.NJW_FCM:
        return njw_fcm(W=W, k=k)
    else:
        raise ValueError(f"[ERROR] {algorithm_name.value} is not a valid spectral algorithm.")


def wrapper_non_spectral_algorithm(algorithm_name: Algorithm, graph: nx.Graph):
    """
    Execute the selected non-spectral comparison algorithm.

    Parameters:
        algorithm_name : (Algorithm)
            The algorithm to execute.
        graph : (nx.Graph)
            Input NetworkX graph.

    Returns:
        predicted_labels : (list[list[int]])
            List of detected community labels assigned to each node.
        k_predicted : (int)
            Number of detected communities.

    Exceptions:
        ValueError : If the selected algorithm is not supported.
    """

    if algorithm_name == Algorithm.SLPA:
        return slpa(graph=graph, t=100, r=0.45, seed=0)
    elif algorithm_name == Algorithm.CFINDER:
        return cfinder(graph=graph, clique_size=4)
    else:
        raise ValueError(f"[ERROR] {algorithm_name.value} is not a valid non-spectral algorithm.")
