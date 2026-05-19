import pytest
from rest_framework import status

@pytest.mark.django_db
def test_get_cards_unauthenticated_user(api_client):
    response = api_client.get('/flashcards/api/v1/cards/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_get_cards_authenticated_user(api_client, test_user, test_flashcard):

    api_client.force_authenticate(user=test_user)

    response = api_client.get('/flashcards/api/v1/cards/')

    assert response.status_code == status.HTTP_200_OK

    assert len(response.data) > 0
    assert response.data['results'][0]['id'] == test_flashcard.id
    assert response.data['results'][0]['english_word'] == "Apple"
    assert response.data['results'][0]['translation'] == "Яблуко"


@pytest.mark.django_db
def test_review_card_endpoint(api_client, test_user, test_flashcard):

    api_client.force_authenticate(user=test_user)

    url = f'/flashcards/api/v1/cards/{test_flashcard.id}/review/'

    data = {'quality': 'hard'}

    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'

    test_flashcard.refresh_from_db()
    assert test_flashcard.success_counter == 1
