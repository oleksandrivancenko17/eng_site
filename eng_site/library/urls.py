from django.urls import path, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'articles', views.ArticleViewSet,basename='articles')

app_name = 'library'



urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('', views.ArticleListView.as_view(), name='list'),
    path('article-deteil/<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('translate/', views.translate_word, name='translate'),
    path('api/v1/translate/', views.TranslateWordView.as_view(), name='translate_api'),
    path('article/<int:article_id>/mark-read/', views.mark_article_read, name='mark_read'),
]
