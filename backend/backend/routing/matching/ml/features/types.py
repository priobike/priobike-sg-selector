from enum import Enum
from typing import List
from django.contrib.gis.geos import LineString
from composer.models import Route

from routing.models import LSA


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
