import csv
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import AllowAny

from django.db.models import Count
from django.http import HttpResponse
from django.http import JsonResponse

from accounts.permissions import IsHeadOfficer

from application.models import Applications
from application.serializer import DashboardDataSerializer

from .forecasting import forecast_scholarship_type
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
    

class ForecastView(APIView):
    
    # Change to IsHeadOfficer later
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