import pytest
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser
from library.models import Article, BookCategory


@pytest.mark.django_db
class TestLibraryAPI:

    def setup_method(self):
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(
            username='bookworm',
            password='testpassword123'
        )

        self.category = BookCategory.objects.create(name='Science Fiction')

        self.article = Article.objects.create(
            title='The Future of AI',
            description='Short description about AI.',
            content='This is a very long text about Artificial Intelligence...',
            level='B2',
            category=self.category
        )

    def test_get_categories_list(self):
        response = self.client.get('/library/api/v1/categories/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        results = data.get('results', data) if isinstance(data, dict) and 'results' in data else data

        assert len(results) == 1
        assert results[0]['name'] == 'Science Fiction'

    def test_get_articles_list_without_content(self):
        response = self.client.get('/library/api/v1/articles/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        results = data.get('results', data) if isinstance(data, dict) and 'results' in data else data

        assert len(results) == 1
        assert results[0]['title'] == 'The Future of AI'
        assert 'content' not in results[0]
        assert results[0]['is_read'] is False

    def test_get_article_detail_with_content(self):
        response = self.client.get(f'/library/api/v1/articles/{self.article.id}/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data['title'] == 'The Future of AI'
        assert 'content' in data
        assert data['content'] == 'This is a very long text about Artificial Intelligence...'

    def test_mark_read_authenticated(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/library/api/v1/articles/{self.article.id}/mark_read/')

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == 'success'

        self.article.refresh_from_db()
        assert self.user in self.article.read_by.all()

    @patch('library.views.GoogleTranslator.translate')
    def test_translate_word(self, mock_translate):
        mock_translate.return_value = 'яблуко'

        data = {'word': 'apple'}
        response = self.client.post('/library/api/v1/translate/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['original_word'] == 'apple'
        assert response.json()['translation'] == 'яблуко'

        response_bad = self.client.post('/library/api/v1/translate/', {'word': ''})
        assert response_bad.status_code == status.HTTP_400_BAD_REQUEST