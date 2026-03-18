from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ('name',)


class Word(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'A1 (Початковий)'),
        ('A2', 'A2 (Базовий)'),
        ('B1', 'B1 (Середній)'),
        ('B2', 'B2 (Вище середнього)'),
        ('C1', 'C1 (Просунутий)'),
        ('C2', 'C2 (Вільне володіння)'),
    ]

    english_word = models.CharField(max_length=150, verbose_name="Слово англійською")
    translation = models.CharField(max_length=150, verbose_name='Переклад слова')
    example = models.TextField(blank=True, null=True, verbose_name="Приклад використання")
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='A1', verbose_name="Рівень")

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='words',
                                 verbose_name="Категорія")


    def __str__(self):
        return f'{self.english_word}--{self.translation}'


    class Meta:
        verbose_name = "Слово"
        verbose_name_plural = "Слова"
        ordering = ['english_word']
