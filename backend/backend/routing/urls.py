from django.urls import path

from routing.views import SignalGroupSelectionView

app_name = "routing"

urlpatterns = [
    path("select", SignalGroupSelectionView.as_view(), name="select"),
]
