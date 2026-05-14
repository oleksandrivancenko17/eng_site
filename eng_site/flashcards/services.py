from datetime import timedelta
from django.utils import timezone
from flashcards.models import UserWord

def process_card_review(card: UserWord, quality: str) -> None:
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


def update_user_streak(user) -> None:
    now = timezone.now()
    today = now.date()
    last_activity = user.last_activity_date

    if last_activity != today:
        if last_activity == today - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1

        user.last_activity_date = today
        user.save(update_fields=['current_streak', 'last_activity_date'])