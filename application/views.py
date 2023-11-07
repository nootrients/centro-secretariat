from django.db.models import Q
from django.shortcuts import redirect

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from rest_framework import permissions, status
from accounts.permissions import IsOfficer, IsHeadOfficer

from .models import Applications, EligibilityConfig
from .serializer import ApplicationsSerializer, IDImageSerializer, EligibleApplicationsSerializer, EligibilityConfigSerializer
from .image_processing import extract_id_info



class EligibilityConfigView(RetrieveUpdateAPIView):
    """
    Endpoint for VIEWING and UPDATING the constraints for eligibility checking.
    """

    permission_classes = [IsHeadOfficer]
    queryset = EligibilityConfig.objects.all()
    serializer_class = EligibilityConfigSerializer
    lookup_field = 'pk'


class ApplicationForm(CreateAPIView):
    """
    Endpoint for posting/submitting a Scholarship Application.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ApplicationsSerializer

    
    # OLD || BEFORE INTEGRATING EXTRACTION
    permission_classes = [permissions.AllowAny]
    serializer_class = ApplicationsSerializer

    def perform_create(self, serializer):
        return serializer.save()
    

    '''
    def post(self, request, format=None):
        serializer = ApplicationsSerializer(data=request.data)

        if serializer.is_valid():
            # Use Django Sessions to TEMPORARILY save the data
            data = serializer.validated_data
            print(f"Data: {data}")

            # Store the national_id in temp_data
            national_id = data['national_id']
            request.session['temp_data'] = {'national_id': national_id}
            print(f"national_id: {national_id}")

            # Execute OCR Script
            extracted_data = extract_id_info(national_id)
            print(f"extracted_data: {extracted_data}")

            data.update(extracted_data)

            request.session['temp_data'] = data

            return redirect('review-and-process')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewAndProcessView(APIView):
    # Retrieve data from the session or temporary storage
    def get(self, request, format=None):
        # Retrieve the saved form data from the session
        temp_data = request.session.get('temp_data', {})
        print(f"{temp_data}")

        if not temp_data:
            # Handle the case where no form data is available
            return Response({"message": "No form data found"})

        # Display the form data for review
        return Response({"temp_data": temp_data})
'''

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