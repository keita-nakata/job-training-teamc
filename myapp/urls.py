from django.urls import path
from .views import ApiTestView, RakutenRedirectView

urlpatterns = [
    path("api_test/", ApiTestView.as_view(), name="api_test"),
    path("go/rakuten/", RakutenRedirectView.as_view(), name="rakuten_redirect"),
]