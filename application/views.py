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
from .serializer import ApplicationsSerializer, EligibleApplicationsSerializer, EligibilityConfigSerializer
from .image_processing import extract_id_info, extract_applicant_voters

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

    def post(self, request, format=None):
        serializer = ApplicationsSerializer(data=request.data)
        response_data = {'status': 'error', 'message': 'Data processing failed.'} # new

        if serializer.is_valid():
            # Use Django Sessions to TEMPORARILY save the data
            data = serializer.validated_data
            
            request.session['temp_data'] = {}                              # Initialize session for storing temp_data

            request.session['temp_data'] = {                               # Store all form data in temp_data
            # Personal Information Section
                'national_id_name': data['national_id'].name,
                'national_id_content': data['national_id'].read(),

                'birthdate': str(data['birthdate']),
                'house_address': data['house_address'],
                'barangay': data['barangay'],
                'email_address': data['email_address'],
                'personalized_facebook_link': data['personalized_facebook_link'],
                'religion': data['religion'],
                
                'gender': data['gender'].id if data.get('gender') else None,

            # Application Validation Section
                'scholarship_type': data['scholarship_type'],
                'semester': data['semester'],
                
                'informative_copy_of_grades_name': data['informative_copy_of_grades'].name,                    # Get file name instead of the whole file for processing
                'informative_copy_of_grades_content': data['informative_copy_of_grades'].read(),               # Get file content(binary) instead of the whole file for processing
                'is_applying_for_merit': data['is_applying_for_merit'],
                
                'voter_certificate_name': data['voter_certificate'].name,                                      # Get file name instead of the whole file for processing
                'voter_certificate_content': data['voter_certificate'].read(),                                 # Get file content(binary) instead of the whole file for processing
            
            # Current Education Section
                'university_attending': data['university_attending'].id if data.get('university_attending') else None,
                
                'registration_form_name': data['registration_form'].name,                                      # Get file name instead of the whole file for processing
                'registration_form_content': data['registration_form'].read(),                                 # Get file content(binary) instead of the whole file for processing
                
                'total_units_enrolled': data['total_units_enrolled'],
                'is_ladderized': data['is_ladderized'],
                'course_taking': data['course_taking'].id if data.get('course_taking') else None,
                'year_level': data['year_level'],
                'is_graduating': data['is_graduating'],
                'course_duration': data['course_duration'],
            }
            
            # Execute OCR scripts
            extracted_id_data = extract_id_info(request.session['temp_data']['national_id_content'], request.session['temp_data']['national_id_name'])
            extracted_voters_data = extract_applicant_voters(request.session['temp_data']['voter_certificate_content'], request.session['temp_data']['voter_certificate_content'])
            
            if extracted_id_data and extracted_voters_data:
                temp_data = request.session.get('temp_data', {})

                temp_data.update(extracted_id_data)
                temp_data.update(extracted_voters_data)
                
                request.session['temp_data'] = temp_data

                # Files or Images that needs to be converted to Base64 for Serialization upon POST() method
                national_id_content = temp_data['national_id_content']
                informative_copy_of_grades_content = temp_data['informative_copy_of_grades_content']
                voter_certificate_content = temp_data['voter_certificate_content']
                registration_form_content = temp_data['registration_form_content']

                if national_id_content and informative_copy_of_grades_content and voter_certificate_content and registration_form_content:
                    # Encode Files to Base64 format
                    national_id_content_base64 = base64.b64encode(national_id_content).decode('utf-8')
                    informative_copy_of_grades_content_base64 = base64.b64encode(informative_copy_of_grades_content).decode('utf-8')
                    voter_certificate_content_base64 = base64.b64encode(voter_certificate_content).decode('utf-8')
                    registration_form_content_base64 = base64.b64encode(registration_form_content).decode('utf-8')

                    # Store files encoded in Base64 format back to the temp_data (in session)
                    temp_data['national_id_content'] = national_id_content_base64
                    temp_data['informative_copy_of_grades_content'] = informative_copy_of_grades_content_base64
                    temp_data['voter_certificate_content'] = voter_certificate_content_base64
                    temp_data['registration_form_content'] = registration_form_content_base64
                
                print(f"temp_data: {temp_data}")

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
        
        id_base64_content = temp_data.get('national_id_content')
        icg_base64_content = temp_data.get('informative_copy_of_grades_content')                    # New
        applicant_voters_base64_content = temp_data.get('voter_certificate_content')                # New
        registration_form_base64_content = temp_data.get('registration_form_content')               # New

        if id_base64_content and icg_base64_content and applicant_voters_base64_content and registration_form_base64_content:
            applications_data = {
            # Personal Information Section
                'national_id': id_base64_content,
                'lastname': temp_data.get('lastname'),
                'firstname': temp_data.get('firstname'),
                'middlename': temp_data.get('middlename'),
                
                'birthdate': temp_data.get('birthdate'),
                'house_address': temp_data.get('house_address'),
                'barangay': temp_data.get('barangay'),
                'email_address': temp_data.get('email_address'),
                'personalized_facebook_link': temp_data.get('personalized_facebook_link'),
                'religion': temp_data.get('religion'),
                
                'gender': temp_data.get('gender'),

            # Application Validation Section
                'scholarship_type': temp_data.get('scholarship_type'),
                'semester': temp_data.get('semester'),

                'informative_copy_of_grades': icg_base64_content,
                'is_applying_for_merit': temp_data.get('is_applying_for_merit'),
                
                'voter_certificate_name': applicant_voters_base64_content,
                'years_of_residency': temp_data.get('years_of_residency'),
                'voters_issued_at': temp_data.get('voters_issued_at'),
                'voters_issuance_date': temp_data.get('voters_issuance_date'),
            
            # Current Education Section
                'university_attending': temp_data.get('university_attending'),
                
                'registration_form': registration_form_base64_content,
                
                'total_units_enrolled': temp_data.get('total_units_enrolled'),
                'is_ladderized': temp_data.get('is_ladderized'),
                'course_taking': temp_data.get('course_taking'),
                'year_level': temp_data.get('year_level'),
                'is_graduating': temp_data.get('is_graduating'),
                'course_duration': temp_data.get('course_duration'),
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