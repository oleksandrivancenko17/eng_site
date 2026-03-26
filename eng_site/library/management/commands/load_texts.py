import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings

from library.models import BookCategory, Article


class Command(BaseCommand):
    help = 'Завантажує тексти з JSON файлу в базу даних'

    def handle(self, *args, **kwargs):
        self.stdout.write("Починаємо завантаження...")

        file_path = os.path.join(settings.BASE_DIR, 'texts.json')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не знайдено: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories_added = 0
        texts_added = 0

        for item in data:

            category_obj, cat_created = BookCategory.objects.get_or_create(name=item['category'])
            if cat_created:
                categories_added += 1

            text_obj, text_created = Article.objects.get_or_create(
                title=item['title'],
                defaults={
                    'description': item['description'],
                    'content': item['content'],
                    'level': item['level'],
                    'category': category_obj
                }
            )
            if text_created:
                texts_added += 1

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Додано нових категорій: {categories_added}. Додано нових текстів: {texts_added}."
        ))

        self.stdout.write(self.style.SUCCESS("Завантаження успішно завершено!"))
