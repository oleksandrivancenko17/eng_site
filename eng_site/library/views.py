import json
from django.conf import settings
from django.core.cache import cache

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView
from django.views.decorators.http import require_POST
from deep_translator import GoogleTranslator
from rest_framework.views import APIView

from library.models import Article, BookCategory

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from library.serializers import ArticleDetailSerializer, ArticleListSerializer,CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookCategory.objects.all()
    serializer_class = CategorySerializer



class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def get_queryset(self):
        queryset = Article.objects.select_related('category').all()

        search_query = self.request.query_params.get('q', '')

        levels = self.request.query_params.getlist('level')
        categories = self.request.query_params.getlist('category')

        read_status = self.request.query_params.get('status', 'all')

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_read(self, request, pk=None):
        article = self.get_object()
        article.read_by.add(request.user)
        return Response({'status': 'success'})


class TranslateWordView(APIView):
    def post(self, request):
        try:
            word = request.data.get('word', '').strip().lower()

            if not word:
                return Response({'error': 'Немає слова для перекладу'}, status=status.HTTP_400_BAD_REQUEST)

            cache_key = f'translation_en_uk_{word}'
            translation = cache.get(cache_key)

            if not translation:
                translation = GoogleTranslator(source='en', target='uk').translate(word)
                cache.set(cache_key, translation, settings.CACHE_TTL * 30)

            return Response({
                'original_word': word,
                'translation': translation
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        categories = cache.get('library_categories')
        if not categories:
            categories = BookCategory.objects.all()
            cache.set('library_categories', categories, settings.CACHE_TTL * 30)

        context['level_choices'] = Article.LEVEL_CHOICES
        context['categories'] = categories

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
        word = data.get('word', '').strip().lower()

        if not word:
            return JsonResponse({'error': 'Немає слова для перекладу'}, status=400)

        cache_key = f'translation_en_uk_{word}'
        translation = cache.get(cache_key)

        if not translation:
            translation = GoogleTranslator(source='en', target='uk').translate(word)
            cache.set(cache_key, translation, settings.CACHE_TTL * 30)


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
