from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class GrammarTopic(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name="Title")
    level = models.CharField(max_length=2, default="A1", verbose_name="Level")
    theory = models.TextField(blank=True, verbose_name="Theory")

    def __str__(self):
        return f"{self.title}-{self.level}"

    class Meta:
        verbose_name = "Grammar Topic"
        verbose_name_plural = "Grammar Topics"
        ordering = ['level', 'title']


class Question(models.Model):
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='questions', verbose_name="Title")
    question = models.TextField(max_length=500, verbose_name="Question")
    explanation = models.TextField(max_length=500, blank=True, verbose_name="Explanation")

    def __str__(self):
        return f"{self.topic.title}-{self.question}"

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['topic', 'id']


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Question")
    answer = models.TextField(max_length=200, verbose_name="Answer")
    is_correct = models.BooleanField(default=False, verbose_name="Correct")

    def __str__(self):
        return f"{self.question}-{self.answer}--{self.is_correct}"

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        ordering = ['question', '-is_correct']


class UserTopicProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grammar_progress')
    topic = models.ForeignKey(GrammarTopic, on_delete=models.CASCADE, related_name='user_progress')
    score = models.IntegerField(default=0, verbose_name="Кількість правильних")

    class Meta:
        unique_together = ['user', 'topic']

    def __str__(self):
        return f"{self.user.username} - {self.topic.title} ({self.score})"