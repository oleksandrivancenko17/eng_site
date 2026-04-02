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
        texts_to_create = []
        category_cache = {c.name: c for c in BookCategory.objects.all()}

        for item in data:

            cat_name = item['category']
            if cat_name not in category_cache:
                category_obj, _ = BookCategory.objects.get_or_create(name=cat_name)
                category_cache[cat_name] = category_obj
                categories_added += 1

            category_obj = category_cache[cat_name]

            texts_to_create.append(Article(
                title=item['title'],
                description=item['description'],
                content=item['content'],
                level=item['level'],
                category_id=category_obj.id
            ))

        if texts_to_create:
            created_texts = Article.objects.bulk_create(texts_to_create, batch_size=50 ,ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Додано нових категорій: {categories_added}. Додано нових текстів: {len(texts_to_create)}."
        ))

        self.stdout.write(self.style.SUCCESS("Завантаження успішно завершено!"))
