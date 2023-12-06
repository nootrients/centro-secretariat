import csv
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt
import datetime

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework import generics, status

from django.db.models import Count
from django.http import HttpResponse
from django.http import JsonResponse

from accounts.permissions import IsHeadOfficer

from application.models import Applications, EligibilityConfig
from application.serializer import DashboardDataSerializer

from .forecasting import forecast_scholarship_type
from .models import YearlyScholarshipData
from .serializer import YearlyScholarshipDataSerializer, YearlyScholarshipPerformanceSerializer

from statsmodels.tsa.arima.model import ARIMA


def plot_to_base64(plt):
        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)
        base64_image = base64.b64encode(image_stream.read()).decode('utf-8')
        plt.close()

        return base64_image

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
        total_applicants_count = Applications.objects.filter(application_status="ACCEPTED").count()
        new_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        renewing_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()
        graduating_scholars_count = Applications.objects.filter(is_graduating=True, application_status = "ACCEPTED").count()
        
        total_pending_applications_count = Applications.objects.filter(is_eligible=True, application_status="PENDING").count()

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
    

class DashboardDataDownloadView(APIView):
    """
    Endpoint for downloading a CSV file containing the JSON Data from the data dashboard.
    """

    permission_classes = [IsHeadOfficer, ]

    def get(self, request, *args, **kwargs):
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
        total_applicants_count = Applications.objects.filter(application_status="ACCEPTED").count()
        new_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        renewing_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        graduating_scholars_count = Applications.objects.filter(is_graduating=True).count()
        
        total_pending_applications_count = Applications.objects.filter(application_status="PENDING").count()

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

        # Create file.csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dashboard_data.csv"'

        csv_writer = csv.writer(response)

        # Assign rows
        csv_writer.writerow([
            'Total Applicants Count',
            'New Applicants Count',
            'Renewing Applicants Count',
            'Graduating Scholars Count',
            'Total Pending Applications Count',
            'Male Applicants Count',
            'Female Applicants Count',
            'Scholarship Type',
            'Scholarship Type Count',
            'Barangay',
            'Scholars Per Barangay Count',
            'Top Schools Count'
        ])

        # Append data to rows
        csv_writer.writerow([
            total_applicants_count,
            new_applicants_count,
            renewing_applicants_count,
            graduating_scholars_count,
            total_pending_applications_count,
            male_applicants_count,
            female_applicants_count,
            scholarship_type_count,
            scholars_per_barangay_count,
            top_schools_count
        ])

        return response
    

class ApplicantStatusData(APIView):
    """
    Endpoint for getting the counts of NEW and RENEWING Applicants.
    """

    permission_classes = [IsHeadOfficer, ]
    serializer_class = DashboardDataSerializer

    def get(self, request, *args, **kwargs):
        new_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        renewing_applicants_count = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()

        data = {
            'new_applicants_count': new_applicants_count,
            'renewing_applicants_count': renewing_applicants_count,
        }

        return Response(data)


class ApplicationStatusData(APIView):
    """
    Endpoint for getting the counts of ACCEPTED, REJECTED, and PENDING Applications.
    """

    permission_classes = [IsHeadOfficer, ]
    serializer_class = DashboardDataSerializer

    def get(self, request, *args, **kwargs):
        accepted_count = Applications.objects.filter(application_status="ACCEPTED").count()
        rejected_count = Applications.objects.filter(application_status="REJECTED").count()
        pending_count = Applications.objects.filter(application_status="PENDING").count()

        data = {
            'accepted_count': accepted_count,
            'rejected_count': rejected_count,
            'pending_count': pending_count,
        }

        return Response(data)


class CountPerScholarshipType(APIView):
    """
    Endpoint for getting the accepted applications per Scholarship Type
    """

    permission_classes = [IsHeadOfficer, ]
    serializer_class = DashboardDataSerializer

    def get(self, request, *args, **kwargs):
        scholarship_type_count = (
            Applications.objects
            .filter(application_status = "ACCEPTED")
            .values('scholarship_type')
            .annotate(count=Count('scholarship_type'))
        )

        return Response(scholarship_type_count)


class ForecastView(APIView):
    
    # Change to IsHeadOfficer later
    # permission_classes = [IsHeadOfficer, ]
    permission_classes = [AllowAny, ]
    parser_classes = [MultiPartParser]
    
    def post(self, request, *args, **kwargs):
        # Ensure 'file' and 'scholarship_type' are present in the request data
        if 'file' not in request.data:
            return Response({"error": "File not provided"}, status=400)

        scholarship_type = request.data.get('scholarship_type')

        if not scholarship_type:
            return Response({"error": "scholarship_type is required"}, status=400)

        # Loading data
        file_obj = request.data['file']
        df = pd.read_csv(file_obj, parse_dates=['Date'])
        df = df.set_index('Date')

        df.index.freq = '6M'
        
        try:
            file_obj = request.data['file']

            best_order_new, best_order_renewing, test = forecast_scholarship_type(df, scholarship_type)

            final_model_new = ARIMA(df[f'{scholarship_type}_New'], order=best_order_new)
            final_model_fit_new = final_model_new.fit()

            final_model_renewing = ARIMA(df[f'{scholarship_type}_Renewing'], order=best_order_renewing)
            final_model_fit_renewing = final_model_renewing.fit()

            # Make predictions and forecast
            start = len(df)
            end = len(df) + len(test) - 1
            forecast_periods = len(test)

            forecast_new = final_model_fit_new.get_forecast(steps=forecast_periods).predicted_mean
            forecast_renewing = final_model_fit_renewing.get_forecast(steps=forecast_periods).predicted_mean

            forecast_new_dict = forecast_new.reset_index().to_dict(orient='records')
            forecast_renewing_dict = forecast_renewing.reset_index().to_dict(orient='records')
            
            plt.figure(figsize=(12, 6))
            plt.plot(df.index, df[f'{scholarship_type}_New'], label='Actual (New)', marker='o')
            plt.plot(forecast_new.index, forecast_new, label='Forecast (New)', linestyle='--', marker='o')
            plt.title(f'Actual vs Forecasted Values for {scholarship_type} (New Applicants) - ARIMA Order: {best_order_new}')
            plt.xlabel('Date')
            plt.ylabel('Number of Applicants')
            plt.legend()
            forecast_new_plot = plot_to_base64(plt)

            # Plot entire dataset along with forecasted values for renewing applicants
            plt.figure(figsize=(12, 6))
            plt.plot(df.index, df[f'{scholarship_type}_Renewing'], label='Actual (Renewing)', marker='o')
            plt.plot(forecast_renewing.index, forecast_renewing, label='Forecast (Renewing)', linestyle='--', marker='o')
            plt.title(f'Actual vs Forecasted Values for {scholarship_type} (Renewing Applicants) - ARIMA Order: {best_order_renewing}')
            plt.xlabel('Date')
            plt.ylabel('Number of Applicants')
            plt.legend()
            forecast_renewing_plot = plot_to_base64(plt)

            response_data = {
                'status': 'Ok',
                # 'forecast_new': forecast_new_dict,
                # 'forecast_renewing': forecast_renewing_dict,
                'forecast_new_plot': forecast_new_plot,
                'forecast_renewing_plot': forecast_renewing_plot,
            }

            return JsonResponse(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        

class DisplayYearlyPerformance(generics.ListAPIView):
    """
    Endpoint for saving the data gathered from the current year and semester to the yearly model.
    """

    permission_classes = [IsHeadOfficer, ]
    serializer_class = YearlyScholarshipPerformanceSerializer
    
    def get_queryset(self):
        return YearlyScholarshipData.objects.all()
    

class SaveYearlyPerformance(APIView):
    """
    Appending the current data (count) to the YearlyScholarshipData model
    """

    permission_classes = [IsHeadOfficer, ]

    def post(self, request, *args, **kwargs):
        eligibility_constraint_instance = EligibilityConfig.objects.first()
        
        year = datetime.date.today().year
        semester = eligibility_constraint_instance.semester
        
        total_applications = Applications.objects.filter(is_eligible=True).count()
        total_accepted = Applications.objects.filter(application_status="ACCEPTED").count()
        total_rejected = Applications.objects.filter(application_status="REJECTED").count()
        total_new = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        total_renewing = Applications.objects.filter(applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()
        total_graduates = Applications.objects.filter(is_graduating=True, application_status="ACCEPTED").count()

        total_basic_plus = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.BASIC_PLUS_SUC, application_status="ACCEPTED").count()
        total_basic_plus_new = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.BASIC_PLUS_SUC, applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        total_basic_plus_renewing = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.BASIC_PLUS_SUC, applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()

        total_basic_scholarship = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.BASIC_SCHOLARSHIP, application_status="ACCEPTED").count()
        total_basic_scholarship_new = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.BASIC_SCHOLARSHIP, applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        total_basic_scholarship_renewing = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.BASIC_SCHOLARSHIP, applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()

        total_suc_lcu = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.SUC_LCU, application_status="ACCEPTED").count()
        total_suc_lcu_new = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.SUC_LCU, applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        total_suc_lcu_renewing = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.SUC_LCU, applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()

        total_honors = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.HONORS, application_status="ACCEPTED").count()
        total_honors_new = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.HONORS, applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        total_honors_renewing = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.HONORS, applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()

        total_premier = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.PREMIER, application_status="ACCEPTED").count()
        total_premier_new = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.PREMIER, applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        total_premier_renewing = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.PREMIER, applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()

        total_priority = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.PRIORITY, application_status="ACCEPTED").count()
        total_priority_new = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.PRIORITY, applicant_status=Applications.ApplicantStatus.NEW_APPLICANT, application_status="ACCEPTED").count()
        total_priority_renewing = Applications.objects.filter(scholarship_type=Applications.ScholarshipType.PRIORITY, applicant_status=Applications.ApplicantStatus.RENEWING_APPLICANT, application_status="ACCEPTED").count()

        data = {
            'year': year,
            'semester': semester,
            
            'total_applications': total_applications,
            'total_accepted': total_accepted,
            'total_rejected': total_rejected,
            'total_new': total_new,
            'total_renewing': total_renewing,
            'total_graduates': total_graduates,

            'total_basic_plus': total_basic_plus,
            'total_basic_plus_new': total_basic_plus_new,
            'total_basic_plus_renewing': total_basic_plus_renewing,

            'total_basic_scholarship': total_basic_scholarship,
            'total_basic_scholarship_new': total_basic_scholarship_new,
            'total_basic_scholarship_renewing': total_basic_scholarship_renewing,

            'total_suc_lcu': total_suc_lcu,
            'total_suc_lcu_new': total_suc_lcu_new,
            'total_suc_lcu_renewing': total_suc_lcu_renewing,

            'total_honors': total_honors,
            'total_honors_new': total_honors_new,
            'total_honors_renewing': total_honors_renewing,
            
            'total_premier': total_premier,
            'total_premier_new': total_premier_new,
            'total_premier_renewing': total_premier_renewing,

            'total_priority': total_priority,
            'total_priority_new': total_priority_new,
            'total_priority_renewing': total_priority_renewing,
        }

        serializer = YearlyScholarshipDataSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            return Response({"status": "Data saved successfully"})
        else:
            return Response(serializer.errors, status=400)
        

class GenerateYearlyScholarshipDataCSV(APIView):
    """
    Endpoint for generating a CSV file containing the yearly scholarship data
    """

    # permission_classes = [IsHeadOfficer, ]
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        data_objects = YearlyScholarshipData.objects.all()

        # Configure response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="yearly_scholarship_data.csv"'

        # Set CSV writer
        writer = csv.writer(response)
        writer.writerow([
            'Date',
            
            'Total_Applications',
            'Total_New',
            'Total_Renewing',
            
            'GRADUATE',
            
            'Total_HONORS',
            'HONORS_New',
            'HONORS_Renewing',
            
            'Total_PREMIER',
            'PREMIER_New',
            'PREMIER_Renewing',
            
            'Total_PRIORITY',
            'PRIORITY_New',
            'PRIORITY_Renewing',
            
            'Total_BASIC PLUS SUC',
            'BASIC PLUS SUC_New',
            'BASIC PLUS SUC_Renewing',
            
            'Total_BASIC SCHOLARSHIP',
            'BASIC SCHOLARSHIP_New',
            'BASIC SCHOLARSHIP_Renewing',
            
            'Total_SUC_LCU',
            'SUC_LCU_New',
            'SUC_LCU_Renewing',
        ])

        for data in data_objects:
            # Generate the value for the "Year" field based on semester
            year_value = f"31 01 {data.year}" if data.semester == "FIRST SEMESTER" else f"31 07 {data.year}"

            writer.writerow([
                year_value,
                
                data.total_applications,
                data.total_new,
                data.total_renewing,

                data.total_graduates,

                data.total_honors,
                data.total_honors_new,
                data.total_honors_renewing,

                data.total_premier,
                data.total_premier_new,
                data.total_premier_renewing,

                data.total_priority,
                data.total_priority_new,
                data.total_priority_renewing,

                data.total_basic_plus,
                data.total_basic_plus_new,
                data.total_basic_plus_renewing,

                data.total_basic_scholarship,
                data.total_basic_scholarship_new,
                data.total_basic_scholarship_renewing,

                data.total_suc_lcu,
                data.total_suc_lcu_new,
                data.total_suc_lcu_renewing,
            ])

        return response
    

class TopFiveUniversities(APIView):
    """
    Endpoint for getting the top 5 university/institutions that has the most number of accepted applicants
    """

    permission_classes = [IsHeadOfficer, ]

    def get(self, request, *args, **kwargs):
        try:
            # Get the top 5 universities for each scholarship type
            top_universities_data = {}
            scholarship_types = ['HONORS', 'PREMIER', 'PRIORITY', 'BASIC PLUS SUC', 'BASIC SCHOLARSHIP', 'SUC_LCU']

            for scholarship_type in scholarship_types:
                top_universities_data[scholarship_type] = (
                    Applications.objects
                    .filter(application_status='ACCEPTED', scholarship_type=scholarship_type)
                    .values('university_attending__university_name')
                    .annotate(total_accepted=Count('id'))
                    .order_by('-total_accepted')
                    .values('university_attending__university_name', 'total_accepted')
                    [:5]
                )

            # Format data for response
            response_data = []
            for scholarship_type, universities in top_universities_data.items():
                response_data.append({
                    'id': scholarship_type,
                    'data': [
                        {'x': university['university_attending__university_name'], 'y': university['total_accepted']}
                        for university in universities
                    ]
                })

            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        

class AcceptedApplicantsPerBarangay(APIView):
    """
    Endpoint for getting the counts of ACCEPTED applicants per BARANGAY.
    """

    permission_classes = [IsHeadOfficer, ]

    def get(self, request, *args, **kwargs):
        scholars_per_barangay_count = (
            Applications.objects
            .values('barangay', 'scholarship_type')
            .annotate(count=Count('id'))
        )

        return Response(scholars_per_barangay_count)
    

class ResetApplicationsView(APIView):
    """
    Endpoint for resetting application instances to application_status = "UNPROCESSED" (Filter out those who only applied).
    """

    permission_classes = [IsHeadOfficer]

    def post(self, request, *args, **kwargs):
        # Reset application instances
        Applications.objects.filter(application_status__in=['ACCEPTED', 'REJECTED']).update(application_status=Applications.Status.UNPROCESSED)

        return Response({"message": "Application instances reset successfully for the next semester."}, status=status.HTTP_200_OK)