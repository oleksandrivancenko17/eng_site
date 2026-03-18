from django.urls import path
from dictionary import views


app_name = 'dictionary'

urlpatterns = [
    path('', views.DictionaryListView.as_view(), name='dictionary'),
]