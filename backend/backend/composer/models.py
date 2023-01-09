from django.conf import settings
from django.contrib.gis.db import models
from routing.models import LSA


class Route(models.Model):
    """ A route. """

    id = models.IntegerField(primary_key=True)
    geometry = models.LineStringField(srid=settings.LONLAT, geography=True)

    def __str__(self):
        return f"{self.id}"


class Constellation(models.Model):
    """ A constellation between route and MAP topology. """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=70)
    description = models.TextField()
    custom_id = models.CharField(max_length=10)


class RouteError(models.Model):
    """ A route error coming from the routing engnine in combination with OMS-data. """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=70)
    description = models.TextField()
    custom_id = models.CharField(max_length=10)


class RouteLSABinding(models.Model):
    """ A manual LSA binding to a route. """

    lsa = models.ForeignKey(LSA, on_delete=models.CASCADE,
                            related_name="bound_routes")
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="bound_lsas")
    
    corresponding_constellation = models.ForeignKey(Constellation, blank=True, null=True, on_delete=models.SET_NULL)
    corresponding_route_error = models.ForeignKey(RouteError, blank=True, null=True, on_delete=models.SET_NULL)

    # An additional indicator to specify how safe the binding is
    # with regards to mapping or routing issues
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.lsa.id}-{self.route.id}"


class Connection(models.Model):
    lsa = models.OneToOneField(LSA, on_delete=models.CASCADE)

    # Elevated geometry with regards to the crossing
    # to visually differenciate between connections
    elevated_geometry = models.LineStringField(dim=3)

    def __str__(self):
        return self.name


class Waypoint(models.Model):
    connection = models.ForeignKey(
        Connection, on_delete=models.CASCADE, related_name="waypoints")

    progress = models.IntegerField()

    # Elevated geometry with regards to the crossing
    # to visually differenciate between connections
    elevated_geometry = models.PointField(dim=3)

    def __str__(self):
        return f"Waypoint at ({self.elevated_geometry}) with progress {self.progress}"
