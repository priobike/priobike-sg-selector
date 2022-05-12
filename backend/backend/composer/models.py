from django.conf import settings
from django.contrib.gis.db import models
from routing.models import SG


class Route(models.Model):
    """ A route. """

    id = models.IntegerField(primary_key=True)
    geometry = models.LineStringField(srid=settings.LONLAT, geography=True)

    def __str__(self):
        return f"{self.id}"


class RouteSGBinding(models.Model):
    """ A manual SG binding to a route. """

    sg = models.ForeignKey(SG, on_delete=models.CASCADE, related_name="bound_routes")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="bound_sgs")

    # An additional indicator to specify how safe the binding is
    # with regards to mapping or routing issues
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sg.id}-{self.route.id}"


class Connection(models.Model):
    sg = models.OneToOneField(SG, on_delete=models.CASCADE)

    # Elevated geometry with regards to the crossing
    # to visually differenciate between connections
    elevated_geometry = models.LineStringField(dim=3)

    def __str__(self):
        return self.name


class Waypoint(models.Model):
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name="waypoints")

    progress = models.IntegerField()

    # Elevated geometry with regards to the crossing
    # to visually differenciate between connections
    elevated_geometry = models.PointField(dim=3)

    def __str__(self):
        return f"Waypoint at ({self.elevated_geometry}) with progress {self.progress}"
