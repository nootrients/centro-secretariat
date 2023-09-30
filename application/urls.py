from django.urls import path
from . import views

urlpatterns = [
    path('', views.application_index, name = 'application_index'),
    path('apply/policyProcedure/', views.policy_procedure, name = 'policy_procedure'),
    path('apply/forms/', views.submit_application, name = 'submit_application'),
]