from django.urls import path
from . import views


urlpatterns = [
    path('catechismbot/', views.catechismbot, name='catechismbot'),
]
