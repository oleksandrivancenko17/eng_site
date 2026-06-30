from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from grammar.models import GrammarTopic, UserTopicProgress
from grammar.serializers import TopicListSerializer, TopicDetailSerializer


class GrammarTopicViewSet(ReadOnlyModelViewSet):
    queryset = GrammarTopic.objects.annotate(total_q=Count('questions')).order_by('level')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TopicDetailSerializer
        return TopicListSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save_progress(self, request, pk=None):
        topic = self.get_object()
        score = int(request.data.get('score', 0))

        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user,
            topic=topic,
            defaults={'score': score}
        )

        if not created and score > progress.score:
            progress.score = score
            progress.save(update_fields=['score'])

        return Response({'status': 'success'})
