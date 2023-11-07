from django.urls import path, include

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # POST
    # API-endpoint for submitting scholarship application
    path('', views.ApplicationForm.as_view(), name='application-form'),
    path('review-and-process/', views.ReviewAndProcessView.as_view(), name='review-and-process'),

    # GET (only those who passed the Automated Eligibility Checking)
    path('list/', views.EligibleApplicationsList.as_view(), name='view-eligible-applications-list'),
    path('list/new/', views.EligibleNewApplicationsList.as_view(), name='view-eligible-new-applications-list'),
    path('list/new/<uuid:application_uuid>', views.ApplicationDetailView.as_view(), name='view-new-applications-detail'),
    path('list/renewing/', views.EligibleRenewingApplicationsList.as_view(), name='view-eligible-renewing-applications-list'),
    path('list/renewing/<uuid:application_uuid>', views.ApplicationDetailView.as_view(), name='view-renewing-applications-detail'),


    path('config/<int:pk>/', views.EligibilityConfigView.as_view(), name='eligibility-config')

]+static(settings.MEDIA_URL, document_route=settings.MEDIA_ROOT)