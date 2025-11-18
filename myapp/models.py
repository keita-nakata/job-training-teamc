# myapp/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


# =========================
# ミッション種別
# =========================
MISSION_CHOICES = [
    ("ichiba", "楽天市場"),      # 楽天市場ミッション
    ("hotel", "楽天トラベル"),   # 楽天トラベルミッション
    ("games", "楽天ゲームズ"),   # 楽天ゲームズミッション（将来実装予定でもOK）
]


# =========================
# ユーザープロフィール（ポイントなど）
# =========================
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    points = models.IntegerField(default=0)

    # ✅ 追加：最後に「3ミッション達成ボーナス」を配った日
    last_mission_bonus_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_points(self, amount: int):
        self.points += amount
        self.save(update_fields=["points", "updated_at"])

    def __str__(self):
        return f"{self.user.username} (points={self.points})"


# =========================
# 日次ミッション進捗
# =========================
class UserDailyMission(models.Model):
    """
    ユーザーごとの「その日のミッション達成状況」を表すモデル。

    例:
      user = ユーザーA
      date = 2025-11-18
      mission_type = "ichiba"
      completed = True  → その日は市場ミッション達成
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_missions",
    )
    date = models.DateField()  # 例: timezone.localdate() でセット
    mission_type = models.CharField(
        max_length=20,
        choices=MISSION_CHOICES,
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "date", "mission_type")
        ordering = ["-date", "user_id", "mission_type"]

    def mark_completed(self, when: timezone.datetime | None = None):
        """ミッション達成フラグを立てるヘルパー。"""
        if not self.completed:
            self.completed = True
            self.completed_at = when or timezone.now()
            self.save(update_fields=["completed", "completed_at"])

    def __str__(self):
        return f"{self.user.username} {self.date} {self.mission_type} completed={self.completed}"