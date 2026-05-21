from rest_framework import serializers

from library.models import Article, BookCategory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = ['id', 'name']


class ArticleListSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = ['id', 'title', 'description', 'level', 'category', 'is_read']


    def get_is_read(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.read_by.filter(id=user.id).exists()
        return False


class ArticleDetailSerializer(ArticleListSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title','content', 'description', 'level', 'category', 'is_read']

