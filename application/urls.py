from django.urls import path, include

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # POST
    # API-endpoint for submitting scholarship application
    path('', views.ApplicationForm.as_view(), name='application-form'),
    path('review-and-process/<str:application_reference_id>/', views.ReviewAndProcessView.as_view(), name='review-and-process'),
    path('renew/', views.RenewingForm.as_view(), name='renewing-form'),

    # GET
    path('tracking/<str:application_reference_id>/', views.TrackingView.as_view(), name='tracking-details'),

    # GET (only those who passed the Automated Eligibility Checking)
    path('list/', views.EligibleApplicationsListAPIView.as_view(), name='view-eligible-applications-list'),
    path('list/<str:application_reference_id>/', views.EligibleApplicationDetailAPIView.as_view(), name='view-eligible-applications-detail'),
    
    # For Head Officer
    path('all/', views.AllApplicationsListAPIView.as_view(), name='view-all-eligible-applications'),
    path('all/<str:application_reference_id>/', views.EligibleApplicationDetailAPIView.as_view(), name='view-all-eligible-application-detail'),

    path('config/<int:pk>/', views.EligibilityConfigView.as_view(), name='eligibility-config'),

    path('logs/', views.AuditTrail.as_view(), name='audit-trail'),

    path('univ/', views.UnivList.as_view(), name='univ-list'),
    path('courses/', views.CourseList.as_view(), name='course-list'),

]+static(settings.MEDIA_URL, document_route=settings.MEDIA_ROOT)