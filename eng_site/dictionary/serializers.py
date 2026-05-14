from rest_framework import serializers
from .models import Word,Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']


class WordSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name',read_only=True)
    class Meta:
        model = Word
        fields = ['id', 'english_word','translation','example','level','category','category_name']


