from django.urls import include, path

from backend.views import StatusView

urlpatterns = [
    path('routing/', include('routing.urls')),
    path('status', StatusView.as_view(), name='status'),
]
