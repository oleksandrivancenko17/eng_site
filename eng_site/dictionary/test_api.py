import pytest
from rest_framework.test import APIClient
from dictionary.models import Word, Category


@pytest.mark.django_db
class TestDictionaryAPI:

    def setup_method(self):
        self.client = APIClient()

        # Create two different categories for testing
        self.category_food = Category.objects.create(name="Food")
        self.category_it = Category.objects.create(name="IT")

        # Create 3 words with different levels and texts to test search and filtering
        self.word1 = Word.objects.create(
            english_word='apple',
            translation='яблуко',
            level='A1',
            category=self.category_food
        )
        self.word2 = Word.objects.create(
            english_word='server',
            translation='сервер',
            level='B2',
            category=self.category_it
        )
        self.word3 = Word.objects.create(
            english_word='application',
            translation='додаток',
            level='B1',
            category=self.category_it
        )

    def test_get_words_list_returns_200(self):
        response = self.client.get('/dictionary/api/v1/words/')

        assert response.status_code == 200

        data = response.json()
        assert data['count'] == 3

    def test_get_single_word_returns_200(self):
        response = self.client.get(f'/dictionary/api/v1/words/{self.word1.id}/')

        assert response.status_code == 200

        data = response.json()
        assert data['english_word'] == 'apple'

    def test_get_non_existent_word_returns_404(self):
        response = self.client.get('/dictionary/api/v1/words/999/')
        assert response.status_code == 404

    def test_filter_words_by_level(self):
        response = self.client.get('/dictionary/api/v1/words/?level=B2')

        assert response.status_code == 200

        data = response.json()
        assert data['count'] == 1
        assert data['results'][0]['english_word'] == 'server'

    def test_search_words_by_text(self):
        response = self.client.get('/dictionary/api/v1/words/?search=app')

        assert response.status_code == 200

        data = response.json()
        assert data['count'] == 2

        found_words = [word['english_word'] for word in data['results']]
        assert 'apple' in found_words
        assert 'application' in found_words
        assert 'server' not in found_words