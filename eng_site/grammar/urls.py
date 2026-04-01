from django.urls import path
from grammar.views import *

app_name = 'grammar'
urlpatterns = [
    path('', TopicListView.as_view(), name='topic_list'),
    path('test/<int:topic_id>/', TestDetailView.as_view(), name='take_test'),
    # Новий шлях для збереження балів
    path('test/<int:topic_id>/save/', save_progress, name='save_progress'),
]