from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardUI.as_view(), name='dashboard'),

    path('api/v1/dashboard/stats/', views.DashboardStatsAPIView.as_view(), name='dashboard_stats'),
]