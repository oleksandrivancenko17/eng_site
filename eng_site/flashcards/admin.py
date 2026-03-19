from django.contrib import admin

from flashcards.models import UserWord


@admin.register(UserWord)
class UserWordAdmin(admin.ModelAdmin):
    list_display = ["id","word", "user","learning_level","next_review_date"]
    search_fields = ["user__username","word__english_word"]
    list_filter = ["learning_level","next_review_date"]

