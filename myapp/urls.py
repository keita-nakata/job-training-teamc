from django.urls import path
from .views import ApiTestView

urlpatterns = [
    path("api_test/", ApiTestView.as_view(), name="api_test"),
]