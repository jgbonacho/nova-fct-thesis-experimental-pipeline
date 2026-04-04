from dataclasses import dataclass, field


@dataclass
class ExtrinsicMetrics:
    """
    Dataclass for extrinsic metrics.

    Attributes:
        diff_of_k : str
            A string representing the number of communities in the ground truth and the number of communities predicted, formatted as "K' | K".
        relative_error_of_k : float
            Relative error of the number of communities, computed as |K'-K|/K.
        ami : float | None
            Adjusted Mutual Information (AMI) score. None if not applicable.
        f_measure : float | None
            F-measure score. None if not applicable.
        ari : float | None
            Adjusted Rand Index (ARI) score. None if not applicable.
        fmi : float | None
            Fowlkes-Mallows Index (FMI) score. None if not applicable.
        nmi : float | None
            Normalized Mutual Information (NMI) score. None if not applicable.
        vi : float | None
            Variation of Information (VI) score. None if not applicable.
        onmi : float | None
            Overlapping Normalized Mutual Information (ONMI) score. None if not applicable.
        omega : float | None
            Omega index score. None if not applicable.
    """

    diff_of_k: str = field(metadata={"label": "K' | K"})
    relative_error_of_k: float = field(metadata={"label": "|K'-K|/K"})
    ami: float = field(default=None, metadata={"label": "AMI"})
    f_measure: float = field(default=None, metadata={"label": "F-measure"})
    ari: float = field(default=None, metadata={"label": "ARI"})
    fmi: float = field(default=None, metadata={"label": "FMI"})
    nmi: float = field(default=None, metadata={"label": "NMI"})
    vi: float = field(default=None, metadata={"label": "VI"})
    onmi: float = field(default=None, metadata={"label": "ONMI"})
    omega: float = field(default=None, metadata={"label": "Omega"})
