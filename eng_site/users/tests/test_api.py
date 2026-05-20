import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser


@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='test_student',
            password='testpassword123',
            current_streak=5
        )

    def test_get_profile_unauthenticated_returns_401(self):
        response = self.client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_authenticated_returns_200(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data['username'] == 'test_student'
        assert data['current_streak'] == 5
        assert 'email' in data

    def test_user_registration_success(self):
        self.client.logout()

        data = {
            "username": "new_tester",
            "password": "supersecurepassword123",
            "email": "tester@example.com"
        }

        response = self.client.post('/api/v1/users/register/', data)

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()

        assert response_data['username'] == 'new_tester'
        assert response_data['email'] == 'tester@example.com'

        assert 'password' not in response_data

        new_user = CustomUser.objects.get(username='new_tester')

        assert new_user.password != 'supersecurepassword123'
        assert new_user.check_password('supersecurepassword123') is True