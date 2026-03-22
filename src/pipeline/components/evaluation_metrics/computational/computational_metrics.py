import time

from pipeline.components.evaluation_metrics.computational.computational_metrics_dataclass import ComputationalMetrics


def get_computation_start_time():
    """
    Retrieve the start time of the computation.

    Returns:
        start_time : (float)
            Start time of the computation.
    """

    return _get_current_time()


def get_computation_end_time():
    """
    Retrieve the end time of the computation.

    Returns:
        end_time : (float)
            End time of the computation.
    """

    return _get_current_time()


def compute_computational_metrics(start_time, end_time):
    """
    Compute computational metrics.

    Parameters:
        start_time : (float)
            Start time of the computation.
        end_time : (float)
            End time of the computation.

    Returns:
        computational_metrics : (ComputationalMetrics)
            Computational metrics.
    """

    return ComputationalMetrics(
        runtime=_compute_runtime(start_time, end_time),
    )


def _get_current_time():
    """
    Retrieve the current time.

    Returns:
        current_time : (float)
            Current time.
    """

    return time.perf_counter()


def _compute_runtime(start_time, end_time):
    """
    Compute the runtime of the computation (in seconds).

    Parameters:
        start_time : (float)
            Start time of the computation.
        end_time : (float)
            End time of the computation.

    Returns:
        runtime : (float)
            Runtime of the computation.
    """

    return end_time - start_time
