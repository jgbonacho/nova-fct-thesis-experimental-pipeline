from dataclasses import dataclass


@dataclass
class DefuzzificationRule:
    """
    Dataclass for defuzzification rule.

    Attributes:
        gamma : (float)
            Hyperparameter for the defuzzification rule.
    """

    gamma: float
