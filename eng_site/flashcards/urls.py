from django.urls import path, include
from django.views.generic import TemplateView

from flashcards import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/v1/cards', views.FlashcardViewSet, basename='api-flashcard')

app_name = 'flashcards'

urlpatterns = [
    path('', include(router.urls)),
    path('training/', TemplateView.as_view(template_name='flashcards/training.html'), name='training'),
]
