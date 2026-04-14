import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Завантаження змінних середовища (API ключ)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Список моделей з дублюванням для автоматичного retry при 503 помилках
MODELS_TO_TRY = [
    'gemini-3.1-flash-lite-preview',
    'gemini-3.1-flash-lite-preview',
    'gemini-3.1-flash-lite-preview',
    'gemini-3-flash-preview',
    'gemini-2.5-flash-lite',
    'gemma-3-27b-it'
]


def generate_json_for_topic(topic_name, next_topic_id, next_q_id, next_a_id):
    """
    Відправляє запит до Gemini API для генерації фікстур (тема + 20 запитань + 80 відповідей).
    Використовує карусель моделей для обробки лімітів та перевантажень.
    """
    prompt = f"""
    Ти досвідчений викладач англійської мови та методист.
    Твоє завдання — створити навчальні матеріали з граматики для теми: "{topic_name}".
    Дані потрібно повернути строго у форматі масиву JSON, який є валідним файлом Django Fixtures.

    Для цієї теми тобі потрібно згенерувати:
    1. Один об'єкт теми (model: "grammar.grammartopic").
    2. 20 запитань до цієї теми (model: "grammar.question").
    3. По 4 варіанти відповіді на кожне запитання, де лише один варіант правильний (model: "grammar.answer").

    ПРАВИЛА НУМЕРАЦІЇ (КРИТИЧНО ВАЖЛИВО):
    - Для теми використовуй pk: {next_topic_id}
    - Для запитань починай нумерацію pk з: {next_q_id} (і далі по порядку). Поле "topic" має дорівнювати {next_topic_id}.
    - Для відповідей починай нумерацію pk з: {next_a_id} (і далі по порядку). Поле "question" має вказувати на правильний pk запитання.

    СТРУКТУРА JSON:
    Поверни єдиний масив об'єктів. Кожен об'єкт має відповідати такій структурі:

    Для теми:
    {{
      "model": "grammar.grammartopic", "pk": {next_topic_id},
      "fields": {{
        "title": "Назва теми (наприклад, Present Simple)",
        "level": "Рівень складності (A1, A2, B1, B2, C1, C2)",
        "theory": "Коротке та зрозуміле пояснення правила українською мовою (2-3 речення)."
      }}
    }}

    Для питання:
    {{
      "model": "grammar.question", "pk": [ID питання],
      "fields": {{
        "topic": {next_topic_id},
        "question": "Речення англійською з пропуском, позначеним як ___",
        "explanation": "Коротке пояснення українською, чому саме така відповідь правильна."
      }}
    }}

    Для відповіді:
    {{
      "model": "grammar.answer", "pk": [ID відповіді],
      "fields": {{
        "question": [ID питання, до якого належить відповідь],
        "answer": "Варіант відповіді",
        "is_correct": true або false
      }}
    }}

    Важливі вимоги:
    1. Питання мають бути різної складності.
    2. Ніколи не використовуй Markdown форматування для тексту всередині JSON.
    3. Поверни ТІЛЬКИ валідний JSON масив без жодних додаткових коментарів.
    """

    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            if not response.text:
                continue

            return json.loads(response.text)

        except Exception as e:
            error_msg = str(e)

            # Обробка лімітів
            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                print(f"⚠️ Ліміт {model_name}. Перемикання...")
                continue

            # Обробка тимчасового перевантаження сервера
            elif '503' in error_msg or 'UNAVAILABLE' in error_msg:
                print(f"⚠️ Сервер {model_name} перевантажено (503). Пауза 5 сек...")
                time.sleep(5)
                continue

            else:
                print(f"❌ Помилка API ({model_name}): {e}")
                continue

    print("🛑 Всі спроби та моделі вичерпано.")
    return None


def main():
    # Налаштування шляхів
    output_dir = 'grammar/fixtures'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'grammar_data.json')

    topics_to_generate = [
        "Verb 'to be' (Present and Past)(A1)",
        "Present Simple(A1)",
        "Past Simple(A1)",
        "Plural of nouns (Regular and Irregular)(A1)",
        "Articles (a, an, the)(A1)",
        "There is / There are(A1)",
        "Possessive adjectives and pronouns(A1)",
        "Present Continuous(A2)",
        "Past Continuous(A2)",
        "Future: 'Will' vs 'Be going to'(A2)",
        "Comparative and Superlative adjectives(A2)",
        "Countable and Uncountable nouns (much, many, a lot of)(A2)",
        "Basic Modal Verbs (can, must, should)(A2)",
        "Present Perfect(B1)",
        "Past Perfect(B1)",
        "First and Second Conditionals(B1)",
        "Passive Voice (Present and Past Simple)(B1)",
        "Gerunds and Infinitives(B1)",
        "Relative Clauses (who, which, that, where)(B1)",
        "Present Perfect Continuous(B2)",
        "Past Perfect Continuous(B2)",
        "Third Conditional(B2)",
        "Reported Speech (Statements and Questions)(B2)",
        "Modal verbs of deduction (must be, can't be, might have)(B2)",
        "Used to vs Be used to vs Get used to(B2)",
        "Future Perfect and Future Continuous(C1)",
        "Mixed Conditionals(C1)",
        "Inversion (Negative and Restrictive Words)(C1)",
        "Causative Form (have/get something done)(C1)",
        "Participle Clauses(C2)",
        "The Subjunctive Mood(C2)",
        "Cleft Sentences (It was... that...)(C2)"
    ]

    for i, current_topic in enumerate(topics_to_generate, start=1):
        # 1. Читання існуючого файлу для підрахунку ID
        all_results = []
        next_topic_id = 1
        next_q_id = 1
        next_a_id = 1

        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
                    # Динамічний підрахунок поточних Primary Keys
                    next_topic_id = sum(1 for item in all_results if item.get('model') == 'grammar.grammartopic') + 1
                    next_q_id = sum(1 for item in all_results if item.get('model') == 'grammar.question') + 1
                    next_a_id = sum(1 for item in all_results if item.get('model') == 'grammar.answer') + 1
            except json.JSONDecodeError:
                all_results = []

        print(f"⏳ [{i}/{len(topics_to_generate)}] Генерація: {current_topic} (ID: {next_topic_id})")

        # 2. Виклик API
        batch_result = generate_json_for_topic(current_topic, next_topic_id, next_q_id, next_a_id)

        if batch_result is None:
            print("❌ Процес зупинено через критичну помилку API.")
            break

        if batch_result:
            # 3. Збереження результатів
            all_results.extend(batch_result)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=4)
            print(f"✅ Успішно збережено.")
        else:
            break

        # Пауза між запитами для запобігання блокуванню
        time.sleep(10)

    print(f"\n🏁 Генерацію завершено. Дані збережено у {output_file}.")


if __name__ == '__main__':
    main()