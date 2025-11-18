from django.contrib import admin
from .models import UserProfile, UserDailyMission

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
  list_display = ("user", "points")


@admin.register(UserDailyMission)
class UserDailyMissionAdmin(admin.ModelAdmin):
  list_display = ("user", "date", "mission_type", "completed", "completed_at")
  list_filter = ("mission_type", "date", "completed")
