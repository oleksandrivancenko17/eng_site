from django.contrib import admin
from library.models import *

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["id", "title","category", "level"]
    list_filter = ["category", "level"]
    search_fields = ["title","id"]