from django.urls import path

from routing.views import LSASelectionView, MultiLaneSelectionView

app_name = "routing"

urlpatterns = [
    path("select", LSASelectionView.as_view(), name="select"),
    path("select_multi_lane", MultiLaneSelectionView.as_view(), name="select_bulk"),
]
