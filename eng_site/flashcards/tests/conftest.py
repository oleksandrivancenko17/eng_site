import pytest
from django.utils import timezone
from users.models import CustomUser
from dictionary.models import Word
from flashcards.models import UserWord
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(
        username='testuser',
        password='testpassword123',
        email='test@example.com'
    )

@pytest.fixture
def test_word(db):
    return Word.objects.create(
        english_word='Apple',
        translation='Яблуко',
        level='A1'
    )

@pytest.fixture
def test_flashcard(db, test_user, test_word):
    return UserWord.objects.create(
        user=test_user,
        word=test_word,
        learning_level=0,
        success_counter=0,
        next_review_date=timezone.now()
    )