from enum import Enum


class AffinityDesign(str, Enum):
    """
    Enumeration of the supported affinity-matrix designs.

    Attributes:
        DEFAULT : (str)
            Use the original adjacency matrix as the affinity matrix.
        KUL : (str)
            Use the Kulczynski binary-set similarity.
        DICE : (str)
            Use the Dice binary-set similarity.
        OCHIAI : (str)
            Use the Ochiai binary-set similarity.
        IP_B0 : (str)
            Use the weighted inner-product similarity with beta equal to 0.
        IP_B0_5 : (str)
            Use the weighted inner-product similarity with beta equal to 0.5.
        IP_B1 : (str)
            Use the weighted inner-product similarity with beta equal to 1.
        COSIP_B0 : (str)
            Use the cosine-weighted inner-product similarity with beta equal to 0.
        COSIP_B0_5 : (str)
            Use the cosine-weighted inner-product similarity with beta equal to 0.5.
        COSIP_B1 : (str)
            Use the cosine-weighted inner-product similarity with beta equal to 1.
    """

    DEFAULT = "Default"
    KUL = "Kul"
    DICE = "Dice"
    OCHIAI = "Ochiai"
    IP_B0 = "IP_beta0"
    IP_B0_5 = "IP_beta0.5"
    IP_B1 = "IP_beta1"
    COSIP_B0 = "CosIP_beta0"
    COSIP_B0_5 = "CosIP_beta0.5"
    COSIP_B1 = "CosIP_beta1"
