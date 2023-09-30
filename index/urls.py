from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('about/', views.about_page, name = 'about'),
    path('guidelines/', views.guidelines_page, name = 'guidelines')
]
