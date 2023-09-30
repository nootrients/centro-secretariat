from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the head scholarship officer's index.")

def manageCriteria(request):
    return render(request, "manageCriteria.html")