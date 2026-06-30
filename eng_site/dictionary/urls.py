from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from dictionary import views

router = DefaultRouter()
router.register(r'words', views.WordViewSet, basename='api-word')
router.register(r'categories', views.CategoryViewSet, basename='api-category')

app_name = 'dictionary'

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('', TemplateView.as_view(template_name='dictionary/dictionary.html'), name='dictionary'),
]
