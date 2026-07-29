from dataclasses import dataclass, field


@dataclass
class SparsificationInfo:
    """
    Dataclass for sparsification information.

    Attributes:
        theta : (float | str)
            Sparsification threshold. If sparsification is skipped, this is "-".
        target_average_degree : (float | str)
            Target average degree used by sparsification. If sparsification is skipped, this is "-".
        actual_average_degree : (float)
            Actual average degree after sparsification.
        diff_n : (str)
            A string representing the original number of nodes and the sparsified number of nodes,
            formatted as "N | N_s".
    """

    theta: float = field(metadata={"label": "Theta"})
    target_average_degree: float = field(metadata={"label": "Target Avg Degree"})
    actual_average_degree: float = field(metadata={"label": "Actual Avg Degree"})
    diff_n: str = field(metadata={"label": "N | Sparsified N"})
