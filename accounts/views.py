from django.shortcuts import HttpResponse

# Create your views here.

# One Login module for all types of Users
# POST - email and password
def login_page(request):
    return HttpResponse("<div style=\"text-align:center\"><h1>Login Page</h1></div>")