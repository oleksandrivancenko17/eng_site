from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import TemplateView
from users import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'users'

urlpatterns = [
    path('login/', TemplateView.as_view(template_name='users/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='users/register.html'), name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    path('api/v1/users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('api/v1/users/register/', views.UserRegisterViewApi.as_view(), name='user-register'),

    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]