from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.base import ContentFile
from datetime import datetime
import django_filters, base64, uuid

from rest_framework import permissions, status, generics
from accounts.permissions import IsOfficer, IsHeadOfficer

from .models import Applications, EligibilityConfig
from .serializer import ApplicationsSerializer, EligibleApplicationsSerializer, EligibilityConfigSerializer, ReviewFormSerializer
from .image_processing import extract_id_info

from demographics.serializer import GenderSerializer


# Constants
def base64_to_image(base64_string):
    format, imgstr = base64_string.split(';base64,')
    ext = format.split('/')[-1]
    return ContentFile(base64.b64decode(imgstr), name=uuid.uuid4().hex + "." + ext)


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

    '''
    # OLD || BEFORE INTEGRATING EXTRACTION
    permission_classes = [permissions.AllowAny]
    serializer_class = ApplicationsSerializer

    def perform_create(self, serializer):
        return serializer.save()
    '''


    def post(self, request, format=None):
        serializer = ApplicationsSerializer(data=request.data)
        response_data = {'status': 'error', 'message': 'Data processing failed.'} # new

        if serializer.is_valid():
            # Use Django Sessions to TEMPORARILY save the data
            data = serializer.validated_data
            print(f"Data: {data}")

            # Store the national_id in temp_data                           # WORKING
            national_id = data['national_id']                              # WORKING
            request.session['temp_data'] = {}                              # WORKING

            # Store all form data in temp_data                             # ADD NEW FIELDS AFTER FURTHER TESTING
            request.session['temp_data'] = {
                'national_id_name': data['national_id'].name,
                'national_id_content': data['national_id'].read(),

                'birthdate': str(data['birthdate']),
                'house_address': data['house_address'],
                'barangay': data['barangay'],
                'email_address': data['email_address'],
                'personalized_facebook_link': data['personalized_facebook_link'],
                'religion': data['religion'],
                'applicant_status': data['applicant_status'],
                'scholarship_type': data['scholarship_type'],
                'gender': data['gender'].id if data.get('gender') else None,
            }

            # Execute OCR Script
            # extracted_data = extract_id_info(national_id)                 # WORKING // REVISED
            
            extracted_data = extract_id_info(request.session['temp_data']['national_id_content'], request.session['temp_data']['national_id_name'])
            print(f"extracted_data: {extracted_data}")
            
            if extracted_data:
                temp_data = request.session.get('temp_data', {})
                temp_data.update(extracted_data)
                request.session['temp_data'] = temp_data

                national_id_content = temp_data['national_id_content']

                if national_id_content:
                    national_id_content_base64 = base64.b64encode(national_id_content).decode('utf-8')
                    temp_data['national_id_content'] = national_id_content_base64
                
                #print(f"temp_data: {temp_data}")
                
                response_data = {
                    'status': 'success',
                    'message': 'Data has been successfully processed and temporarily stored.',
                }

                review_and_process_url = reverse('review-and-process')
                return redirect(review_and_process_url)
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewAndProcessView(APIView):
    """
    Endpoint for REVIEWING and FINALIZING the submitted information in the following Scholarship Application.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        temp_data = request.session.get('temp_data', {})
        #return Response({"temp_data": temp_data})                      # Display the form data for review || WORKING // REVISED - DEPRECATED
        
        base64_content = temp_data.get('national_id_content')

        if base64_content:
            applications_data = {
                'national_id': base64_content,
                'lastname': temp_data.get('lastname'),
                'firstname': temp_data.get('firstname'),
                'middlename': temp_data.get('middlename'),
                'birthdate': temp_data.get('birthdate'),
                'house_address': temp_data.get('house_address'),
                'barangay': temp_data.get('barangay'),
                'email_address': temp_data.get('email_address'),
                'personalized_facebook_link': temp_data.get('personalized_facebook_link'),
                'religion': temp_data.get('religion'),
                'applicant_status': temp_data.get('applicant_status'),
                'scholarship_type': temp_data.get('scholarship_type'),
                'gender': temp_data.get('gender'),
            }
            return Response({"applications_data": applications_data})
    

    def post(self, request, format=None):
        temp_data = request.session.get('temp_data')

        submitted_data = request.data

        submitted_lastname = submitted_data.get('lastname')
        if submitted_lastname:
            temp_data['lastname'] = submitted_lastname

        submitted_firstname = submitted_data.get('firstname')
        if submitted_firstname:
            temp_data['firstname'] = submitted_firstname

        submitted_middlename = submitted_data.get('middlename')
        if submitted_middlename:
            temp_data['middlename'] = submitted_middlename

        # ADD MORE DEPENDING ON FIELDS THAT NEEDS OCR
        
        request.session['temp_data'] = temp_data                        # Save updated session data

        print(request.session['temp_data'])

        #serializer = ApplicationsSerializer(data=temp_data)            # WORKING
        serializer = ApplicationsSerializer(data=request.data)

        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()

            response_data = {
                'status': 'success',
                'message': 'Data has been successfully updated and saved to the database.',
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                'status': 'error',
                'message': 'Data validation failed. Please check the submitted data.',
                'errors': serializer.errors,
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


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