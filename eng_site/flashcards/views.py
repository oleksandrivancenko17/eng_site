import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST
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


@login_required
@require_POST
def add_word_to_flashcards(request, word_id):
    word = get_object_or_404(Word, id=word_id)
    flashcard, created = UserWord.objects.get_or_create(user=request.user, word=word)

    if created:
        return JsonResponse({'status': 'success', 'message': 'Слово додано до вивчення!'})
    else:
        return JsonResponse({'status': 'info', 'message': 'Це слово вже є у твоїх картках.'})


@login_required
def training_view(request):
    today = timezone.now()

    cards_to_review = UserWord.objects.filter(
        user=request.user,
        next_review_date__lte=today
    ).select_related('word', "word__category").order_by('next_review_date')

    cards_left = cards_to_review.count()

    cards_queryset = cards_to_review[:20]

    cards_list = []
    for card in cards_queryset:
        cards_list.append({
            'id': card.id,
            'english_word': card.word.english_word,
            'translation': card.word.translation,
            'example': card.word.example if card.word.example else '',
            'category': card.word.category.name if card.word.category else 'Слово',
        })

    context = {
        'cards_list': cards_list,
        'cards_left': cards_left,
    }

    return render(request, 'flashcards/training.html', context)


@login_required
@require_POST
def review_card(request, card_id):
    data = json.loads(request.body)
    quality = data.get('quality')
    card = get_object_or_404(UserWord, id=card_id, user=request.user)

    now = timezone.now()

    learning_level = card.learning_level
    coefficient = 1
    success_counter = card.success_counter

    if learning_level == 0:
        learning_level = 1
    elif learning_level == 2:
        coefficient = 24

    if quality == 'again':
        card.next_review_date = now + timedelta(minutes=2)
        learning_level = 1
        success_counter = 0
    elif quality == 'hard':
        card.next_review_date = now + timedelta(minutes=5 * coefficient)
        success_counter += 1
    elif quality == 'good':
        card.next_review_date = now + timedelta(minutes=60 * coefficient)
        success_counter += 1
    elif quality == 'easy':
        card.next_review_date = now + timedelta(hours=5 * coefficient)
        success_counter += 2

    if success_counter >= 5:
        learning_level = 2
        success_counter = 1

    if success_counter == 0 and learning_level == 2:
        learning_level = 1

    card.success_counter = success_counter
    card.learning_level = learning_level

    card.save(update_fields=['next_review_date', 'learning_level', 'success_counter'])

    user = request.user
    today = now.date()
    last_activity = user.last_activity_date

    if last_activity != today:
        if last_activity == today - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1

        user.last_activity_date = today
        user.save(update_fields=['current_streak', 'last_activity_date'])

    return JsonResponse({'status': 'success'})

@require_POST
def add_custom_word_ajax(request):
    try:
        data = json.loads(request.body)
        word = data.get('word','').strip()
        translation = data.get('translation','').strip()
        example = data.get('example_usage','').strip()
        level = data.get('level','A1')
        category_id = data.get('category_id')

        if not category_id:
            category_id = None

        if not word or not translation:
            return JsonResponse({'status': 'error', 'message': 'Недостатньо даних'}, status=400)

        word_obj, word_created = Word.objects.get_or_create(
            english_word = word.capitalize(),
            defaults={
                'translation': translation,
                'example': example,
                'level': level,
                'category_id': category_id,
            }
        )


        user_word, uw_created = UserWord.objects.get_or_create(
            user=request.user,
            word=word_obj,
        )

        return JsonResponse({'status': 'success', 'created': word_created})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
