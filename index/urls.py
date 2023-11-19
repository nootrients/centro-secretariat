from django.urls import path
from . import views

urlpatterns = [
    path("forgot-password/", views.PasswordResetView.as_view(), name="forgot-password"),
    path("forgot-password/confirm/", views.PasswordResetConfirmView.as_view(), name="forgot-password-confirm")
]