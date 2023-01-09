from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from backend.views import HealthcheckView, StatusView

urlpatterns = [
    path('routing/', include('routing.urls')),
    path('status', StatusView.as_view(), name='status'),
    path('healthcheck', HealthcheckView.as_view(), name='healthcheck'),
]

if settings.DEBUG:
    # Include development modules
    urlpatterns += [
        path('admin', admin.site.urls),
        path('composer/', include('composer.urls')),
        path('analytics/', include('analytics.urls')),
        path('jiggle_vis/', include('jiggle_vis.urls')),
        path('projection_vis/', include('projection_vis.urls')),
        path('ml_evaluation/', include('ml_evaluation.urls')),
        path('demo/', include('demo.urls')),
    ]
