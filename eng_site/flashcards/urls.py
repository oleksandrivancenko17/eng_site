from django.urls import path
from flashcards import views


app_name = 'flashcards'

urlpatterns = [
    path('add/<int:word_id>/', views.add_word_to_flashcards, name='flashcards'),
]