from django.shortcuts import render
from django.views.generic import ListView
from dictionary.models import Category, Word


class DictionaryListView(ListView):
    model = Word
    template_name = 'dictionary/dictionary.html'
    context_object_name = 'words'
    paginate_by = 10

    def get_queryset(self):
        return Word.objects.select_related('category').all()
