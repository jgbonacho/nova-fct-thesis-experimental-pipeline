from dataclasses import dataclass, field


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
