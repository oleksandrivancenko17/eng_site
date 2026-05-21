from django.urls import path, include
from rest_framework import routers

from grammar.views import *

router = routers.DefaultRouter()
router.register(r'topics', GrammarTopicViewSet)


app_name = 'grammar'
urlpatterns = [
    path('', TopicListView.as_view(), name='topic_list'),
    path('test/<int:topic_id>/', TestDetailView.as_view(), name='take_test'),
    # Новий шлях для збереження балів
    path('test/<int:topic_id>/save/', save_progress, name='save_progress'),
    path('api/v1/', include(router.urls)),
]