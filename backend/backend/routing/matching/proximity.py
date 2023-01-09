
from typing import Tuple

from django.contrib.gis.geos.linestring import LineString
from django.contrib.gis.measure import D
from django.db.models.query import QuerySet
from routing.matching import RouteMatcher


class ProximityMatcher(RouteMatcher):
    def __init__(self, search_radius_m=13, *args, **kwargs):
        """
        Initialize the proximity matcher.

        :param search_radius_m: The search radius in meters.
        """
        super().__init__(*args, **kwargs)
        self.search_radius_m = search_radius_m

    def matches(self, lsas: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        lsas, route = super().matches(lsas, route)
        lsas = lsas.filter(geometry__dwithin=(route, D(m=self.search_radius_m)))
        return lsas, route
