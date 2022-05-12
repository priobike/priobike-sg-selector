from django.urls import path

from routing.views import SGSelectionView

app_name = "routing"

urlpatterns = [
    path("select", SGSelectionView.as_view(), name="select"),
]
