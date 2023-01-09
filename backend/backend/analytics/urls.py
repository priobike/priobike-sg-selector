from django.urls import path

from analytics.views import StatisticsResource

app_name = "analytics"

urlpatterns = [
    path("api/statistics", StatisticsResource.as_view(), name="statistics"),
]
