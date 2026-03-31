from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='list'),
    path('article-deteil/<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('translate/', views.translate_word, name='translate'),
    path('article/<int:article_id>/mark-read/', views.mark_article_read, name='mark_read'),
]
