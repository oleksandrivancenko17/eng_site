import json

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView
from django.views.decorators.http import require_POST
from deep_translator import GoogleTranslator

from library.models import Article, BookCategory


class ArticleListView(ListView):
    model = Article
    template_name = 'library/reading_list.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        queryset = Article.objects.select_related('category').all()

        search_query = self.request.GET.get('q', '')

        levels = self.request.GET.getlist('level')
        categories = self.request.GET.getlist('category')

        read_status = self.request.GET.get('status', 'all')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
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


class ArticleDetailView(TemplateView):
    template_name = 'library/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = Article.objects.get(pk=self.kwargs['pk'])

        is_read = False
        if self.request.user.is_authenticated:
            if article.read_by.filter(id=self.request.user.id).exists():
                is_read = True

        context = {
            'id': article.id,
            'title': article.title,
            'description': article.description,
            'content': article.content,
            'level': article.level,
            'category_id': article.category.id if article.category else '',
            'is_read': is_read,
        }

        return context


@require_POST
def translate_word(request):
    try:
        data = json.loads(request.body)
        word = data.get('word', '').strip()

        if not word:
            return JsonResponse({'error': 'Немає слова для перекладу'}, status=400)

        translation = GoogleTranslator(source="en", target="uk").translate(word)

        return JsonResponse({
            'original_word': word,
            'translation': translation
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def mark_article_read(request, article_id):
    try:
        article = get_object_or_404(Article, id=article_id)
        article.read_by.add(request.user)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
