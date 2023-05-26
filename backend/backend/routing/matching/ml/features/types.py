from enum import Enum


class FeatureType(Enum):
    NUMERICAL = 1
    CATEGORIAL = 2
    CONTINUOUS = 3
    DISCRETE = 4


class Timing:
    def __init__(
        self,
        base: float,
        extra: float
    ):
        self.base = base
        self.extra = extra
