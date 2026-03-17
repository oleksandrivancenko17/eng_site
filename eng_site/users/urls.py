from django.urls import path
from users import views


app_name = 'users'

urlpatterns = [
    path('login/', views.Login_View.as_view, name='login'),
    path('register/', views.Register_View.as_view, name='register'),
    path('logout/', views.Logout_View.as_view, name='logout'),
]