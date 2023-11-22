from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count

from accounts.permissions import IsHeadOfficer

from application.models import Applications
from application.serializer import DashboardDataSerializer


# Create your views here.
class DashboardDataView(APIView):
    """
    Endpoint for serving the JSON response to populate charts in :8000/head/dashboard
    """

    permission_classes = [IsHeadOfficer, ]
    serializer_class = DashboardDataSerializer
    
    def get(self, request, *args, **kwargs):
        # Constants
        SCHOLARSHIP_TYPE_BUDGETS = {
            'HONOR': 20000,
            'PREMIER': 20000,
            'PRIORITY': 20000,
            'BASIC PLUS SUC': 10000,
            'BASIC SCHOLARSHIP': 7500,
            'SUC_LCU': 7500, 
        }
        MERIT_INCENTIVE = 5000

        # Total number of applicants
        total_applicants_count = Applications.objects.filter(status="ACCEPTED").count()
        new_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, status="ACCEPTED").count()
        renewing_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, status="ACCEPTED").count()
        graduating_scholars_count = Applications.objects.filter(is_graduating=True).count()
        
        total_pending_applications_count = Applications.objects.filter(status="PENDING").count()

        # Per scholarship_type
        scholarship_type_count = (
            Applications.objects
            .values('scholarship_type')
            .annotate(count=Count('scholarship_type'))
        )

        # Per barangay
        scholars_per_barangay_count = (
            Applications.objects
            .values('barangay', 'scholarship_type')
            .annotate(count=Count('id'))
        )

        # Gender
        male_applicants_count = Applications.objects.filter(gender=1).count()
        female_applicants_count = Applications.objects.filter(gender=2).count()

        # Get the top 3 schools/universities with the most applicants
        top_schools_count = (
            Applications.objects
            .values('university_attending')
            .annotate(count=Count('university_attending'))
            .order_by('-count')                                 # Order by count in descending order
            [:3]                                                # Limit the results to the top 3
        )

        data = {
            'total_applicants_count': total_applicants_count,
            'new_applicants_count': new_applicants_count,
            'renewing_applicants_count': renewing_applicants_count,
            'graduating_scholars_count': graduating_scholars_count,

            'total_pending_applications_count': total_pending_applications_count,
            
            'scholarship_type_count': scholarship_type_count,
            'scholars_per_barangay_count': scholars_per_barangay_count,
            
            'male_applicants_count': male_applicants_count,
            'female_applicants_count': female_applicants_count,
            
            'top_schools_count': top_schools_count,
        }

        return Response(data)