from dictionary.models import Category, Word

from rest_framework import viewsets, filters
from .serializers import WordSerializer, CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from dictionary.filters import WordFilter


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Word.objects.select_related('category').all()
    serializer_class = WordSerializer
    filterset_class = WordFilter

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('english_word', 'translation')


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing word categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


