import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser
from grammar.models import GrammarTopic, Question, Answer, UserTopicProgress


@pytest.mark.django_db
class TestGrammarAPI:

    def setup_method(self):
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(
            username='grammar_ninja',
            password='testpassword123'
        )

        self.topic = GrammarTopic.objects.create(
            title='Present Simple',
            level='A1',
            theory='Теорія про Present Simple'
        )

        self.question = Question.objects.create(
            topic=self.topic,
            question='I ___ an apple every day.',
            explanation='З займенником I використовуємо дієслово без закінчення s.'
        )

        self.answer_correct = Answer.objects.create(
            question=self.question,
            answer='eat',
            is_correct=True
        )
        self.answer_wrong = Answer.objects.create(
            question=self.question,
            answer='eats',
            is_correct=False
        )

    def test_get_topics_list(self):
        response = self.client.get('/grammar/api/v1/topics/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        results = data.get('results', [])

        assert len(results) == 1
        assert results[0]['title'] == 'Present Simple'
        assert results[0]['total_questions'] == 1
        assert results[0]['percentage'] == 0

    def test_get_topic_detail_with_nested_questions(self):
        response = self.client.get(f'/grammar/api/v1/topics/{self.topic.id}/')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data['title'] == 'Present Simple'
        assert len(data['questions']) == 1

        question_data = data['questions'][0]
        assert question_data['text'] == 'I ___ an apple every day.'
        assert len(question_data['answers']) == 2

        answers_texts = [a['text'] for a in question_data['answers']]
        assert 'eat' in answers_texts

    def test_save_progress_unauthenticated_returns_401(self):
        data = {'score': 1}
        response = self.client.post(f'/grammar/api/v1/topics/{self.topic.id}/save_progress/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_save_progress_authenticated_success(self):
        self.client.force_authenticate(user=self.user)

        data_first_try = {'score': 1}
        response = self.client.post(f'/grammar/api/v1/topics/{self.topic.id}/save_progress/', data_first_try)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status'] == 'success'

        progress = UserTopicProgress.objects.get(user=self.user, topic=self.topic)
        assert progress.score == 1

        data_second_try = {'score': 5}
        self.client.post(f'/grammar/api/v1/topics/{self.topic.id}/save_progress/', data_second_try)

        progress.refresh_from_db()
        assert progress.score == 5

        data_third_try = {'score': 2}
        self.client.post(f'/grammar/api/v1/topics/{self.topic.id}/save_progress/', data_third_try)

        progress.refresh_from_db()
        assert progress.score == 5