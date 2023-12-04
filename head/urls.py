from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('dashboard/', views.DashboardDataView.as_view(), name='dashboard'),
    path('dashboard/download-csv/', views.DashboardDataDownloadView.as_view(), name='dashboard-download-csv'),
    path('forecasting/', views.ForecastView.as_view(), name='forecast'),
]
