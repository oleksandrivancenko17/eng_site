import hashlib
from django.conf import settings
from django.core.cache import cache

from django.db.models import Q
from deep_translator import GoogleTranslator
from rest_framework.views import APIView

from library.models import Article, BookCategory
from dictionary.models import Word
from flashcards.models import UserWord

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
            text_to_translate = request.data.get('word', '').strip()

            if not text_to_translate:
                return Response({'error': 'Немає тексту для перекладу'}, status=status.HTTP_400_BAD_REQUEST)

            text_hash = hashlib.md5(text_to_translate.encode('utf-8')).hexdigest()
            cache_key = f'trans_en_uk_{text_hash}'

            translation = cache.get(cache_key)

            if not translation:
                translation = GoogleTranslator(source='en', target='uk').translate(text_to_translate)
                cache.set(cache_key, translation, settings.CACHE_TTL * 30)

            is_in_flashcards = False
            if request.user.is_authenticated:
                word_obj = Word.objects.filter(english_word__iexact=text_to_translate).first()
                if word_obj:
                    is_in_flashcards = UserWord.objects.filter(user=request.user, word=word_obj).exists()

            return Response({
                'original_word': text_to_translate,
                'translation': translation,
                'is_in_flashcards': is_in_flashcards
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)