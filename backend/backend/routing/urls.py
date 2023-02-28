from django.urls import path

from routing.views import LSASelectionView, CrossingSelectionView

app_name = "routing"

urlpatterns = [
    path("select", LSASelectionView.as_view(), name="select"),
    path("select_crossing", CrossingSelectionView.as_view(), name="select_bulk"),
]
