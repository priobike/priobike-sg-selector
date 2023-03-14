from multi_lane_analyzer.views import *
from django.urls import path

app_name = "multi_lane_analyzer"

urlpatterns = [
   path(
        "api/signalgroups",
        SignalgroupsResource.as_view(),
        name="signalgroups"
    ),
   path(
        "api/signalgroups/segments",
        SignalgroupsSegmentsResource.as_view(),
        name="signalgroups"
    ),
   path(
        "api/route/<route_id>/matches",
        MatchesResource.as_view(),
        name="signalgroups"
    ),
]
