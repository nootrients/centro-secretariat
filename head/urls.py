from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('dashboard/', views.DashboardDataView.as_view(), name='dashboard'),
]
