from django.conf import settings
from django.db import models


class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорія книги'
        verbose_name_plural = 'Категорії книг'
        ordering = ('name',)


class Article(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'A1 (Початковий)'),
        ('A2', 'A2 (Базовий)'),
        ('B1', 'B1 (Середній)'),
        ('B2', 'B2 (Вище середнього)'),
        ('C1', 'C1 (Просунутий)'),
        ('C2', 'C2 (Вільне володіння)'),
    ]

    title = models.CharField(max_length=100, unique=True, verbose_name='Title')
    description = models.TextField(max_length=200, verbose_name='Description')
    content = models.TextField(verbose_name='Content')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default="A1", verbose_name='Level')

    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='articles',
                                 verbose_name="category")

    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_articles',
        blank=True,
        verbose_name="Прочитано користувачами"
    )

    def __str__(self):
        return f"{self.title}-level-{self.level}-category-{self.category}"

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ('title',)


