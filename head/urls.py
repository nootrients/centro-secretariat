from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('dashboard/', views.DashboardDataView.as_view(), name='dashboard'),
    path('data/applicant-status/', views.ApplicantStatusData.as_view(), name='applicant-status-data'),
    path('data/application-status/', views.ApplicationStatusData.as_view(), name='application-status-data'),
    path('data/applicants-per-type/', views.CountPerScholarshipType.as_view(), name='applicants-per-type'),

    path('data/yearly-scholarship-performance/', views.DisplayYearlyPerformance.as_view(), name='yearly-scholarship-performance'),

    path('dashboard/download-csv/', views.DashboardDataDownloadView.as_view(), name='dashboard-download-csv'),
    path('forecasting/', views.ForecastView.as_view(), name='forecast'),
]
