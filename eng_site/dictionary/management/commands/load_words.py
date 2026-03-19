import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings

from dictionary.models import Category, Word


class Command(BaseCommand):
    help = 'Завантажує слова з JSON файлу в базу даних'

    def handle(self, *args, **kwargs):
        self.stdout.write("Починаємо завантаження...")

        file_path = os.path.join(settings.BASE_DIR, 'words.json')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не знайдено: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories_added = 0
        words_added = 0

        for item in data:

            category_obj, cat_created = Category.objects.get_or_create(name=item['category'])
            if cat_created:
                categories_added += 1

            word_obj, word_created = Word.objects.get_or_create(
                english_word=item['english_word'],
                defaults={
                    'translation': item['translation'],
                    'example': item['example'],
                    'level': item['level'],
                    'category': category_obj
                }
            )
            if word_created:
                words_added += 1

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Додано нових категорій: {categories_added}. Додано нових слів: {words_added}."
        ))

        self.stdout.write(self.style.SUCCESS("Завантаження успішно завершено!"))
