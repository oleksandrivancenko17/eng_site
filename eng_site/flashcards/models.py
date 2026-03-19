from django.db import models
from django.utils import timezone

from dictionary.models import Word
from users.models import CustomUser


class UserWord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="user_words", verbose_name='User')
    word = models.ForeignKey(Word, on_delete=models.CASCADE,related_name="user_learning", verbose_name='Word')

    learning_level = models.SmallIntegerField(default=0, verbose_name='Learning Level')

    next_review_date = models.DateTimeField(default=timezone.now, verbose_name='Next Review Date')

    def __str__(self):
        return f'{self.user.username} | {self.word.english_word}  lvl-- {self.learning_level}'


    class Meta:
        db_table = 'flashcards_word'
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'

        ordering = ['next_review_date']
        constraints = [
            models.UniqueConstraint(fields=['user', 'word'], name='unique_user_word'),
        ]
