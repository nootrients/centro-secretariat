from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about_page, name="about"),
    path("guidelines/", views.guidelines_page, name="guidelines"),
    path("application/", views.application_index, name="application_index"),
    path(
        "application/apply/policyProcedure/",
        views.policy_procedure,
        name="policy_procedure",
    ),
    path(
        "application/apply/forms/", views.submit_application, name="submit_application"
    ),
]
