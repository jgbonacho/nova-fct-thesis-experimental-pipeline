from dataclasses import dataclass


@dataclass
class ExecutionMode:
    """
    Dataclass for execution mode.

    Attributes:
        label : (str)
            The label for the execution mode.
        apply_lapin : (bool)
            Whether to apply LAPIN or not.
    """

    label: str
    apply_lapin: bool
