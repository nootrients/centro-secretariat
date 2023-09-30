from django.http import HttpResponse

# Create your views here.

# [Client] Scholar Application Page
# Views Object that presents the different choices and/or operations under the subject of Scholarship Application
def application_index(request):
    return HttpResponse("<div style=\"text-align:center\"><h1>Scholar Application Page</h1></div>")

# [Client] Policy Procedure Page
# Invoked upon the start of an application
def policy_procedure(request):
    return HttpResponse("<div style=\"text-align:center\"><h1>Policy Procedure Page</h1></div>")

# [Client] Form Completion
def submit_application(request):
    # Call Application Form
    return HttpResponse("<div style=\"text-align:center\"><h1>Scholarship Application Submission Form</h1></div>")

"""
# [Client] Load / Retrieve Scholarship Application
def load_application(request):
    # Call Retrieval Form
    # POST - Application ID, Security Question Answer
    # GET - Security Question

    # Restore Application State (where Client left off)
    return HttpResponse("<div style=\"text-align:center\"><h1>Application Retrieval Form</h1></div>")    
"""
