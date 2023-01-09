from typing import Iterable, List, Tuple

from django.conf import settings
from django.contrib.gis.geos import LineString
from django.db.models.query import QuerySet
from routing.models import LSA


class RouteMatcher:
    def __init__(self, system=settings.LONLAT, *args, **kwargs):
        """
        Initialize the route matcher.

        :param system: The coordinate system used by this matcher.
        """
        self.system = system

    def matches(self, lsas: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        """
        Return the LSAs that match the route, as a queryset.
        """
        route = route.transform(self.system, clone=True)
        return lsas, route


class ElementwiseRouteMatcher(RouteMatcher):
    def match(self, lsa: LSA, route: LineString) -> bool:
        """
        Return if the LSA matches the route.
        """
        raise NotImplementedError()

    def matches(self, lsas: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        """
        Return the list of LSAs that match the route.
        """
        lsas, route = super().matches(lsas, route)
        pks_to_include = [lsa.pk for lsa in lsas if self.match(lsa, route)]
        return lsas.filter(pk__in=pks_to_include), route


def get_matches(route: LineString, matchers: List[RouteMatcher]) -> Iterable[LSA]:
    """
    Return all LSA's that match the route.
    """
    matched_lsas = LSA.objects.all()
    for matcher in matchers:
        matched_lsas, _ = matcher.matches(matched_lsas, route)
    return matched_lsas
