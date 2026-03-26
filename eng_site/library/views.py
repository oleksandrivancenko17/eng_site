from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView

from library.models import Article, BookCategory


class ArticleListView(ListView):
    model = Article
    template_name = 'library/reading_list.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        queryset = Article.objects.select_related('category').all()

        search_query = self.request.GET.get('q','')

        levels = self.request.GET.getlist('level')
        categories = self.request.GET.getlist('category')

        read_status = self.request.GET.get('status', 'all')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)|
                Q(description__icontains=search_query)
            )

        if levels:
            queryset = queryset.filter(level__in=levels)

        if categories:
            queryset = queryset.filter(category_id__in=categories)

        if self.request.user.is_authenticated:
            if read_status == 'read':
                queryset = queryset.filter(read_by=self.request.user)
            elif read_status == 'unread':
                queryset = queryset.exclude(read_by=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['level_choices'] = Article.LEVEL_CHOICES
        context['categories'] = BookCategory.objects.all()

        context['current_q'] = self.request.GET.get('q', '')
        context['current_levels'] = self.request.GET.getlist('level', '')

        context['current_categories'] = [int(c) for c in self.request.GET.getlist('category') if c.isdigit()]
        context['current_status'] = self.request.GET.get('status', 'all')

        return context