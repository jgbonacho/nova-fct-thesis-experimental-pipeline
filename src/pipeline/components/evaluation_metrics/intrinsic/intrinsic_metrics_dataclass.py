from dataclasses import dataclass, field

import numpy as np


@dataclass
class IntrinsicMetrics:
    """
    Dataclass for intrinsic metrics.

    Attributes:
        modularity : (float | None)
            Modularity score. None if not applicable.
        conductance : (float | None)
            Conductance score. None if not applicable.
        fuzzy_modularity : (float | None)
            Fuzzy-Modularity score. None if not applicable.
        conductance_bn : (float | None)
            Conductance of Boundary Nodes score. None if not applicable.
    """

    modularity: float = field(default=None, metadata={"label": "Modularity"})
    conductance: float = field(default=None, metadata={"label": "Conductance"})
    fuzzy_modularity: float = field(default=None, metadata={"label": "Fuzzy-Modularity"})
    conductance_bn: float = field(default=None, metadata={"label": "Conductance-BN"})


def labels_to_membership_matrix(
        predicted_labels: list[list[int]],
        k_predicted: int
) -> np.ndarray:
    """
    Convert overlapping community labels to a normalized membership matrix.

    Parameters:
        predicted_labels : (list[list[int]])
            Predicted community labels for each node.
        k_predicted : (int)
            Number of predicted communities.

    Returns:
        U : (np.ndarray, shape[n,k])
            Normalized membership matrix.
    """

    U = np.zeros((len(predicted_labels), k_predicted))

    for node, labels in enumerate(predicted_labels):
        if labels:
            membership = 1.0 / len(labels)

            for label in labels:
                U[node, label] = membership

    return U
