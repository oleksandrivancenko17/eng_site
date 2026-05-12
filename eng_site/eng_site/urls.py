from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', include('users.urls', namespace='users')),
    path('', include('core.urls', namespace='core')),
    path('dictionary/', include('dictionary.urls', namespace='dictionary')),
    path('flashcards/', include('flashcards.urls', namespace='flashcards')),
    path('library/', include('library.urls', namespace='library')),
    path('grammar/', include('grammar.urls', namespace='grammar')),
]
