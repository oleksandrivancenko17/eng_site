from django.contrib import admin
from .models import GrammarTopic, Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3


# 2. Реєструємо Теми
@admin.register(GrammarTopic)
class GrammarTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'level')
    list_filter = ('level',)
    search_fields = ('title', 'theory')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'topic')
    list_filter = ('topic__level', 'topic')
    search_fields = ('question',)

    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('answer', 'question__question')