from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("<div style=\"text-align:center\"><h1>Main Homepage</h1></div>")

def about_page(request):
    return HttpResponse("<div style=\"text-align:center\"><h1>About Page</h1></div>")

def guidelines_page(request):
    return HttpResponse("<div style=\"text-align:center\"><h1>Guidelines Page</h1></div>")