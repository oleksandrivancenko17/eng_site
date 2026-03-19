from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from dictionary.models import Word
from flashcards.models import UserWord


@login_required
@require_POST
def add_word_to_flashcards(request, word_id):
    word = get_object_or_404(Word, id=word_id)
    flashcard, created = UserWord.objects.get_or_create(user=request.user, word=word)

    if created:
        return JsonResponse({'status': 'success', 'message': 'Слово додано до вивчення!'})
    else:
        return JsonResponse({'status': 'info', 'message': 'Це слово вже є у твоїх картках.'})
