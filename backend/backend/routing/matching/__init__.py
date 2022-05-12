from typing import Iterable, List, Tuple

from django.conf import settings
from django.contrib.gis.geos import LineString
from django.db.models.query import QuerySet
from routing.models import SG


class RouteMatcher:
    def __init__(self, system=settings.LONLAT, *args, **kwargs):
        """
        Initialize the route matcher.

        :param system: The coordinate system used by this matcher.
        """
        self.system = system

    def matches(self, sgs: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        """
        Return the SGs that match the route, as a queryset.
        """
        route = route.transform(self.system, clone=True)
        return sgs, route


class ElementwiseRouteMatcher(RouteMatcher):
    def match(self, sg: SG, route: LineString) -> bool:
        """
        Return if the SG matches the route.
        """
        raise NotImplementedError()

    def matches(self, sgs: QuerySet, route: LineString) -> Tuple[QuerySet, LineString]:
        """
        Return the list of SGs that match the route.
        """
        sgs, route = super().matches(sgs, route)
        pks_to_include = [sg.pk for sg in sgs if self.match(sg, route)]
        return sgs.filter(pk__in=pks_to_include), route


def get_matches(route: LineString, matchers: List[RouteMatcher]) -> Iterable[SG]:
    """
    Return all SG's that match the route.
    """
    matched_sgs = SG.objects.all()
    for matcher in matchers:
        matched_sgs, _ = matcher.matches(matched_sgs, route)
    return matched_sgs
