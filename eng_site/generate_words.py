import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def load_words(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        words = f.read().split()
    return [w.strip() for w in words if w.strip()]


MODELS_TO_TRY = [
    'gemini-3.1-flash-lite-preview',

    'gemini-3-flash-preview',
    'gemini-2.5-flash-lite',

    'gemma-3-27b-it'
]


def generate_json_for_batch(words_batch):
    prompt = f"""
    Ти професійний лінгвіст та викладач англійської мови. 
    Переклади наступні англійські слова українською мовою.

    Список слів: {", ".join(words_batch)}

    Поверни масив JSON об'єктів. Кожен об'єкт повинен мати строго таку структуру:
    {{
        "english_word": "слово англійською",
        "translation": "переклад українською",
        "example": "один короткий, але змістовний приклад речення англійською",
        "level": "один з: A1, A2, B1, B2, C1, C2",
        "category": "одна з: Повсякдення, Робота і Бізнес, IT та Технології, Подорожі, Їжа та Напої, Емоції та Відносини, Здоров'я та Тіло, Освіта"
    }}
    """

    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )

            if not response.text:
                continue

            return json.loads(response.text)


        except Exception as e:

            error_msg = str(e)

            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                print(f"⚠️ Ліміт для {model_name} вичерпано. Перемикаємось...")
                continue

            elif '503' in error_msg or 'UNAVAILABLE' in error_msg:
                print(f"⚠️ Модель {model_name} перевантажена (503). Перемикаємось...")
                continue

            else:
                print(f"❌ Невідома помилка для {model_name}: {e}")
                continue

    print("🛑 ВСІ МОДЕЛІ ВИЧЕРПАНО! Сесію доведеться зупинити.")
    return None


def main():
    source_file = 'raw_words.txt'
    output_file = 'words_final.json'

    if not os.path.exists(source_file):
        print(f"Файл {source_file} не знайдено!")
        return

    all_source_words = load_words(source_file)

    already_done_words = set()
    existing_data = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                already_done_words = {item['english_word'].lower() for item in existing_data}
        except:
            existing_data = []

    words_to_process = [w for w in all_source_words if w.lower() not in already_done_words]

    total_total = len(all_source_words)
    to_do_count = len(words_to_process)

    print(f"📊 Всього у файлі: {total_total}")
    print(f"✅ Вже оброблено: {len(already_done_words)}")
    print(f"🚀 Залишилось зробити: {to_do_count}")

    if to_do_count == 0:
        print("Всі слова вже оброблені!")
        return

    batch_size = 150
    all_results = existing_data

    for i in range(0, to_do_count, batch_size):
        batch = words_to_process[i:i + batch_size]
        print(f"⏳ Обробка пачки ({i + 1}/{to_do_count})...")

        batch_result = generate_json_for_batch(batch)

        if batch_result is None:
            print("Зупиняємо скрипт. Спробуйте завтра.")
            break

        if batch_result:
            all_results.extend(batch_result)

        if batch_result:
            all_results.extend(batch_result)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=4)
        else:
            print("🛑 Квоту вичерпано остаточно. Спробуйте через кілька годин або завтра.")
            break

        time.sleep(10)

    print(f"🏁 Сесію завершено. Прогрес збережено у {output_file}.")


if __name__ == '__main__':
    main()
