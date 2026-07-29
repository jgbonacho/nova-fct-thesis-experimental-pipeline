def set_stop_criterion(n: int, threshold_identifier: str, thresholds: dict[str, float]) -> tuple[float, float, int]:
    """
    Set the stop criterion for FADDIS based on the number of nodes and experimental thresholds.

    Parameters:
        n : (int)
            The number of nodes in the graph.
        threshold_identifier : (str)
            The network family or network identifier.
        thresholds : (dict[str, float])
            A dictionary mapping threshold identifiers to their corresponding threshold.

    Returns:
        epsilon, tau, k_max : (float, float, int)
            Tuple containing the stopping rules:
                - Threshold for individual cluster contribution (experimental threshold or default 1/n);
                - Threshold for total clusters contribution (0.05);
                - Maximum number of clusters (min(500, n/2)).

    Exceptions:
        ValueError : If the number of nodes is not positive.
    """

    if n <= 0:
        raise ValueError("[ERROR] Number of nodes must be positive.")

    threshold = thresholds.get(threshold_identifier)
    epsilon = threshold if threshold is not None else 1 / n
    tau = 0.05
    k_max = min(500, n // 2)

    return epsilon, tau, k_max
