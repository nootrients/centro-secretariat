from .models import YearlyScholarshipData
from rest_framework import serializers

class YearlyScholarshipDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearlyScholarshipData
        fields = '__all__'


class YearlyScholarshipPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearlyScholarshipData
        fields = (
            'id',
            'year',
            'semester',
            'total_basic_plus',
            'total_basic_scholarship',
            'total_suc_lcu',
            'total_honors',
            'total_premier',
            'total_priority',
        )