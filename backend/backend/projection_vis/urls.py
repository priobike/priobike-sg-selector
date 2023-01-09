from projection_vis.views import *
from django.urls import path

app_name = "projection_vis"

urlpatterns = [
    path(
        "api/route/<route_id>/connections/segments",
        ConnectionSegmentsResource.as_view(),
        name="route-connection-segments"
    ),
    path(
        "api/route/<route_id>/connections",
        ConnectionsResource.as_view(),
        name="route-connections"
    ),
    path(
        "api/route/<route_id>/segments",
        RouteSegmentsResource.as_view(),
        name="route-segments"
    ),
    path(
        "api/route/<route_id>/bindings",
        RouteBindingResource.as_view(),
        name="route-bindings"
    ),
    path(
        "api/route/<route_id>/region",
        RouteRegionResource.as_view(),
        name="route-region"
    ),
    path(
        "api/route/<route_id>",
        RouteResource.as_view(),
        name="route"
    ),
    path(
        "api/route/<route_id>/lsa/<lsa_id>",
        BindingsConnectionsResource.as_view(),
        name="route-lsa"
    ),
    path(
        "api/route/<route_id>/lsa/<lsa_id>/vis",
        ExtendedProjectionVisResource.as_view(),
        name="route-lsa"
    ),
    path(
        "api/route/<route_id>/lsa/segments",
        BindingsConnectionsSegmentsResource.as_view(),
        name="route-lsa-segments"
    ),
]
