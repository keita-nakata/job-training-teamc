# myapp/views.py
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .models import UserDailyMission, MISSION_CHOICES, UserProfile
from .services.external_api import ichiba_item_search, books_search, games_search

DAILY_MISSION_BONUS = 50


class ApiTestView(LoginRequiredMixin, TemplateView):
    """
    楽天市場・ブックス・ゲームズの検索ページ。
    ・検索結果を表示
    ・今日のミッション達成状況を表示
    """
    template_name = "myapp/api_test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 楽天市場
        context.setdefault("ichiba_items", [])
        context.setdefault("ichiba_search_keyword", None)
        context.setdefault("ichiba_error_message", None)

        # 楽天ブックス
        context.setdefault("books_items", [])
        context.setdefault("books_search_keyword", None)
        context.setdefault("books_error_message", None)

        # 楽天ゲーム
        context.setdefault("games_items", [])
        context.setdefault("games_search_keyword", None)
        context.setdefault("games_error_message", None)

        # 今日のミッション達成状況 { "ichiba": True/False, "books": ..., "games": ... }
        today = timezone.localdate()
        missions = {code: False for code, _ in MISSION_CHOICES}

        if self.request.user.is_authenticated:
            qs = UserDailyMission.objects.filter(user=self.request.user, date=today)
            for m in qs:
                missions[m.mission_type] = m.completed

            profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
            context["user_points"] = profile.points
        else:
            context["user_points"] = 0

        context["mission_status"] = missions
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type")  # "ichiba" / "books" / "games"

        # 初期値
        ichiba_items = []
        ichiba_search_keyword = None
        ichiba_error_message = None

        books_items = []
        books_search_keyword = None
        books_error_message = None

        games_items = []
        games_search_keyword = None
        games_error_message = None

        if form_type == "ichiba":
            ichiba_search_keyword = request.POST.get("keyword", "")
            ichiba_items, ichiba_error_message = ichiba_item_search(
                ichiba_search_keyword, hits=5
            )

        elif form_type == "books":
            books_search_keyword = request.POST.get("keyword", "")
            books_items, books_error_message = books_search(
                books_search_keyword,
                hits=5,
            )

        elif form_type == "games":
            games_search_keyword = request.POST.get("keyword", "")
            games_items, games_error_message = games_search(
                games_search_keyword, hits=5
            )

        context = self.get_context_data(
            ichiba_items=ichiba_items,
            ichiba_search_keyword=ichiba_search_keyword,
            ichiba_error_message=ichiba_error_message,
            books_items=books_items,
            books_search_keyword=books_search_keyword,
            books_error_message=books_error_message,
            games_items=games_items,
            games_search_keyword=games_search_keyword,
            games_error_message=games_error_message,
        )
        return self.render_to_response(context)


class RakutenRedirectView(LoginRequiredMixin, View):
    """
    検索結果リンククリック時のビュー。
    ・該当ミッションを completed=True にする
    ・3種類すべて completed になった日に初めてボーナス付与
    """

    def get(self, request, *args, **kwargs):
        url = request.GET.get("url")
        mission_type = request.GET.get("mission")  # "ichiba" / "books" / "games"

        if not url:
            raise Http404("url パラメータがありません")

        mission_codes = {code for code, _ in MISSION_CHOICES}

        if mission_type in mission_codes and request.user.is_authenticated:
            today = timezone.localdate()

            # ① 今日のそのミッションを completed=True にする
            mission, created = UserDailyMission.objects.get_or_create(
                user=request.user,
                date=today,
                mission_type=mission_type,
                defaults={
                    "completed": True,
                    "completed_at": timezone.now(),
                },
            )
            if not created and not mission.completed:
                mission.completed = True
                mission.completed_at = timezone.now()
                mission.save(update_fields=["completed", "completed_at"])

            # ② 今日の3ミッションが全て completed かチェック
            all_completed = True
            for code, _label in MISSION_CHOICES:
                exists = UserDailyMission.objects.filter(
                    user=request.user,
                    date=today,
                    mission_type=code,
                    completed=True,
                ).exists()
                if not exists:
                    all_completed = False
                    break

            # ③ すべて completed かつ、今日まだボーナスをあげていなければポイント付与
            if all_completed:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)

                if profile.last_mission_bonus_date != today:
                    # 初めての3ミッション達成 → ボーナス付与
                    if DAILY_MISSION_BONUS > 0:
                        profile.add_points(DAILY_MISSION_BONUS)
                    profile.last_mission_bonus_date = today
                    # add_points 内でも save しているので、ここも合わせて更新
                    profile.save(update_fields=["last_mission_bonus_date"])

        return redirect(url)