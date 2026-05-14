from django.urls import path, include
from flashcards import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/v1/cards', views.FlashcardViewSet, basename='api-flashcard')

app_name = 'flashcards'

urlpatterns = [
    path('', include(router.urls)),
    path('add/<int:word_id>/', views.add_word_to_flashcards, name='flashcards'),
    path('training/', views.training_view, name='training'),
    path('review/<int:card_id>/', views.review_card, name='review_card'),
    path('add-ajax/', views.add_custom_word_ajax, name='add_card_ajax'),
]
