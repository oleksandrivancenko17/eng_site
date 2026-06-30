from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers

from grammar.views import GrammarTopicViewSet

router = routers.DefaultRouter()
router.register(r'topics', GrammarTopicViewSet)

app_name = 'grammar'

urlpatterns = [
    # API Routes
    path('api/v1/', include(router.urls)),

    # UI Routes (SPA Shells)
    path('topics/', TemplateView.as_view(template_name='grammar/topic_list.html'), name='topic_list'),

    path('test/<int:pk>/', TemplateView.as_view(template_name='grammar/take_test.html'), name='take_test'),
]