from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from dictionary.models import Category, Word
from flashcards.models import UserWord


class DictionaryListView(ListView):
    model = Word
    template_name = 'dictionary/dictionary.html'
    context_object_name = 'words'
    paginate_by = 10

    def get_queryset(self):
        queryset = Word.objects.select_related('category').all()

        search_query = self.request.GET.get('q', '')
        level_query = self.request.GET.get('level', 'all')
        category_query = self.request.GET.get('category', 'all')
        learning_status = self.request.GET.get('status', 'all')

        if search_query:
            queryset = queryset.filter(
                Q(english_word__icontains=search_query) |
                Q(translation__icontains=search_query)
            )

        if level_query and level_query != 'all':
            # startswith працює, але якщо рівень це точний збіг (напр. 'B1'), краще просто exact
            queryset = queryset.filter(level=level_query)

        if category_query and category_query != 'all':
            queryset = queryset.filter(category_id=category_query)

        if self.request.user.is_authenticated:
            if learning_status and learning_status != 'all':
                # ПЕРЕВІРКА: якщо related_name не вказано, заміни user_learning на userword
                if learning_status == 'learning':
                    queryset = queryset.filter(user_learning__user=self.request.user)
                elif learning_status == 'not_learning':
                    queryset = queryset.exclude(user_learning__user=self.request.user)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # ДОДАНО: Передаємо вибрані фільтри в шаблон, щоб форма не "скидалася"
        context['current_search'] = self.request.GET.get('q', '')
        context['current_level'] = self.request.GET.get('level', 'all')
        context['current_category'] = self.request.GET.get('category', 'all')
        context['current_status'] = self.request.GET.get('status', 'all')

        if self.request.user.is_authenticated:
            context['user_words'] = UserWord.objects.filter(
                user=self.request.user
            ).values_list('word_id', flat=True)
        else:
            context['user_words'] = []

        return context