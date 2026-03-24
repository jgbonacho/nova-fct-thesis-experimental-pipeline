def set_stop_criterion(n: int, network_family: str, thresholds: dict[str, float]) -> tuple[float, float, int]:
    """
    Set the stop criterion for FADDIS based on the number of nodes and experimental thresholds.

    Parameters:
        n : (int)
            The number of nodes in the graph.
        network_family : (str)
            The family of the network.
        thresholds : (dict[str, float])
            A dictionary mapping network families to their corresponding threshold.

    Returns:
        epsilon, tau, k_max : (float, float, int)
            Tuple containing the stopping rules:
                - Threshold for individual cluster contribution;
                - Threshold for total clusters contribution;
                - Maximum number of clusters.

    Exceptions:
        ValueError : If the number of nodes is not positive.
    """

    if n <= 0:
        raise ValueError("[ERROR] Number of nodes must be positive.")

    threshold = thresholds.get(network_family)
    epsilon = threshold if threshold is not None else 1 / n
    tau = 0.05
    k_max = min(100, n // 2)

    return epsilon, tau, k_max
