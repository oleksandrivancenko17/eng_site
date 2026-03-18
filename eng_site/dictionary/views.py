from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from dictionary.models import Category, Word


class DictionaryListView(ListView):
    model = Word
    template_name = 'dictionary/dictionary.html'
    context_object_name = 'words'
    paginate_by = 10

    def get_queryset(self):
        queryset = Word.objects.select_related('category').all()

        search_query = self.request.GET.get('q')

        level_query = self.request.GET.get('level')

        category_query = self.request.GET.get('category')

        if search_query:
            queryset = queryset.filter(
                Q(english_word__icontains=search_query) |
                Q(translation__icontains=search_query)
            )


        if level_query and level_query != 'all':
            queryset = queryset.filter(
                Q(level__startswith=level_query)
            )


        if category_query and category_query != 'all':
            queryset = queryset.filter(category_id = category_query)


        return queryset

    def get_context_data(self, **kwargs):
        context = super(DictionaryListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context