import json

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.functional import cached_property


class SG(models.Model):
    """ A signal group. """
    id = models.CharField(max_length=10, primary_key=True)

    # The geometry of the ingress line
    ingress_geometry = models.LineStringField(srid=settings.LONLAT, geography=True)

    # The geometry of the connection line (MAP topology)
    geometry = models.LineStringField(srid=settings.LONLAT, geography=True)

    # The geometry of the egress line
    egress_geometry = models.LineStringField(srid=settings.LONLAT, geography=True)

    @cached_property
    def start_point(self) -> Point:
        """
        The start point of the SG.

        The start point is defined as the first point of the geometry.
        """
        return Point(*self.geometry.coords[0], srid=self.geometry.srid)

    @cached_property
    def end_point(self) -> Point:
        """
        The end point of the SG.

        The end point is defined as the last point of the geometry.
        """
        return Point(*self.geometry.coords[-1], srid=self.geometry.srid)

    def serialize(self) -> dict:
        """
        Serialize the SG to a dict.
        """
        return {
            "id": self.id,
            "geometry": json.loads(self.geometry.geojson),
        }

    def __str__(self):
        return f"{self.id}"


class SGMetadata(models.Model):
    """ Metadata for a SG. """

    sg = models.OneToOneField(SG, on_delete=models.CASCADE, primary_key=True)
    topic = models.TextField()
    asset_id = models.TextField()
    lane_type = models.TextField()
    language = models.TextField()
    owner_thing = models.TextField()
    info_last_update = models.DateTimeField()

    connection_id = models.CharField(max_length=10)
    egress_lane_id = models.CharField(max_length=10)
    ingress_lane_id = models.CharField(max_length=10)
    traffic_lights_id = models.CharField(max_length=10)
    signal_group_id = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.sg.id}"
