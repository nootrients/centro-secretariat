from rest_framework import serializers

from application.models import Applications, EligibilityConfig

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


class ApplicationsSerializer(serializers.ModelSerializer):
    """Serializer for Applications model."""
    #national_id = serializers.ImageField()
    #national_id = serializers.ImageField(write_only=True)

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

    class Meta:
        model = Applications
        fields = '__all__'
        read_only_fields = ('district',
                            
                            'applicant_status',
                            'applying_for_academic_year',

                            'is_eligible',
                            'is_approved',
                            'approved_by',
                        )

    def create(self, validated_data):
        print("Creating Application with data:", validated_data)

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
        fields = '__all__'


# Change to something else, RetrieveUpdate should be used for retrieval of application in the applicant's side
class ApplicationRetrieveUpdateSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and approving/rejecting an eligible scholarship application."""
    
    class Meta:
        model = Applications
        fields = ['is_approved']


class ReviewFormSerializer(serializers.Serializer):
    national_id = serializers.ImageField()
    birthdate = serializers.DateField()
    house_address = serializers.CharField()
    barangay = serializers.CharField()
    email_address = serializers.EmailField()
    personalized_facebook_link = serializers.CharField()
    religion = serializers.CharField()
    applicant_status = serializers.CharField()
    scholarship_type = serializers.CharField()
    
    gender = GenderSerializer()

    lastname = serializers.CharField()
    firstname = serializers.CharField()
    middlename = serializers.CharField()