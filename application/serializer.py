from rest_framework import serializers

from application.models import Applications, EligibilityConfig



class EligibilityConfigSerializer(serializers.ModelSerializer):
    """Serializer for EligibilityConfig model."""

    class Meta:
        model = EligibilityConfig
        fields = '__all__'
        read_only_fields = 'academic_year',


class ApplicationsSerializer(serializers.ModelSerializer):
    """Serializer for Applications model."""

    class Meta:
        model = Applications
        fields = '__all__'
        read_only_fields = ('firstname', 
                            'lastname',
                            'middlename',
                            
                            'district',
                            
                            'is_applying_for_merit',
        
                            'total_units_enrolled',
                            
                            'is_eligible',
                            'is_approved',
                            'approved_by',
                            'created_at',
                            'updated_at')
        
    
class EligibleApplicationsSerializer(serializers.ModelSerializer):
    """Serializer for retrieving `ELIGIBLE` scholarship applications."""

    class Meta:
        model = Applications
        fields = '__all__'


class ApplicationRetrieveUpdateSerializer(serializers.ModelSerializer):
    """Serializer for retrieving and approving/rejecting an eligible scholarship application."""
    
    class Meta:
        model = Applications
        fields = ['is_approved']

