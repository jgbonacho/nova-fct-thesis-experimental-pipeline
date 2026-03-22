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
        ami : float
            Adjusted Mutual Information (AMI) score.
        f_measure : float
            F-measure score.
        ari : float
            Adjusted Rand Index (ARI) score.
        fmi : float
            Fowlkes-Mallows Index (FMI) score.
        nmi : float
            Normalized Mutual Information (NMI) score.
        vi : float
            Variation of Information (VI) score.
        onmi : float
            Overlapping Normalized Mutual Information (ONMI) score.
        omega : float
            Omega index score.
    """

    diff_of_k: str = field(metadata={"label": "K' | K"})
    relative_error_of_k: float = field(metadata={"label": "|K'-K|/K"})
    ami: float | None = field(default=None, metadata={"label": "AMI"})
    f_measure: float | None = field(default=None, metadata={"label": "F-measure"})
    ari: float | None = field(default=None, metadata={"label": "ARI"})
    fmi: float | None = field(default=None, metadata={"label": "FMI"})
    nmi: float | None = field(default=None, metadata={"label": "NMI"})
    vi: float | None = field(default=None, metadata={"label": "VI"})
    onmi: float | None = field(default=None, metadata={"label": "ONMI"})
    omega: float | None = field(default=None, metadata={"label": "Omega"})
