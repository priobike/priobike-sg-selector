from composer.models import Route
from django.contrib.gis.db import models
from routing.models import SG


class Run(models.Model):
    """
    An analytics run.
    """

    timestamp = models.DateTimeField(auto_now_add=True)
    algorithm_name = models.TextField()

    def __str__(self):
        return f"{self.timestamp}"


class RouteAnalysis(models.Model):
    """
    An analysis for a specific route.
    """

    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)

    duration_seconds = models.FloatField()

    def __str__(self):
        return f"{self.route.id}"


class Hit(models.Model):
    """
    A model to persist true positives, false positives, and false negatives for SGs.
    """

    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    analysis = models.ForeignKey(RouteAnalysis, on_delete=models.CASCADE, related_name="hits")
    sg = models.ForeignKey(SG, on_delete=models.CASCADE, related_name="hits")

    # The key is used to denote the kind of hit, i.e. "tp", "fp", ...
    key = models.TextField()

    def __str__(self):
        return f"{self.analysis.route.id}-{self.sg.id}"
