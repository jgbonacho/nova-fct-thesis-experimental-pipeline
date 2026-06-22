from dataclasses import dataclass, field

from pipeline.components.evaluation_metrics.computational.computational_metrics import ComputationalMetrics
from pipeline.components.evaluation_metrics.extrinsic.extrinsic_metrics_dataclass import ExtrinsicMetrics
from pipeline.components.evaluation_metrics.intrinsic.intrinsic_metrics_dataclass import IntrinsicMetrics


@dataclass
class Result:
    """
    Dataclass for results.

    Attributes:
        id : (str)
            Identifier for the result.
        network_family : (str)
            The family of the network.
        network : (str)
            The name of the network.
        overlapping : (bool)
            Whether the ground truth is overlapping.
        affinity_design : (str)
            The affinity design label used in the experiment.
        actual_average_degree : (float)
            Actual average degree after sparsification.
        sparsification_target_average_degree : (float)
            Target average degree used by the sparsification procedure.
        sparsification_theta : (float)
            Theta used by the sparsification.
        sparsification_diff_n : (str)
            A string representing the original number of nodes and the number of nodes after sparsification,
            formatted as "N | N_s".
        execution_mode : (str)
            The execution mode used in the experiment.
        laplacian_variant : (str | None)
            The Laplacian variant used in the experiment, if any.
        epsilon : (float)
            The epsilon parameter used in the experiment.
        tau : (float)
            The tau parameter used in the experiment.
        k_max : (int)
            The k_max parameter used in the experiment.
        stop_condition : (str)
            The stop condition used in the experiment.
        gamma : (float)
            The gamma parameter used in the experiment.
        first_cluster_discarded : (bool)
            Whether the first cluster was discarded in the experiment.
        extrinsic_results : (ExtrinsicMetrics | None)
            The extrinsic metrics results, if computed.
        intrinsic_results : (IntrinsicMetrics | None)
            The intrinsic metrics results, if computed.
        computational_results : (ComputationalMetrics | None)
            The computational metrics results, if computed.
    """

    id: str = field(metadata={"label": "ID"})
    network_family: str = field(metadata={"label": "Network Family"})
    network: str = field(metadata={"label": "Network"})
    overlapping: bool = field(metadata={"label": "Overlapping?"})
    affinity_design: str = field(metadata={"label": "Affinity Design"})
    actual_average_degree: float = field(metadata={"label": "Actual Avg Degree"})
    sparsification_target_average_degree: float = field(metadata={"label": "Target Avg Degree"})
    sparsification_theta: float = field(metadata={"label": "Theta"})
    sparsification_diff_n: str = field(metadata={"label": "N | Sparsified N"})
    execution_mode: str = field(metadata={"label": "Execution Mode"})
    laplacian_variant: str = field(metadata={"label": "Laplacian"})
    epsilon: float = field(metadata={"label": "Epsilon"})
    tau: float = field(metadata={"label": "Tau"})
    k_max: int = field(metadata={"label": "Kmax"})
    stop_condition: str = field(metadata={"label": "Stop Condition"})
    gamma: float = field(metadata={"label": "Gamma"})
    first_cluster_discarded: bool = field(metadata={"label": "C0 discarded?"})
    extrinsic_results: ExtrinsicMetrics = field(default=None),
    intrinsic_results: IntrinsicMetrics = field(default=None),
    computational_results: ComputationalMetrics = field(default=None)
