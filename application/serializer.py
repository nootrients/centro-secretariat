from rest_framework import serializers

from application.models import TempApplications, Applications, EligibilityConfig, StatusUpdate, PartneredUniversities, Courses

from demographics.serializer import GenderSerializer
from demographics.models import Gender

from django.core.files.base import ContentFile
import base64


class EligibilityConfigSerializer(serializers.ModelSerializer):
    """Serializer for EligibilityConfig model."""

    class Meta:
        model = EligibilityConfig
        fields = '__all__'
        read_only_fields = 'academic_year',


class TempApplicationsSerializer(serializers.ModelSerializer):
    lastname = serializers.CharField(write_only=True, allow_blank=True, required=False)
    firstname = serializers.CharField(write_only=True, allow_blank=True, required=False)
    middlename = serializers.CharField(write_only=True, allow_blank=True, required=False)

    years_of_residency = serializers.CharField(write_only=True, allow_blank=True, required=False)
    voters_issued_at = serializers.CharField(write_only=True, allow_blank=True, required=False)
    voters_issuance_date = serializers.CharField(write_only=True, allow_blank=True, required=False)

    # Guardian's Voter's Certificate Validation Fields
    guardians_years_of_residency = serializers.CharField(write_only=True, allow_blank=True, required=False)
    guardians_voters_issued_at = serializers.CharField(write_only=True, allow_blank=True, required=False)
    guardians_voters_issuance_date = serializers.CharField(write_only=True, allow_blank=True, required=False)
    
    gender = serializers.PrimaryKeyRelatedField(
        queryset=Gender.objects.all(),
        write_only=True
    )

    # # new
    # university_attending = serializers.PrimaryKeyRelatedField(
    #     queryset=PartneredUniversities.objects.all(),
    #     write_only=True
    # )

    class Meta:
        model = TempApplications
        fields = '__all__'
        read_only_fields = ('district',
                            
                            'applicant_status',
                            'applying_for_academic_year',
                        )

    def create(self, validated_data):
        # Extract and decode the base64_content
        id_base64_content = validated_data.pop('national_id_content', None)
        icg_base64_content = validated_data.pop('informative_copy_of_grades_content', None)
        applicant_voters_base64_content = validated_data.pop('voter_certificate_content', None)
        registration_form_base64_content = validated_data.pop('registration_form_content', None)
        guardian_voters_base64_content = validated_data.pop('guardians_voter_certificate_content', None)
        
        if id_base64_content:
            id_binary_content = base64.b64decode(id_base64_content)
            icg_binary_content = base64.b64decode(icg_base64_content)
            applicant_voters_binary_content = base64.b64decode(applicant_voters_base64_content)
            registration_form_binary_content = base64.b64decode(registration_form_base64_content)
            guardian_voters_binary_content = base64.b64decode(guardian_voters_base64_content)

            validated_data['national_id'] = ContentFile(id_binary_content, name='national_id.jpg')
            validated_data['informative_copy_of_grades'] = ContentFile(icg_binary_content, name='informative_copy_of_grades.pdf')
            validated_data['voter_certificate'] = ContentFile(applicant_voters_binary_content, name='applicant_votersCert.jpg')
            validated_data['registration_form'] = ContentFile(registration_form_binary_content, name='registration_form.pdf')
            validated_data['guardians_voter_certificate'] = ContentFile(guardian_voters_binary_content, name='guardians_votersCert.jpg')

        # Create and return the TempApplications object
        return super(TempApplicationsSerializer, self).create(validated_data)


class ApplicationsSerializer(serializers.ModelSerializer):
    """Serializer for Applications model."""
    class Meta:
        model = Applications
        fields = '__all__'
        read_only_fields = (
            'national_id',
            'informative_copy_of_grades',
            'voter_certificate',
            'registration_form',
            'guardians_voter_certificate',

            'district',
                            
            'applicant_status',
            'applying_for_academic_year',

            'is_eligible',
            'expires_at',
            'status',
            'evaluated_by',
            'scholar',
        )

    def create(self, validated_data):
        # Extract and decode the base64_content
        id_base64_content = validated_data.pop('national_id_content', None)
        icg_base64_content = validated_data.pop('informative_copy_of_grades_content', None)
        applicant_voters_base64_content = validated_data.pop('voter_certificate_content', None)
        registration_form_base64_content = validated_data.pop('registration_form_content', None)
        guardian_voters_base64_content = validated_data.pop('guardians_voter_certificate_content', None)
        
        if id_base64_content:
            id_binary_content = base64.b64decode(id_base64_content)
            icg_binary_content = base64.b64decode(icg_base64_content)
            applicant_voters_binary_content = base64.b64decode(applicant_voters_base64_content)
            registration_form_binary_content = base64.b64decode(registration_form_base64_content)
            guardian_voters_binary_content = base64.b64decode(guardian_voters_base64_content)

            validated_data['national_id'] = ContentFile(id_binary_content, name='national_id.jpg')
            validated_data['informative_copy_of_grades'] = ContentFile(icg_binary_content, name='informative_copy_of_grades.pdf')
            validated_data['voter_certificate'] = ContentFile(applicant_voters_binary_content, name='applicant_votersCert.jpg')
            validated_data['registration_form'] = ContentFile(registration_form_binary_content, name='registration_form.pdf')
            validated_data['guardians_voter_certificate'] = ContentFile(guardian_voters_binary_content, name='guardians_votersCert.jpg')

        # Create and return the Applications object
        return super(ApplicationsSerializer, self).create(validated_data)
        
    
class EligibleApplicationsSerializer(serializers.ModelSerializer):
    """Serializer for retrieving `ELIGIBLE` scholarship applications."""

    class Meta:
        model = Applications
        fields = (
            'application_reference_id',
            'lastname',
            'firstname',
            'middlename',
            'email_address',
            'semester',
            'applicant_status',
            'scholarship_type',
        )


# Change to something else, RetrieveUpdate should be used for retrieval of application in the applicant's side
class ApplicationRetrieveUpdateSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and approving/rejecting an eligible scholarship application."""
    application_status = serializers.ChoiceField(write_only=True, choices=Applications.Status.choices)
    evaluated_by = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Applications
        fields = '__all__'
        read_only_fields = (
            'application_reference_id',
            'national_id',
            'lastname',
            'firstname',
            'middlename',
            'birthdate',
            'house_address',
            'barangay',
            'district',
            'email_address',
            'personalized_facebook_link',
            'religion',
            'applicant_status',
            'scholarship_type',
            'applying_for_academic_year',
            'semester',
            'informative_copy_of_grades',
            'is_applying_for_merit',
            'voter_certificate',
            'years_of_residency',
            'voters_issued_at',
            'voters_issuance_date',
            'registration_form',
            'total_units_enrolled',
            'is_ladderized',
            'year_level',
            'is_graduating',
            'course_duration',
            'elementary_school',
            'elementary_school_type',
            'elementary_school_address',
            'elementary_start_end',
            'jhs_school',
            'jhs_school_type',
            'jhs_school_address',
            'jhs_start_end',
            'shs_school',
            'shs_school_type',
            'shs_school_address',
            'shs_start_end',
            'guardian_complete_name',
            'guardian_complete_address',
            'guardian_contact_number',
            'guardian_occupation',
            'guardian_place_of_work',
            'guardian_educational_attainment',
            'guardians_voter_certificate',
            'guardians_years_of_residency',
            'guardians_voters_issued_at',
            'guardians_voters_issuance_date',
            'number_of_semesters_before_graduating',
            'transferee',
            'shiftee',
            'student_status',
            'is_eligible',
            'created_at',
            'updated_at',
            'gender',
            'university_attending',
            'course_taking',
            'scholar',
            'expires_at',
        )


class StatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusUpdate
        fields = '__all__'


class TempApplicationsRetrievalSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving ALL THE DATA saved from TempApplications table
    """

    class Meta:
        model = TempApplications
        fields = '__all__'


class DashboardDataSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying numerical data to serve into the Head Officer's dashboard endpoint
    """

    class Meta:
        model = Applications
        fields = '__all__'


class ApplicationsRenewalSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving specific fields for renewal of application
    """

    years_of_residency = serializers.CharField(write_only=True, allow_blank=True, required=False)
    voters_issued_at = serializers.CharField(write_only=True, allow_blank=True, required=False)
    voters_issuance_date = serializers.CharField(write_only=True, allow_blank=True, required=False)

    # Guardian's Voter's Certificate Validation Fields
    guardians_years_of_residency = serializers.CharField(write_only=True, allow_blank=True, required=False)
    guardians_voters_issued_at = serializers.CharField(write_only=True, allow_blank=True, required=False)
    guardians_voters_issuance_date = serializers.CharField(write_only=True, allow_blank=True, required=False)

    class Meta:
        model = Applications
        fields = '__all__'
        read_only_fields = (
            # 'application_reference_id',
            'national_id',
            # 'lastname',
            # 'firstname',
            # 'middlename',
            'birthdate',
            'district',
            # 'email_address',
            'religion',
            'scholarship_type',
            'gender',

            'elementary_school',
            'elementary_school_type',
            'elementary_school_address',
            'elementary_start_end',
            'jhs_school',
            'jhs_school_type',
            'jhs_school_address',
            'jhs_start_end',
            'shs_school',
            'shs_school_type',
            'shs_school_address',
            'shs_start_end',

            'applicant_status',
            'applying_for_academic_year',

            'is_eligible',
            'expires_at',
            'application_status',
            'evaluated_by',
            'scholar',
        )

    def update(self, instance, validated_data):
        # Extract and decode the base64_content
        icg_base64_content = validated_data.pop('informative_copy_of_grades_content', None)
        applicant_voters_base64_content = validated_data.pop('voter_certificate_content', None)
        registration_form_base64_content = validated_data.pop('registration_form_content', None)
        guardian_voters_base64_content = validated_data.pop('guardians_voter_certificate_content', None)
        
        if icg_base64_content and applicant_voters_base64_content and registration_form_base64_content and guardian_voters_base64_content:
            icg_binary_content = base64.b64decode(icg_base64_content)
            applicant_voters_binary_content = base64.b64decode(applicant_voters_base64_content)
            registration_form_binary_content = base64.b64decode(registration_form_base64_content)
            guardian_voters_binary_content = base64.b64decode(guardian_voters_base64_content)

            validated_data['informative_copy_of_grades'] = ContentFile(icg_binary_content, name='informative_copy_of_grades.pdf')
            validated_data['voter_certificate'] = ContentFile(applicant_voters_binary_content, name='applicant_votersCert.jpg')
            validated_data['registration_form'] = ContentFile(registration_form_binary_content, name='registration_form.pdf')
            validated_data['guardians_voter_certificate'] = ContentFile(guardian_voters_binary_content, name='guardians_votersCert.jpg')

        return super(ApplicationsRenewalSerializer, self).update(instance, validated_data)
    

class UnivSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartneredUniversities
        fields = '__all__'

        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'