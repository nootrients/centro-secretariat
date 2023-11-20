from django.urls import path, include

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # POST
    # API-endpoint for submitting scholarship application
    path('', views.ApplicationForm.as_view(), name='application-form'),
    path('review-and-process/<str:application_reference_id>/', views.ReviewAndProcessView.as_view(), name='review-and-process'),

    # GET
    path('tracking/<str:application_reference_id>/', views.TrackingView.as_view(), name='tracking-details'),

    # GET (only those who passed the Automated Eligibility Checking)
    path('list/', views.EligibleApplicationsListAPIView.as_view(), name='view-eligible-applications-list'),
    path('list/<str:application_reference_id>/', views.EligibleApplicationDetailAPIView.as_view(), name='view-eligible-applications-detail'),

    path('config/<int:pk>/', views.EligibilityConfigView.as_view(), name='eligibility-config')

]+static(settings.MEDIA_URL, document_route=settings.MEDIA_ROOT)