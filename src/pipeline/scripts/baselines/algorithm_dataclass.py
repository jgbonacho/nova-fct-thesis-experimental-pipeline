from enum import Enum


class Algorithm(Enum):
    FADDIS = "FADDIS"
    NJW_FCM = "NJW+FCM"
    SLPA = "SLPA (t=100, r=0.45)"
    CFINDER = "CFinder (clique_size=4)"
