from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from dictionary.models import Word
from flashcards.serializers import AddExistingWordSerializer, CustomWordCreateSerializer, FlashcardReadSerializer, ReviewCardSerializer
from flashcards.models import UserWord
from flashcards.services import process_card_review, update_user_streak


class FlashcardViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FlashcardReadSerializer

    def get_serializer_class(self):
        if self.action == 'review':
            return ReviewCardSerializer
        elif self.action == 'add_existing_word_to_flashcards':
            return AddExistingWordSerializer
        elif self.action == 'add_custom_word_to_flashcards':
            return CustomWordCreateSerializer
        return FlashcardReadSerializer

    def get_queryset(self):
        today = timezone.now()
        return UserWord.objects.filter(
            user=self.request.user,
            next_review_date__lte=today
        ).select_related('word', "word__category").order_by('next_review_date')

    @action(detail=False, methods=['get'], url_path='training-session')
    def training_session(self, request):
        queryset = self.get_queryset()

        cards_left = queryset.count()
        cards_to_review = queryset[:20]

        serializer = self.get_serializer(cards_to_review, many=True)

        return Response({
            'cards_left': cards_left,
            'cards_to_review': serializer.data
                        })

    @action(detail=True, methods=['post'])
    def review(self,request, pk=None):
        card = get_object_or_404(UserWord, pk=pk, user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        process_card_review(card, serializer.validated_data['quality'])
        update_user_streak(request.user)
        return Response({'status':'success'})



    @action(detail=False, methods=['post'], url_path='add-existing-word')
    def add_existing_word_to_flashcards(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        word = get_object_or_404(Word, id=serializer.validated_data['word_id'])
        flashcard, created = UserWord.objects.get_or_create(user=request.user, word=word)

        if created:
            return Response({'status': 'success', 'message': 'Слово додано до вивчення!'})
        else:
            return Response({'status': 'info', 'message': 'Це слово вже є у твоїх картках.'})

    @action(detail=False, methods=['post'], url_path='add-custom-word')
    def add_custom_word_to_flashcards(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        word_obj, word_created = Word.objects.get_or_create(
            english_word=serializer.validated_data['english_word'],
            translation=serializer.validated_data['translation'],
            example=serializer.validated_data['example'],
            level=serializer.validated_data['level'],
            category_id=serializer.validated_data['category_id']
        )
        flashcard, created = UserWord.objects.get_or_create(user=request.user, word=word_obj)

        if created:
            return Response({'status': 'success', 'message': 'Слово додано до вивчення!'})
        else:
            return Response({'status': 'info', 'message': 'Це слово вже є у твоїх картках.'})
