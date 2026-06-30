from rest_framework import serializers

from flashcards.models import UserWord


class FlashcardReadSerializer(serializers.ModelSerializer):
    english_word = serializers.CharField(source='word.english_word', read_only=True)
    translation = serializers.CharField(source='word.translation', read_only=True)
    example = serializers.CharField(source='word.example', read_only=True)

    class Meta:
        model = UserWord
        fields = ['id', 'word_id', 'english_word', 'translation', 'example' , 'learning_level', 'next_review_date', 'success_counter']


class ReviewCardSerializer(serializers.Serializer):
    quality = serializers.ChoiceField(choices=['again', 'hard', 'good', 'easy'])


class CustomWordCreateSerializer(serializers.Serializer):
    english_word = serializers.CharField(required=True, max_length=300)
    translation = serializers.CharField(required=True, max_length=300)
    example = serializers.CharField(required=False, allow_blank=True, max_length=500)
    level = serializers.CharField(required=True, max_length=2)
    category_id = serializers.IntegerField(required=True)


class AddExistingWordSerializer(serializers.Serializer):
    word_id = serializers.IntegerField(required=True)

