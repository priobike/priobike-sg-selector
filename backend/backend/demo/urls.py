from demo.views import *
from django.urls import path

app_name = "demo"

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
