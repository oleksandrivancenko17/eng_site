from django.contrib import admin

from dictionary.models import Word, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('english_word', 'translation', 'category', 'level')

    list_filter = ('category', 'level')

    search_fields = ('english_word', 'translation')
