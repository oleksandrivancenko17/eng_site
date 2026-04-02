import requests


def download_words():
    # Використовуємо репозиторій jnoodle
    url = "https://raw.githubusercontent.com/jnoodle/English-Vocabulary-Word-List/master/Oxford%205000.txt"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка, чи все ок

        with open('source_words.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"Успішно завантажено! Файл source_words.txt створено.")
    except Exception as e:
        print(f"Знову біда: {e}")


if __name__ == "__main__":
    download_words()