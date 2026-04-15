import json
from django.conf import settings
from django.core.cache import cache

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView

from grammar.models import GrammarTopic, UserTopicProgress


class TopicListView(ListView):
    model = GrammarTopic
    template_name = 'grammar/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        topics = cache.get('grammar_topics_annotated')
        if not topics:
            topics = list(GrammarTopic.objects.annotate(total_q=Count('questions')))
            cache.set('grammar_topics_annotated', topics, settings.CACHE_TTL * 30)

        return topics

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topics = context['topics']

        if self.request.user.is_authenticated:
            progress_records = UserTopicProgress.objects.filter(user=self.request.user)
            progress_map = {p.topic_id: p.score for p in progress_records}

            for topic in topics:
                topic.score = progress_map.get(topic.id, None)

                if topic.score is not None and topic.total_q > 0:
                    topic.percentage = int((topic.score / topic.total_q) * 100)
                else:
                    topic.percentage = 0

        return context



class TestDetailView(LoginRequiredMixin,DetailView):
    model = GrammarTopic
    template_name = "grammar/take_test.html"
    context_object_name = 'topic'
    pk_url_kwarg = 'topic_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_id = self.object.id

        cache_key = f'quiz_data_json_topic_{topic_id}'
        cached_quiz_data = cache.get(cache_key)
        if cached_quiz_data:
           context['quiz_data_json'] = cached_quiz_data['json']
           context['total_questions'] = cached_quiz_data['total']
        else:
            questions = self.object.questions.prefetch_related('answers').all()
            quiz_data = []

            for question in questions:
                answers = [{"id":a.id,"text":a.answer,"is_correct":a.is_correct} for a in question.answers.all()]
                quiz_data.append({
                    "text":question.question,
                    "explanation":question.explanation,
                    "answers":answers
                })
            quiz_json_string = json.dumps(quiz_data)
            total_q = len(questions)

            context['quiz_data_json'] = quiz_json_string
            context['total_questions'] = total_q

            cache.set(cache_key, {'json':quiz_json_string, 'total':total_q}, settings.CACHE_TTL * 30)

        return context

@login_required
@require_POST
def save_progress(request,topic_id):
    try:
        data = json.loads(request.body)
        score = data.get('score',0)
        topic = get_object_or_404(GrammarTopic, pk=topic_id)

        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user,
            topic=topic,
            defaults={'score':score}
        )

        if not created and score > progress.score:
            progress.score = score
            progress.save(update_fields=['score'])

        return JsonResponse({'status':'success'})

    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)},status=500)
