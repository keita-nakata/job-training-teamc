# myapp/views.py
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


from .models import UserDailyMission, MISSION_CHOICES, UserProfile
from .services.external_api import ichiba_item_search, books_search, games_search, hotel_ranking
from .forms import SimpleSignUpForm

User = get_user_model()

# points for each mission type
POINTS_PER_MISSION = {
    "ichiba": 1,  # 楽天市場ミッション
    "hotel": 1,   # 楽天トラベルミッション
    "games": 1,   # 楽天ゲームズミッション
}

# bonus points for completing all daily missions
DAILY_MISSION_BONUS = 5


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
    ・そのミッションを初めて達成したときに基本ポイントを付与
    ・3種類すべて completed になった日に初めてボーナスを付与
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

            newly_completed = False

            if created:
                # レコード新規作成 = その時点で達成扱い
                newly_completed = True
            elif not mission.completed:
                # 既存レコードだがまだ未達成 → 今回のクリックで達成
                mission.completed = True
                mission.completed_at = timezone.now()
                mission.save(update_fields=["completed", "completed_at"])
                newly_completed = True

            # プロフィール取得（ポイント管理用）
            profile, _ = UserProfile.objects.get_or_create(user=request.user)

            # ② 初めて達成したミッションには基本ポイントを付与
            if newly_completed:
                base_point = POINTS_PER_MISSION.get(mission_type, 0)
                if base_point > 0:
                    profile.add_points(base_point)

            # ③ 今日の3ミッションが全て completed かチェック
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

            # ④ すべて completed かつ、今日まだボーナスをあげていなければボーナス付与
            if all_completed and profile.last_mission_bonus_date != today:
                if DAILY_MISSION_BONUS > 0:
                    profile.add_points(DAILY_MISSION_BONUS)
                profile.last_mission_bonus_date = today
                profile.save(update_fields=["last_mission_bonus_date"])

        return redirect(url)

    
class RankingView(LoginRequiredMixin, TemplateView):
    """
    全ユーザのポイントランキングを表示するページ。
    """
    template_name = "myapp/ranking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # まず全 UserProfile を取得して user_id -> points の辞書にする
        profiles = {
            p.user_id: p.points
            for p in UserProfile.objects.select_related("user")
        }

        # 全ユーザを取得し、「ポイント（なければ0）」付きのリストを作成
        users = User.objects.all()
        ranking_list = []
        for user in users:
            points = profiles.get(user.id, 0)
            ranking_list.append({
                "user": user,
                "points": points,
            })

        # ポイント降順、同点ならユーザーID昇順でソート
        ranking_list.sort(key=lambda x: (-x["points"], x["user"].id))

        # 自分の順位も計算しておく（1位スタート）
        current_user_rank = None
        for idx, entry in enumerate(ranking_list, start=1):
            if entry["user"] == self.request.user:
                current_user_rank = idx
                break

        context["ranking_list"] = ranking_list
        context["current_user_rank"] = current_user_rank
        return context
    
class BaseMissionView(LoginRequiredMixin, TemplateView):
    """
    ミッション共通のコンテキスト（今日の達成状況 + ユーザーポイント）を渡すためのベースクラス
    """

    def _add_mission_context(self, context):
        today = timezone.localdate()
        missions = {code: False for code, _ in MISSION_CHOICES}

        qs = UserDailyMission.objects.filter(user=self.request.user, date=today)
        for m in qs:
            missions[m.mission_type] = m.completed

        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context.setdefault("user_points", profile.points)
        context.setdefault("mission_status", missions)
        return context


class IchibaSearchView(BaseMissionView):
    template_name = "myapp/ichiba_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("items", [])
        context.setdefault("search_keyword", None)
        context.setdefault("error_message", None)
        return self._add_mission_context(context)

    def post(self, request, *args, **kwargs):
        search_keyword = request.POST.get("keyword", "")
        items, error_message = ichiba_item_search(search_keyword, hits=5)

        context = self.get_context_data(
            items=items,
            search_keyword=search_keyword,
            error_message=error_message,
        )
        return self.render_to_response(context)


class BooksSearchView(BaseMissionView):
    template_name = "myapp/books_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("items", [])
        context.setdefault("search_keyword", None)
        context.setdefault("error_message", None)
        return self._add_mission_context(context)

    def post(self, request, *args, **kwargs):
        search_keyword = request.POST.get("keyword", "")
        items, error_message = books_search(search_keyword, hits=5)

        context = self.get_context_data(
            items=items,
            search_keyword=search_keyword,
            error_message=error_message,
        )
        return self.render_to_response(context)


class GamesSearchView(BaseMissionView):
    template_name = "myapp/games_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("items", [])
        context.setdefault("search_keyword", None)
        context.setdefault("error_message", None)
        return self._add_mission_context(context)

    def post(self, request, *args, **kwargs):
        search_keyword = request.POST.get("keyword", "")
        items, error_message = games_search(search_keyword, hits=5)

        context = self.get_context_data(
            items=items,
            search_keyword=search_keyword,
            error_message=error_message,
        )
        return self.render_to_response(context)
    
class HotelRankingView(BaseMissionView):
    template_name = "myapp/hotel_ranking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ?genre=all / ?genre=onsen / ?genre=premium などで切り替え
        genre = self.request.GET.get("genre", "all")

        items, error_message = hotel_ranking(genre=genre)

        context.setdefault("items", items)
        context.setdefault("error_message", error_message)
        context.setdefault("selected_genre", genre)

        return self._add_mission_context(context)

def landing(request):
    return render(request, "myapp/landing.html")


def signup_view(request):
    if request.method == "POST":
        form = SimpleSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()       # saves username + password in database
            auth_login(request, user)
            return redirect("myapp:dashboard")
    else:
        form = SimpleSignUpForm()
    return render(request, "myapp/signup.html", {"form": form})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        return redirect("myapp:dashboard")
    return render(request, "myapp/login.html", {"form": form})

def get_user_rank(points: int) -> str:
    if points >= 5:
        return "Gold"
    elif points >= 2:
        return "Silver"
    else:
        return "Bronze"

@login_required(login_url="myapp:login")
def dashboard(request):
    today = timezone.localdate()

    # 今日のミッション達成状況 { "ichiba": True/False, "hotel": ..., "games": ... }
    missions = {code: False for code, _ in MISSION_CHOICES}
    qs = UserDailyMission.objects.filter(user=request.user, date=today)
    for m in qs:
        missions[m.mission_type] = m.completed
        
    # 今日完了したタスク数
    completed_mission_num = sum(1 for done in missions.values() if done)
    # ミッション総数（今は 3）
    total_missions = len(MISSION_CHOICES)

    # ユーザープロフィール取得
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    rank = get_user_rank(profile.points)

    # 各タスクの報酬ポイント
    mission_rewards = {
        "ichiba": POINTS_PER_MISSION.get("ichiba", 0),
        "hotel": POINTS_PER_MISSION.get("hotel", 0), 
        "games": POINTS_PER_MISSION.get("games", 0),
    }
    
    print("DEBUG completed_mission_num =", completed_mission_num)


    context = {
        "mission_status": missions,
        "mission_rewards": mission_rewards,
        "user_points": profile.points,
        "DAILY_MISSION_BONUS": DAILY_MISSION_BONUS,
        "completed_mission_num": completed_mission_num, 
        "total_missions": total_missions, 
        "rank": rank,
    }
    return render(request, "myapp/dashboard.html", context)

@login_required(login_url="myapp:login")
def logout_view(request):
    """
    シンプルなログアウトビュー。
    POSTで呼ばれたらログアウトして、ログインページに飛ばす。
    """
    if request.method == "POST":
        auth_logout(request)
        return redirect("myapp:login")
    # GETで来た場合はダッシュボードに戻す（直接叩かれたとき用）
    return redirect("myapp:dashboard")