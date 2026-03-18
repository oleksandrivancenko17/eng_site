from django.urls import path
from core import views


app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
]