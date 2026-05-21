from rest_framework import serializers
from grammar.models import GrammarTopic, Question, Answer, UserTopicProgress

class TopicListSerializer(serializers.ModelSerializer):
    total_questions = serializers.IntegerField(source='total_q', read_only=True, default=0)
    score = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = GrammarTopic
        fields = ['id', 'title', 'level', 'theory', 'total_questions', 'score', 'percentage']

    def get_score(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            progress = UserTopicProgress.objects.filter(user=user, topic=obj).first()
            return progress.score if progress else 0
        return None


    def get_percentage(self, obj):
        score = self.get_score(obj)
        total_q = getattr(obj, 'total_q', 0)
        if score is not None and total_q > 0:
            return int(100 * (score / total_q))
        return 0


class AnswerSerializers(serializers.ModelSerializer):
    text = serializers.CharField(source='answer', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializers(many=True, read_only=True)
    text = serializers.CharField(source='question', read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'explanation', 'answers']


class TopicDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = GrammarTopic
        fields = ['id', 'title', 'level', 'theory', 'questions']
