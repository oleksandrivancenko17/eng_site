import pytest
from rest_framework.test import APIClient
from dictionary.models import Word, Category
from flashcards.models import UserWord
from users.models import CustomUser


@pytest.mark.django_db
class TestDictionaryAPI:

    def setup_method(self):
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

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

        self.flashcard = UserWord.objects.create(
            user=self.user,
            word=self.word1,
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


    def test_is_learning_field_logic(self):
        response_anon = self.client.get('/dictionary/api/v1/words/')
        results_anon = response_anon.json()['results']
        assert results_anon[0]['is_learning'] is False

        self.client.force_authenticate(user=self.user)
        response_auth = self.client.get('/dictionary/api/v1/words/')
        results_auth = response_auth.json()['results']

        apple_data = next((word for word in results_auth if word['english_word'] == 'apple'))
        server_data = next((word for word in results_auth if word['english_word'] == 'server'))

        assert apple_data['is_learning'] is True
        assert server_data['is_learning'] is False


    def test_filter_words_by_custom_status(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/dictionary/api/v1/words/?status=learning')
        data_learning = response.json()
        assert data_learning['count'] == 1
        assert data_learning['results'][0]['english_word'] == 'apple'

        response_not_learning = self.client.get('/dictionary/api/v1/words/?status=not_learning')
        results_not_learning = response_not_learning.json()
        assert results_not_learning['count'] == 2

        found_words = [word['english_word'] for word in results_not_learning['results']]
        assert 'server' in found_words
        assert 'application' in found_words



@pytest.mark.django_db
class TestCategoryAPI:

    def setup_method(self):
        self.client = APIClient()
        self.category_food = Category.objects.create(name="Food")
        self.category_it = Category.objects.create(name="IT")

    def test_get_categories_list_returns_200(self):
        response = self.client.get('/dictionary/api/v1/categories/')

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['name'] == 'Food'

    def test_get_single_category_returns_200(self):
        response = self.client.get(f'/dictionary/api/v1/categories/{self.category_food.id}/')

        assert response.status_code == 200

        data = response.json()
        assert data['name'] == 'Food'

    def test_get_non_existent_category_returns_404(self):
        response = self.client.get('/dictionary/api/v1/categories/999/')
        assert response.status_code == 404


