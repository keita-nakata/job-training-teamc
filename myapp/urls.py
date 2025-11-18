from django.urls import path
from .views import (
    landing,
    signup_view,
    login_view,
    dashboard,
    logout_view,
    ApiTestView,
    RakutenRedirectView,
    RankingView,
)

app_name = "myapp"

urlpatterns = [
    path("", landing, name="landing"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("api_test/", ApiTestView.as_view(), name="api_test"),
    path("go/rakuten/", RakutenRedirectView.as_view(), name="rakuten_redirect"),
    path("ranking/", RankingView.as_view(), name="ranking"),
]