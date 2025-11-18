from django.urls import path
from .views import ApiTestView, RakutenRedirectView, RankingView

urlpatterns = [
    path("api_test/", ApiTestView.as_view(), name="api_test"),
    path("go/rakuten/", RakutenRedirectView.as_view(), name="rakuten_redirect"),
    path("ranking/", RankingView.as_view(), name="ranking"),
]