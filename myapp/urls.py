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
    IchibaSearchView,
    BooksSearchView,
    GamesSearchView,
    HotelRankingView,
)

app_name = "myapp"

urlpatterns = [
    path("", landing, name="landing"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("ichiba/", IchibaSearchView.as_view(), name="ichiba_search"),
    path("books/", BooksSearchView.as_view(), name="books_search"),
    path("games/", GamesSearchView.as_view(), name="games_search"),
    path("hotels/", HotelRankingView.as_view(), name="hotel_ranking"),
    path("api_test/", ApiTestView.as_view(), name="api_test"),
    path("go/rakuten/", RakutenRedirectView.as_view(), name="rakuten_redirect"),
    path("ranking/", RankingView.as_view(), name="ranking"),
]