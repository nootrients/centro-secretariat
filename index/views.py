from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    return HttpResponse('<div style="text-align:center"><h1>Main Homepage</h1></div>')


def about_page(request):
    return HttpResponse('<div style="text-align:center"><h1>About Page</h1></div>')


def guidelines_page(request):
    return HttpResponse('<div style="text-align:center"><h1>Guidelines Page</h1></div>')


# [Client] Scholar Application Page
# Views Object that presents the different choices and/or operations under the subject of Scholarship Application
def application_index(request):
    return HttpResponse(
        '<div style="text-align:center"><h1>Scholar Application Page</h1></div>'
    )


# [Client] Policy Procedure Page
# Invoked upon the start of an application
def policy_procedure(request):
    return HttpResponse(
        '<div style="text-align:center"><h1>Policy Procedure Page</h1></div>'
    )


"""
# [Client] Load / Retrieve Scholarship Application
def load_application(request):
    # Call Retrieval Form
    # POST - Application ID, Security Question Answer
    # GET - Security Question

    # Restore Application State (where Client left off)
    return HttpResponse("<div style=\"text-align:center\"><h1>Application Retrieval Form</h1></div>")    
"""


# [Client] Tracking Application Page
# POST - Application ID
# GET - Logs
def track_application(request):
    return HttpResponse(
        '<div style="text-align:center"><h1>Scholarship Application Tracking Form</h1></div>'
    )
    # Call Tracking Details page


# [Client] Client Satisfaction Survey
# POST - Application ID, Answers, and Comments (Optional)
def evaluation_survey(request):
    return HttpResponse(
        '<div style="text-align:center"><h1>Client Satisfaction Survey Page</h1></div>'
    )
    # After recording the response, return to index page together with a notification modal.
