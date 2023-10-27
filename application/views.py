from django.db.models import Q

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView

from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from rest_framework import permissions
from accounts.permissions import IsOfficer, IsHeadOfficer

from .models import Applications
from .serializer import ApplicationsSerializer, EligibleApplicationsSerializer, EligibilityConfigSerializer



class EligibilityConfig(RetrieveUpdateAPIView):
    """
    Endpoint for VIEWING and UPDATING the constraints for eligibility checking.
    """

    permission_classes = [IsHeadOfficer]
    serializer_class = EligibilityConfigSerializer


class ApplicationForm(CreateAPIView):
    """
    Endpoint for posting/submitting a Scholarship Application.
    """
    
    permission_classes = [permissions.AllowAny]
    serializer_class = ApplicationsSerializer

    def perform_create(self, serializer):
        return serializer.save()
    

class EligibleApplicationsFilter(django_filters.FilterSet):
    class Meta:
        model = Applications
        fields = {
            'applicant_status': ['exact'],
            'scholarship_type': ['exact'],
        }


class EligibleApplicationsList(ListAPIView):
    """
    Endpoint for LISTING all the `ELIGIBLE` scholarship applications.
    """

    permission_classes = [permissions.IsAdminUser | IsOfficer]

    queryset = Applications.objects.filter(is_eligible=True)
    serializer_class = EligibleApplicationsSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = EligibleApplicationsFilter

    template = 'rest_framework/filters/base.html'


class EligibleNewApplicationsList(ListAPIView):
    """
    Endpoint for LISTING all the 'ELIGIBLE` and `NEW` scholarship applications.
    """
    
    permission_classes = [permissions.IsAdminUser | IsOfficer]

    queryset = Applications.objects.filter(Q(is_eligible=True) & Q(applicant_status='NEW_APPLICANT'))
    serializer_class = EligibleApplicationsSerializer


class EligibleRenewingApplicationsList(ListAPIView):
    """
    Endpoint for LISTING all the 'ELIGIBLE` and `RENEWING` scholarship applications.
    """
    
    permission_classes = [permissions.IsAdminUser | IsOfficer]

    queryset = Applications.objects.filter(Q(is_eligible=True) & Q(applicant_status='RENEWING_APPLICANT'))
    serializer_class = EligibleApplicationsSerializer


class ApplicationDetailView(RetrieveUpdateAPIView):
    """
    Endpoint for RETRIEVING a specific scholarship application.
    """

    permission_classes = [IsOfficer]

    queryset = Applications.objects.all()
    serializer_class = ApplicationsSerializer

    lookup_field = 'application_uuid'