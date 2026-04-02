
import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

MODEL_ID = 'gemini-2.5-flash'


def load_words(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        words = f.read().split()
    return [w.strip() for w in words if w.strip()]


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

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Помилка генерації: {e}")
        return []


def main():
    source_file = 'raw_words.txt'
    output_file = 'words_final.json'

    if not os.path.exists(source_file):
        print(f"Файл {source_file} не знайдено!")
        return

    words = load_words(source_file)
    total_words = len(words)
    print(f"🚀 Знайдено слів для обробки: {total_words}")

    batch_size = 40
    all_results = []

    for i in range(0, total_words, batch_size):
        batch = words[i:i + batch_size]
        print(f"⏳ Обробка слів {i + 1} - {min(i + batch_size, total_words)} із {total_words}...")

        batch_result = generate_json_for_batch(batch)
        all_results.extend(batch_result)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)

        time.sleep(4)

    print(f"✅ Генерацію успішно завершено! Дані збережено у {output_file}.")


if __name__ == '__main__':
    main()