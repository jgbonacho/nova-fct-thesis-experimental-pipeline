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
    SLPA = "SLPA"
    CFINDER = "CFinder"

    def execute_faddis(
            self,
            W: np.ndarray,
            k: int = None,
            faddis_stopping_criterion: tuple = None
    ) -> np.ndarray:
        """
        Execute FADDIS.

        Parameters:
           W : (np.ndarray, shape[n,n])
               nxn symmetric affinity matrix.
           k : (int, optional)
               Desired number of communities.
               Default is None.
           faddis_stopping_criterion : (tuple[float, float, int], optional)
               FADDIS stopping criterion containing epsilon, tau and k_max.
               Default is None.

        Returns:
           U : (np.ndarray, shape[n,k])
               Fuzzy memberships per node per community.
        """

        if self != Algorithm.FADDIS:
            raise Exception("[ERROR] Algorithm is not FADDIS.")

        if k is not None and faddis_stopping_criterion is None:
            U, _, _, _, _, _ = faddis(W=W, desired_k=k + 1)
            return U
        elif k is None and faddis_stopping_criterion is not None:
            (epsilon, tau, k_max) = faddis_stopping_criterion
            U, _, _, _, _, _ = faddis(W=W, epsilon=epsilon, tau=tau, k_max=k_max)
            return U
        else:
            raise Exception("[ERROR] Algorithm parameters are invalid.")

    def execute_njw_fcm(
            self,
            W: np.ndarray,
            k: int,
            fcm_m: float,
            fcm_error: float,
            fcm_max_iter: int,
            fcm_seed: int
    ) -> np.ndarray:
        """
        Execute NJW followed by Fuzzy C-Means.

        Parameters:
          W : (np.ndarray, shape[n,n])
              nxn symmetric affinity matrix.
          k : (int)
              Number of communities.
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
              Fuzzy memberships per node per community.
        """

        if self != Algorithm.NJW_FCM:
            raise Exception("[ERROR] Algorithm is not NJW+FCM.")

        return njw_fcm(W, k, fcm_m, fcm_error, fcm_max_iter, fcm_seed)

    def execute_slpa(
            self,
            graph: nx.Graph,
            t: int,
            r: float,
            seed: int
    ) -> tuple[list[list[int]], int]:
        """
        Execute SLPA.

        Parameters:
            graph : (nx.Graph)
                The graph.
            t : (int)
                Number of SLPA iterations.
            r : (float)
                Post-processing threshold used to remove labels with low occurrence probabilities.
            seed : (int)
                Random seed.

        Returns:
            predicted_labels : (list[list[int]], length n)
                Predicted community labels for each node.
            k_predicted : (int)
                Number of predicted communities.
        """

        if self != Algorithm.SLPA:
            raise Exception("[ERROR] Algorithm is not SLPA.")

        return slpa(graph, t, r, seed)

    def execute_cfinder(
            self,
            graph: nx.Graph,
            clique_size: int
    ) -> tuple[list[list[int]], int]:
        """
        Execute CFinder.

        Parameters:
            graph : (nx.Graph)
                The graph.
            clique_size : (int)
                Minimum clique size used to detect communities.

        Returns:
            predicted_labels : (list[list[int]], length n)
                Predicted community labels for each node.
            k_predicted : (int)
                Number of predicted communities.
        """

        if self != Algorithm.CFINDER:
            raise Exception("[ERROR] Algorithm is not CFinder.")

        return cfinder(graph, clique_size)
