from django.urls import path

from composer.views import *

app_name = "composer"

urlpatterns = [
    path("api/sg/<sg_id>/metadata", SGMetadataResource.as_view(), name="sg-metadata"),
    path("api/sg/<sg_id>/region", SGRegionResource.as_view(), name="sg-region"),

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
        "api/route/<route_id>/crossings",
        RouteCrossingsResource.as_view(),
        name="route-region"
    ),
    path(
        "api/route/<route_id>/next",
        NextRouteResource.as_view(),
        name="route-next"
    ),
    path(
        "api/route/<route_id>",
        RouteResource.as_view(),
        name="route"
    ),
]
