from dataclasses import dataclass, field


@dataclass
class ComputationalMetrics:
    """
    Dataclass for computational metrics.

    Attributes:
        runtime : (float)
            Runtime in seconds.
    """

    runtime: float = field(metadata={"label": "FADDIS Runtime"})
