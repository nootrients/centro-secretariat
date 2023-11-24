import django_filters, base64, uuid

from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db import IntegrityError

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.validators import ValidationError

from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.base import ContentFile
from datetime import datetime

from rest_framework import permissions, status, generics, viewsets

from .models import Applications, EligibilityConfig, TempApplications, PartneredUniversities, Courses, StatusUpdate
from .serializer import TempApplicationsSerializer, TempApplicationsRetrievalSerializer, ApplicationsSerializer, EligibleApplicationsSerializer, EligibilityConfigSerializer, ApplicationRetrieveUpdateSerializer, StatusUpdateSerializer, ApplicationsRenewalSerializer
from .image_processing import extract_id_info, extract_applicant_voters, extract_guardian_voters
from .tasks import check_eligibility

from accounts.tasks import supply_account, update_scholar_profile
from accounts.permissions import IsOfficer, IsHeadOfficer, IsLinkedApplicationUser
from demographics.models import Gender

# For sending custom email
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth import get_user_model


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

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]
    serializer_class = TempApplicationsSerializer

    def post(self, request, *args, **kwargs):
        serializer = TempApplicationsSerializer(data=request.data)
        
        if serializer.is_valid():
            data = request.data

            temp_data = {
                'application_reference_id': data['application_reference_id'],

                # Personal Information Section
                'national_id_name': data['national_id'].name,
                'national_id_content': data['national_id'].read(),

                'birthdate': str(data['birthdate']),
                'house_address': data['house_address'],
                'barangay': data['barangay'],
                'email_address': data['email_address'],
                'personalized_facebook_link': data['personalized_facebook_link'],
                'religion': data['religion'],

                # Application Validation Section
                'scholarship_type': data['scholarship_type'],
                'semester': data['semester'],
                    
                'informative_copy_of_grades_name': data['informative_copy_of_grades'].name,                    # Get file name instead of the whole file for processing
                'informative_copy_of_grades_content': data['informative_copy_of_grades'].read(),               # Get file content(binary) instead of the whole file for processing
                'is_applying_for_merit': data.get('is_applying_for_merit'),
                #'is_applying_for_merit': bool(data['is_applying_for_merit']),

                'voter_certificate_name': data['voter_certificate'].name,                                      # Get file name instead of the whole file for processing
                'voter_certificate_content': data['voter_certificate'].read(),                                 # Get file content(binary) instead of the whole file for processing
                
                # Current Education Section
                'registration_form_name': data['registration_form'].name,                                      # Get file name instead of the whole file for processing
                'registration_form_content': data['registration_form'].read(),                                 # Get file content(binary) instead of the whole file for processing
                    
                'total_units_enrolled': data['total_units_enrolled'],
                'is_ladderized': data.get('is_ladderized'),
                #'is_ladderized': bool(data['is_ladderized']),
                
                'year_level': data['year_level'],
                'is_graduating': data.get('is_graduating'),
                #'is_graduating': bool(data['is_graduating']),
                'course_duration': data['course_duration'],

                # Educational Background Section
                # Elementary
                'elementary_school': data['elementary_school'],
                'elementary_school_type': data['elementary_school_type'],
                'elementary_school_address': data['elementary_school_address'],
                'elementary_start_end': data['elementary_start_end'],

                # JHS
                'jhs_school': data['jhs_school'],
                'jhs_school_type': data['jhs_school_type'],
                'jhs_school_address': data['jhs_school_address'],
                'jhs_start_end': data['jhs_start_end'],

                # SHS
                'shs_school': data['shs_school'],
                'shs_school_type': data['shs_school_type'],
                'shs_school_address': data['shs_school_address'],
                'shs_start_end': data['shs_start_end'],

                # Guardian's Background Section
                'guardian_complete_name': data['guardian_complete_name'],
                'guardian_complete_address': data['guardian_complete_address'],
                'guardian_contact_number': data['guardian_contact_number'],
                'guardian_occupation': data['guardian_occupation'],
                'guardian_place_of_work': data['guardian_place_of_work'],
                'guardian_educational_attainment': data['guardian_educational_attainment'],

                'guardians_voter_certificate_name': data['guardians_voter_certificate'].name,                   # Get file name instead of the whole file for processing
                'guardians_voter_certificate_content': data['guardians_voter_certificate'].read(),              # Get file content(binary) instead of the whole file for processing

                # Miscellaneous Section
                'number_of_semesters_before_graduating': data['number_of_semesters_before_graduating'],
                'transferee': data['transferee'],
                'shiftee': data['shiftee'],
                'student_status': data['student_status'],
            }
                
            # Execute OCR scripts
            extracted_id_data = extract_id_info(temp_data['national_id_content'], temp_data['national_id_name'])
            extracted_voters_data = extract_applicant_voters(temp_data['voter_certificate_content'], temp_data['voter_certificate_name'])
            extracted_guardian_info_data = extract_guardian_voters(temp_data['guardians_voter_certificate_content'], temp_data['guardians_voter_certificate_name'])

            if extracted_id_data and extracted_voters_data and extracted_guardian_info_data:
                temp_data.update(extracted_id_data)
                temp_data.update(extracted_voters_data)
                temp_data.update(extracted_guardian_info_data)

                # Files or Images that needs to be converted to Base64 for Serialization upon POST() method
                national_id_content = temp_data['national_id_content']
                informative_copy_of_grades_content = temp_data['informative_copy_of_grades_content']
                voter_certificate_content = temp_data['voter_certificate_content']
                registration_form_content = temp_data['registration_form_content']
                guardians_voter_certificate_content = temp_data['guardians_voter_certificate_content']

                if national_id_content and informative_copy_of_grades_content and voter_certificate_content and registration_form_content and guardians_voter_certificate_content:
                    # Encode Files to Base64 format
                    national_id_content_base64 = base64.b64encode(national_id_content).decode('utf-8')
                    informative_copy_of_grades_content_base64 = base64.b64encode(informative_copy_of_grades_content).decode('utf-8')
                    voter_certificate_content_base64 = base64.b64encode(voter_certificate_content).decode('utf-8')
                    registration_form_content_base64 = base64.b64encode(registration_form_content).decode('utf-8')
                    guardians_voter_certificate_content_base64 = base64.b64encode(guardians_voter_certificate_content).decode('utf-8')

                    # Store files encoded in Base64 format back to the data
                    temp_data['national_id_content'] = national_id_content_base64
                    temp_data['informative_copy_of_grades_content'] = informative_copy_of_grades_content_base64
                    temp_data['voter_certificate_content'] = voter_certificate_content_base64
                    temp_data['registration_form_content'] = registration_form_content_base64
                    temp_data['guardians_voter_certificate_content'] = guardians_voter_certificate_content_base64
                
                gender_id = data['gender']
                gender_instance = Gender.objects.get(id=gender_id)
                temp_data['gender'] = gender_instance

                partnered_universities_id = data['university_attending']
                partnered_universities_instance = PartneredUniversities.objects.get(id=partnered_universities_id)
                temp_data['university_attending'] = partnered_universities_instance

                courses_id = data['course_taking']
                courses_instance = Courses.objects.get(id=courses_id)
                temp_data['course_taking'] = courses_instance

                # Fields to exclude when creating the TempApplications instance
                exclude_fields = [
                    'national_id_name',
                    'informative_copy_of_grades_name',
                    'voter_certificate_name',
                    'registration_form_name',
                    'guardians_voter_certificate_name',
                ]

                # Remove excluded fields from temp_data
                for field in exclude_fields:
                    temp_data.pop(field, None)

                serializer.validated_data.update(temp_data)

                if serializer.is_valid():
                    serializer.save()
        
            return Response({'status': 'success', 'message': 'Data has been successfully processed and stored temporarily to TempApplications'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewAndProcessView(APIView):
    """
    Endpoint for REVIEWING and FINALIZING the submitted information in the following Scholarship Application.
    """
    permission_classes = [permissions.AllowAny]

    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, application_reference_id, *args, **kwargs):
        # Retrieve the TempApplications instance using application_reference_id
        temp_application = get_object_or_404(TempApplications, application_reference_id=application_reference_id)
        serializer = TempApplicationsRetrievalSerializer(temp_application)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, application_reference_id, *args, **kwargs):
        temp_application = get_object_or_404(TempApplications, application_reference_id=application_reference_id)
        
        # Check for Unique Constraint Violation
        email_address = temp_application.email_address  # Assuming email is the field with a unique constraint
        if not Applications.objects.filter(email_address=email_address).exists():
            serializer = ApplicationsSerializer(data=request.data, partial=True)
        
            if serializer.is_valid():
                temp_data = {
                    'application_reference_id': temp_application.application_reference_id,

                    'national_id_content': temp_application.national_id.read(),
                    'lastname': temp_application.lastname,
                    'firstname': temp_application.firstname,
                    'middlename': temp_application.middlename,

                    'gender': temp_application.gender.id if temp_application.gender else None,
                    
                    'birthdate': temp_application.birthdate,
                    'house_address': temp_application.house_address,
                    'barangay': temp_application.barangay,

                    'email_address': temp_application.email_address,
                    'personalized_facebook_link': temp_application.personalized_facebook_link,
                    'religion': temp_application.religion,

                    # Application Validation Section
                    'scholarship_type': temp_application.scholarship_type,
                    'semester': temp_application.semester,

                    'informative_copy_of_grades_content': temp_application.informative_copy_of_grades.read(),
                    'is_applying_for_merit': temp_application.is_applying_for_merit,
                        
                    'voter_certificate_content': temp_application.voter_certificate.read(),
                    'years_of_residency': temp_application.years_of_residency,
                    'voters_issued_at': temp_application.voters_issued_at,
                    'voters_issuance_date': temp_application.voters_issuance_date,
                    
                    # Current Education Section
                    'university_attending': temp_application.university_attending.id if temp_application.university_attending else None,
                        
                    'registration_form_content': temp_application.registration_form.read(),
                        
                    'total_units_enrolled': temp_application.total_units_enrolled,
                    'is_ladderized': temp_application.is_ladderized,
                    'course_taking': temp_application.course_taking.id if temp_application.course_taking else None,
                    'year_level': temp_application.year_level,
                    'is_graduating': temp_application.is_graduating,
                    'course_duration': temp_application.course_duration,

                    # Educational Background Section
                    # Elementary
                    'elementary_school': temp_application.elementary_school,
                    'elementary_school_type': temp_application.elementary_school_type,
                    'elementary_school_address': temp_application.elementary_school_address,
                    'elementary_start_end': temp_application.elementary_start_end,

                    # JHS
                    'jhs_school': temp_application.jhs_school,
                    'jhs_school_type': temp_application.jhs_school_type,
                    'jhs_school_address': temp_application.jhs_school_address,
                    'jhs_start_end': temp_application.jhs_start_end,

                    # SHS
                    'shs_school': temp_application.shs_school,
                    'shs_school_type': temp_application.shs_school_type,
                    'shs_school_address': temp_application.shs_school_address,
                    'shs_start_end': temp_application.shs_start_end,

                    # Guardian's Section
                    'guardian_complete_name': temp_application.guardian_complete_name,
                    'guardian_complete_address': temp_application.guardian_complete_address,
                    'guardian_contact_number': temp_application.guardian_contact_number,
                    'guardian_occupation': temp_application.guardian_occupation,
                    'guardian_place_of_work': temp_application.guardian_place_of_work,
                    'guardian_educational_attainment': temp_application.guardian_educational_attainment,

                    'guardians_voter_certificate_content': temp_application.guardians_voter_certificate.read(),
                    'guardians_years_of_residency': temp_application.guardians_years_of_residency,
                    'guardians_voters_issued_at': temp_application.guardians_voters_issued_at,
                    'guardians_voters_issuance_date': temp_application.guardians_voters_issuance_date,
                    
                    # Miscellaneous Section
                    'number_of_semesters_before_graduating': temp_application.number_of_semesters_before_graduating,
                    'transferee': temp_application.transferee,
                    'shiftee': temp_application.shiftee,
                    'student_status': temp_application.student_status,
                }

                submitted_data = request.data

                # Updating fields in temp_data that are being updated through request
                submitted_lastname = submitted_data.get('lastname')
                if submitted_lastname:
                    temp_data['lastname'] = submitted_lastname

                submitted_firstname = submitted_data.get('firstname')
                if submitted_firstname:
                    temp_data['firstname'] = submitted_firstname

                submitted_middlename = submitted_data.get('middlename')
                if submitted_middlename:
                    temp_data['middlename'] = submitted_middlename

                # Handle file data
                national_id_content = temp_data['national_id_content']
                informative_copy_of_grades_content = temp_data['informative_copy_of_grades_content']
                voter_certificate_content = temp_data['voter_certificate_content']
                registration_form_content = temp_data['registration_form_content']
                guardians_voter_certificate_content = temp_data['guardians_voter_certificate_content']

                if (national_id_content and informative_copy_of_grades_content and voter_certificate_content and registration_form_content and guardians_voter_certificate_content
                ):
                    # Encode Files to Base64 format
                    national_id_content_base64 = base64.b64encode(national_id_content).decode('utf-8')
                    informative_copy_of_grades_content_base64 = base64.b64encode(informative_copy_of_grades_content).decode('utf-8')
                    voter_certificate_content_base64 = base64.b64encode(voter_certificate_content).decode('utf-8')
                    registration_form_content_base64 = base64.b64encode(registration_form_content).decode('utf-8')
                    guardians_voter_certificate_content_base64 = base64.b64encode(guardians_voter_certificate_content).decode('utf-8')

                    # Store files encoded in Base64 format back to the data
                    temp_data['national_id_content'] = national_id_content_base64
                    temp_data['informative_copy_of_grades_content'] = informative_copy_of_grades_content_base64
                    temp_data['voter_certificate_content'] = voter_certificate_content_base64
                    temp_data['registration_form_content'] = registration_form_content_base64
                    temp_data['guardians_voter_certificate_content'] = guardians_voter_certificate_content_base64

                gender_id = temp_application.gender.id
                gender_instance = Gender.objects.get(id=gender_id)
                temp_data['gender'] = gender_instance

                partnered_universities_id = temp_application.university_attending.id
                partnered_universities_instance = PartneredUniversities.objects.get(id=partnered_universities_id)
                temp_data['university_attending'] = partnered_universities_instance

                courses_id = temp_application.course_taking.id
                courses_instance = Courses.objects.get(id=courses_id)
                temp_data['course_taking'] = courses_instance

                serializer.validated_data.update(temp_data)

                print(serializer.validated_data.keys())

                if serializer.is_valid():
                    # serializer.save()
                    saved_application_instance = serializer.save()

                    # Send email after saving the instance
                    context = {
                        "firstname": serializer.validated_data.get('firstname'),
                        "lastname": serializer.validated_data.get('lastname'),
                        "application_reference_id": serializer.validated_data.get('application_reference_id')
                    }

                    html_message = render_to_string("content/application_received_email.html", context=context)
                    plain_message = strip_tags(html_message)

                    message = EmailMultiAlternatives(
                        subject = "Scholarship Application",
                        body = plain_message,
                        from_email = None,
                        to = [serializer.data.get('email_address'),]
                    )

                    message.attach_alternative(html_message, "text/html")
                    message.send()

                    # Constant values after creation of an Application instance
                    StatusUpdate.objects.create(
                        application = saved_application_instance,
                        application_reference_id = saved_application_instance.application_reference_id,
                        description = "Your scholarship application has been submitted and received by our system.",
                        current_step = 1,
                        is_active = True
                    )

                    # Initiate Automated Eligibility Checking
                    # Get the application ID after saving
                    application_id = serializer.data.get('id')

                    # Trigger Celery task for eligibility checking asynchronously
                    check_eligibility.apply_async(args=[application_id])

                    temp_application.national_id.close()
                    temp_application.informative_copy_of_grades.close()
                    temp_application.voter_certificate.close()
                    temp_application.registration_form.close()
                    temp_application.guardians_voter_certificate.close()

                    # Delete instance after transferring data to Applications model
                    temp_application.delete()

                    # # Constant values after creation of an Application instance
                    # StatusUpdate.objects.create(
                    #     application = saved_application_instance,
                    #     application_reference_id = saved_application_instance.application_reference_id,
                    #     description = "Your scholarship application has been submitted and received by our system.",
                    #     current_step = 1,
                    #     is_active = True
                    # )

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
        else:
            error_message = "An application with this email already exists."
            response_data = {
                'status': 'error',
                'message': error_message,
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)  


class EligibleApplicationsFilter(django_filters.FilterSet):
    class Meta:
        model = Applications
        fields = {
            'applicant_status': ['exact'],
            'scholarship_type': ['exact'],
        }


class EligibleApplicationsListAPIView(ListAPIView):
    """
    Endpoint for LISTING all the `ELIGIBLE` scholarship applications.
    """
    # OLD CODE
    permission_classes = [permissions.IsAdminUser | IsOfficer]

    queryset = Applications.objects.filter(is_eligible=True, application_status="PENDING", evaluated_by=None)
    serializer_class = EligibleApplicationsSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = EligibleApplicationsFilter

    template = 'rest_framework/filters/base.html'


class EligibleApplicationDetailAPIView(RetrieveUpdateAPIView):
    """
    Endpoint for retrieving the application instance's details, and for approving an application.
    """

    permission_classes = [permissions.IsAdminUser | IsOfficer]
    queryset = Applications.objects.all()
    serializer_class = ApplicationRetrieveUpdateSerializer
    lookup_field = 'application_reference_id'

    def get_object(self):
        application_reference_id = self.kwargs.get('application_reference_id')
        return get_object_or_404(Applications, application_reference_id=application_reference_id)
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            application_status = request.data.get('application_status', "PENDING")

            if application_status == "ACCEPTED":
                officer_instance = get_user_model().objects.get(pk=request.user.id)
                instance.application_status = "ACCEPTED"
                instance.evaluated_by = officer_instance
                instance.save()

                officer_profile = officer_instance.profile

                # Send email after saving the instance
                context = {
                    "firstname": instance.firstname,
                    "lastname": instance.lastname,
                    "application_reference_id": instance.application_reference_id,
                    "officer_firstname": officer_profile.firstname,
                    "officer_lastname": officer_profile.lastname,
                    "officer_instance_email": officer_instance.email
                }

                html_message = render_to_string("content/application_approved_email.html", context=context)
                plain_message = strip_tags(html_message)

                message = EmailMultiAlternatives(
                    subject = "Scholarship Application",
                    body = plain_message,
                    from_email = None,
                    to = [instance.email_address, ]
                )

                message.attach_alternative(html_message, "text/html")
                message.send()
            
            elif application_status == "REJECTED":
                officer_instance = get_user_model().objects.get(pk=request.user.id)
                instance.application_status = "REJECTED"
                instance.evaluated_by = officer_instance
                instance.save()

                officer_profile = officer_instance.profile

                # Send email after saving the instance
                context = {
                    "firstname": instance.firstname,
                    "lastname": instance.lastname,
                    "application_reference_id": instance.application_reference_id,
                    "officer_firstname": officer_profile.firstname,
                    "officer_lastname": officer_profile.lastname,
                    "officer_instance_email": officer_instance.email
                }

                html_message = render_to_string("content/application_rejected_email.html", context=context)
                plain_message = strip_tags(html_message)

                message = EmailMultiAlternatives(
                    subject = "Scholarship Application",
                    body = plain_message,
                    from_email = None,
                    to = [instance.email_address, ]
                )

                message.attach_alternative(html_message, "text/html")
                message.send()
            
            if instance.applicant_status == "NEW APPLICANT" and instance.application_status == "ACCEPTED":
                supply_account.apply_async(args=[instance.id])
            elif instance.applicant_status == "RENEWING APPLICANT" and instance.application_status == "ACCEPTED":
                update_scholar_profile.apply_async(args=[instance.id])

            existing_status_updates = StatusUpdate.objects.filter(application_reference_id=instance.application_reference_id, is_active=True)
            existing_status_updates.update(is_active=False)

            StatusUpdate.objects.create(
                application = instance,
                application_reference_id = instance.application_reference_id,
                description = f"Your scholarship application has been reviewed and evaluated by Officer {officer_profile.firstname} {officer_profile.lastname}.",
                current_step = 4,
                is_active = True
            )

            response_data = {
                'status': 'success',
                'message': 'Scholarship application has been successfully evaluated.',
            }
                
            return Response(response_data, status=status.HTTP_200_OK)
        except get_user_model().DoesNotExist:
            raise ValidationError({"detail": "User does not exist."}, status_code=status.HTTP_404_NOT_FOUND)
        # except Applications.DoesNotExist:
        #     raise ValidationError({"detail": "Application does not exist."}, status_code=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class TrackingView(ListAPIView):
    """
    Endpoint for submitting the request to track the submitted scholarship application through its reference ID.
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = StatusUpdateSerializer

    def get(self, request, *args, **kwargs):
        application_reference_id = self.kwargs.get('application_reference_id')
        
        if not self.application_reference_id_exists(application_reference_id):
            return Response({'error': 'Application does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        application = get_object_or_404(Applications, application_reference_id=application_reference_id)
        status_updates = StatusUpdate.objects.filter(application_reference_id=application_reference_id)

        data = {
            'lastname': application.lastname,
            'firstname': application.firstname,
            'middlename': application.middlename,
            'email_address': application.email_address,

            'status_updates': [
                {
                    'date_accomplished': status_update.date_accomplished,
                    'description': status_update.description,
                    'current_step': status_update.current_step,
                    'is_active': status_update.is_active,
                }
                for status_update in status_updates
            ],
        }

        return Response(data)
    
    def application_reference_id_exists(self, application_reference_id):
        try:
            get_object_or_404(Applications, application_reference_id=application_reference_id)
            return True
        except:
            return False
        

class RenewingForm(RetrieveUpdateAPIView):
    """
    Endpoint for enabling the Scholars to RENEW their scholarship application.
    """

    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Applications.objects.all()
    serializer_class = ApplicationsRenewalSerializer

    def get_object(self):
        scholar = self.request.user
        try:
            return Applications.objects.get(scholar=scholar)
        except:
            return Response({'error': 'Application does not exist for this user'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            data = request.data

            StatusUpdate.objects.filter(application=instance).delete()

            temp_data = {
                'house_address': data['house_address'],
                'barangay': data['barangay'],
                'personalized_facebook_link': data['personalized_facebook_link'],

                # Application Validation Section
                'semester': data['semester'],
                        
                'informative_copy_of_grades_name': data['informative_copy_of_grades'].name,                    # Get file name instead of the whole file for processing
                'informative_copy_of_grades_content': data['informative_copy_of_grades'].read(),               # Get file content(binary) instead of the whole file for processing
                #'is_applying_for_merit': data.get('is_applying_for_merit'),
                'is_applying_for_merit': bool(data.get('is_applying_for_merit')),

                'voter_certificate_name': data['voter_certificate'].name,                                      # Get file name instead of the whole file for processing
                'voter_certificate_content': data['voter_certificate'].read(),                                 # Get file content(binary) instead of the whole file for processing
                    
                # Current Education Section
                'registration_form_name': data['registration_form'].name,                                      # Get file name instead of the whole file for processing
                'registration_form_content': data['registration_form'].read(),                                 # Get file content(binary) instead of the whole file for processing
                        
                'total_units_enrolled': data['total_units_enrolled'],
                #'is_ladderized': data.get('is_ladderized'),
                'is_ladderized': bool(data.get('is_ladderized')),
                    
                'year_level': data['year_level'],
                #'is_graduating': data.get('is_graduating'),
                'is_graduating': bool(data.get('is_graduating')),
                'course_duration': data['course_duration'],

                # Guardian's Background Section
                'guardian_complete_name': data['guardian_complete_name'],
                'guardian_complete_address': data['guardian_complete_address'],
                'guardian_contact_number': data['guardian_contact_number'],
                'guardian_occupation': data['guardian_occupation'],
                'guardian_place_of_work': data['guardian_place_of_work'],
                'guardian_educational_attainment': data['guardian_educational_attainment'],

                'guardians_voter_certificate_name': data['guardians_voter_certificate'].name,                   # Get file name instead of the whole file for processing
                'guardians_voter_certificate_content': data['guardians_voter_certificate'].read(),              # Get file content(binary) instead of the whole file for processing

                # Miscellaneous Section
                'number_of_semesters_before_graduating': data['number_of_semesters_before_graduating'],
                'transferee': data['transferee'],
                'shiftee': data['shiftee'],
                'student_status': data['student_status'],
            }
                    
            # Execute OCR scripts
            extracted_voters_data = extract_applicant_voters(temp_data['voter_certificate_content'], temp_data['voter_certificate_name'])
            extracted_guardian_info_data = extract_guardian_voters(temp_data['guardians_voter_certificate_content'], temp_data['guardians_voter_certificate_name'])

            if extracted_voters_data and extracted_guardian_info_data:
                    temp_data.update(extracted_voters_data)
                    temp_data.update(extracted_guardian_info_data)

                    # Files or Images that needs to be converted to Base64 for Serialization upon POST() method
                    informative_copy_of_grades_content = temp_data['informative_copy_of_grades_content']
                    voter_certificate_content = temp_data['voter_certificate_content']
                    registration_form_content = temp_data['registration_form_content']
                    guardians_voter_certificate_content = temp_data['guardians_voter_certificate_content']

                    if informative_copy_of_grades_content and voter_certificate_content and registration_form_content and guardians_voter_certificate_content:
                        # Encode Files to Base64 format
                        informative_copy_of_grades_content_base64 = base64.b64encode(informative_copy_of_grades_content).decode('utf-8')
                        voter_certificate_content_base64 = base64.b64encode(voter_certificate_content).decode('utf-8')
                        registration_form_content_base64 = base64.b64encode(registration_form_content).decode('utf-8')
                        guardians_voter_certificate_content_base64 = base64.b64encode(guardians_voter_certificate_content).decode('utf-8')

                        # Store files encoded in Base64 format back to the data
                        temp_data['informative_copy_of_grades_content'] = informative_copy_of_grades_content_base64
                        temp_data['voter_certificate_content'] = voter_certificate_content_base64
                        temp_data['registration_form_content'] = registration_form_content_base64
                        temp_data['guardians_voter_certificate_content'] = guardians_voter_certificate_content_base64

                    partnered_universities_id = data['university_attending']
                    partnered_universities_instance = PartneredUniversities.objects.get(id=partnered_universities_id)
                    temp_data['university_attending'] = partnered_universities_instance

                    courses_id = data['course_taking']
                    courses_instance = Courses.objects.get(id=courses_id)
                    temp_data['course_taking'] = courses_instance

                    # Fields to exclude when creating the TempApplications instance
                    exclude_fields = [
                        'informative_copy_of_grades_name',
                        'voter_certificate_name',
                        'registration_form_name',
                        'guardians_voter_certificate_name',
                    ]

                    # Remove excluded fields from temp_data
                    for field in exclude_fields:
                        temp_data.pop(field, None)

                    temp_data.update(temp_data)
            
            serializer.validated_data.update(temp_data)
            
            serializer.validated_data['is_eligible'] = False
            serializer.validated_data['applicant_status'] = Applications.ApplicantStatus.RENEWING_APPLICANT
            serializer.validated_data['application_status'] = Applications.Status.PENDING
            serializer.validated_data['evaluated_by'] = None

            saved_application_instance = serializer.save()

            # Send email after saving the instance
            context = {
                "firstname": serializer.validated_data.get('firstname'),
                "lastname": serializer.validated_data.get('lastname'),
                "application_reference_id": serializer.validated_data.get('application_reference_id')
            }

            print(context)

            html_message = render_to_string("content/application_received_email.html", context=context)
            plain_message = strip_tags(html_message)

            message = EmailMultiAlternatives(
                subject = "Scholarship Application",
                body = plain_message,
                from_email = None,
                to = [serializer.validated_data.get('email_address'),]
            )

            message.attach_alternative(html_message, "text/html")
            message.send()

            # Constant values after creation of an Application instance
            StatusUpdate.objects.create(
                application = saved_application_instance,
                application_reference_id = saved_application_instance.application_reference_id,
                description = "Your scholarship application has been submitted and received by our system.",
                current_step = 1,
                is_active = True
            )

            # Initiate Automated Eligibility Checking
            application_id = serializer.data.get('id')

            # Trigger Celery task for eligibility checking asynchronously
            check_eligibility.apply_async(args=[application_id])

            response_data = {
                        'status': 'success',
                        'message': 'Data has been successfully updated and saved to the database.',
                    }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                        'status': 'error',
                        'message': 'Data validation failed. Please check the submitted data.',
                        'errors': serializer.errors,
                    }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)