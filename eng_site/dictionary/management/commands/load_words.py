import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings

from dictionary.models import Category, Word


class Command(BaseCommand):
    help = 'Завантажує слова з JSON файлу в базу даних'

    def handle(self, *args, **kwargs):
        self.stdout.write("Починаємо завантаження...")

        file_path = os.path.join(settings.BASE_DIR, 'words_final.json')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не знайдено: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        categories_added = 0
        words_to_create = []
        category_cache = {c.name: c for c in Category.objects.all()}

        for item in data:

            cat_name = item['category']
            if cat_name not in category_cache:
                category_obj, _ = Category.objects.get_or_create(name=cat_name)
                category_cache[cat_name] = category_obj
                categories_added += 1

            category_obj = category_cache[cat_name]

            words_to_create.append(Word(
                english_word=item['english_word'],
                translation=item.get('translation',''),
                example=item.get('example',''),
                level=item.get('level','A1'),
                category_id=category_obj.id
            )
            )

        created_words = Word.objects.bulk_create(words_to_create, batch_size=500, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Додано нових категорій: {categories_added}. Додано нових слів: {len(words_to_create)}."
        ))

        self.stdout.write(self.style.SUCCESS("Завантаження успішно завершено!"))
