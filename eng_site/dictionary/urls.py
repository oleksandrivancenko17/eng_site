from django.urls import path, include
from rest_framework.routers import DefaultRouter
from dictionary import views

router = DefaultRouter()
router.register(r'words', views.WordViewSet, basename='api-word')


app_name = 'dictionary'

urlpatterns = [
    path('', views.DictionaryListView.as_view(), name='dictionary'),

    path('api/v1/', include(router.urls)),
]