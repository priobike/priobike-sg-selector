from django.urls import path

from routing.views import LSASelectionView

app_name = "routing"

urlpatterns = [
    path("select", LSASelectionView.as_view(), name="select"),
]
