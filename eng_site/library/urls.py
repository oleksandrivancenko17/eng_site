from django.urls import path, include
from rest_framework import routers
from django.views.generic import TemplateView
from . import views

app_name = 'library'

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='categories')
router.register(r'articles', views.ArticleViewSet, basename='articles')

urlpatterns = [
    path('', TemplateView.as_view(template_name='library/reading_list.html'), name='list_ui'),
    path('article/<int:pk>/', TemplateView.as_view(template_name='library/article_detail.html'), name='detail_ui'),

    # Наші API маршрути
    path('api/v1/translate/', views.TranslateWordView.as_view(), name='translate_api'),
    path('api/v1/', include(router.urls)),
]