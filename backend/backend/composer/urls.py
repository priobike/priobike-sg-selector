from composer.views import *
from django.urls import path

app_name = "composer"

urlpatterns = [
    path("api/lsa/<lsa_id>/metadata",
         LSAMetadataResource.as_view(), name="lsa-metadata"),
    path("api/lsa/<lsa_id>/region", LSARegionResource.as_view(), name="lsa-region"),

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
    path(
        "api/constellation/<constellation_id>",
        ConstellationResource.as_view(),
        name="single-constellation"
    ),
    path(
        "api/constellation/<constellation_id>/stats",
        ConstellationStatsResource.as_view(),
        name="constellation-stats"
    ),
    path(
        "api/constellation",
        ConstellationAllResource.as_view(),
        name="all-constellations"
    ),
    path(
        "api/route_error/<error_id>",
        RouteErrorResource.as_view(),
        name="single-route-error"
    ),
    path(
        "api/route_error/<error_id>/stats",
        RouteErrorStatsResource.as_view(),
        name="route-error-stats"
    ),
    path(
        "api/route_error",
        RouteErrorAllResource.as_view(),
        name="all-route-errors"
    ),
    path(
        "api/health_check/bindings/files",
        HealthCheckBindingFiles.as_view(),
        name="health-check-bindings-files"
    ),
    path(
        "api/health_check/bindings/database",
        HealthCheckBindingsDatabase.as_view(),
        name="health-check-bindings-database"
    )
]
