from django.urls import path

from routing.views import LSASelectionView, MultiLaneSelectionView, AllSGViewGeo, AllSGViewMin

app_name = "routing"

urlpatterns = [
    path("select", LSASelectionView.as_view(), name="select"),
    path("select_multi_lane", MultiLaneSelectionView.as_view(), name="select_bulk"),
    path("all_geo", AllSGViewGeo.as_view(), name="all_geo"),
    path("all_min", AllSGViewMin.as_view(), name="all_min"),
]
