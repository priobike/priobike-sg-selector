import json

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.functional import cached_property


class SignalGroup(models.Model):
    """ A signal group. """
    id = models.CharField(max_length=10, primary_key=True)

    # The geometry of the connection line (MAP topology)
    geometry = models.LineStringField(srid=settings.LONLAT, geography=True)

    @cached_property
    def start_point(self) -> Point:
        """
        The start point of the SignalGroup.

        The start point is defined as the first point of the geometry.
        """
        return Point(*self.geometry.coords[0], srid=self.geometry.srid)

    @cached_property
    def end_point(self) -> Point:
        """
        The end point of the SignalGroup.

        The end point is defined as the last point of the geometry.
        """
        return Point(*self.geometry.coords[-1], srid=self.geometry.srid)

    def serialize(self) -> dict:
        """
        Serialize the SignalGroup to a dict.
        """
        return {
            "id": self.id,
            "geometry": json.loads(self.geometry.geojson),
        }

    def __str__(self):
        return f"{self.id}"
