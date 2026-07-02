import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings

from dictionary.models import Category, Word


class Command(BaseCommand):
    help = 'Завантажує слова з JSON файлу в базу даних без дублювання'

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

        # 1. Завантажуємо всі існуючі англійські слова з бази у множину (set)
        # Це працює блискавично швидко (О(1) для пошуку)
        existing_words = set(Word.objects.values_list('english_word', flat=True))

        for item in data:
            eng_word = item['english_word']

            # 2. Якщо слово вже є в базі — просто пропускаємо цю ітерацію циклу
            if eng_word in existing_words:
                continue

            cat_name = item['category']
            if cat_name not in category_cache:
                category_obj, _ = Category.objects.get_or_create(name=cat_name)
                category_cache[cat_name] = category_obj
                categories_added += 1

            category_obj = category_cache[cat_name]

            words_to_create.append(Word(
                english_word=eng_word,
                translation=item.get('translation', ''),
                example=item.get('example', ''),
                level=item.get('level', 'A1'),
                category_id=category_obj.id
            ))

        # 3. Зберігаємо лише якщо є нові слова
        if words_to_create:
            Word.objects.bulk_create(words_to_create, batch_size=500, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f"Готово! Додано нових категорій: {categories_added}. Додано нових слів: {len(words_to_create)}."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "Нових слів не знайдено. Всі слова з файлу вже є в базі."
            ))

        self.stdout.write(self.style.SUCCESS("Завантаження успішно завершено!"))