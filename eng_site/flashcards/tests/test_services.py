import pytest
from datetime import timedelta
from django.utils import timezone
from flashcards.services import process_card_review, update_user_streak


@pytest.mark.django_db
def test_process_card_review_good(test_flashcard):
    now = timezone.now()

    process_card_review(test_flashcard, 'good')

    test_flashcard.refresh_from_db()

    assert test_flashcard.learning_level == 1
    assert test_flashcard.success_counter == 1

    expected_time = now + timedelta(minutes=60)
    assert abs((test_flashcard.next_review_date - expected_time).total_seconds()) < 2


@pytest.mark.django_db
def test_process_card_review_again(test_flashcard):
    test_flashcard.learning_level = 2
    test_flashcard.success_counter = 4
    test_flashcard.save()

    now = timezone.now()

    process_card_review(test_flashcard, 'again')
    test_flashcard.refresh_from_db()

    assert test_flashcard.learning_level == 1
    assert test_flashcard.success_counter == 0

    expected_time = now + timedelta(minutes=2)
    assert abs((test_flashcard.next_review_date - expected_time).total_seconds()) < 2


@pytest.mark.django_db
def test_update_user_streak(test_flashcard, test_user):
    yesterday = timezone.now() - timedelta(days=1)
    test_user.last_activity_date = yesterday.date()
    test_user.current_streak = 1
    test_user.save()

    update_user_streak(test_user)
    test_user.refresh_from_db()

    assert test_user.current_streak == 2
    assert test_user.last_activity_date == timezone.now().date()