from rest_framework import permissions, generics, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from django.utils import timezone
from django.urls import reverse

from .serializers import PasswordResetSerializer, PasswordResetConfirmSerializer
from .models import PasswordReset

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class PasswordResetView(generics.CreateAPIView):
    """
    Endpoint for `Forgot Password`.
    Enables all the existing users to reset their password.
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        # Get email and retrieve the user with the given email
        email = self.request.data.get('email')
        user_model = get_user_model()
        user = user_model.objects.filter(email=email).first()

        print(user)
        print(email)

        # Generate a unique token
        token = default_token_generator.make_token(user)

        # Save the token in the database along with the user and expiration date
        reset_instance = PasswordReset.objects.create(
            user = user,
            token = token,
            expires_at = timezone.now() + timezone.timedelta(hours=1)
        )

        # Generate link for resetting password (with the token included)
        reset_url = reverse('forgot-password-confirm')
        reset_link = f"{self.request.build_absolute_uri(reset_url)}?token={token}"

        # Send email
        context = {
            "link": reset_link
        }

        html_message = render_to_string("content/forgot_password_email.html", context=context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject = "Password Reset",
            body = plain_message,
            from_email = None,
            to = [email,]
        )

        message.attach_alternative(html_message, "text/html")
        message.send()

        return Response({'message': 'Link for password reset request sent successfully'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.CreateAPIView):
    """
    Endpoint for setting the new password after password reset request.
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = PasswordResetConfirmSerializer

    def create(self, request, *args, **kwargs):
        token = self.request.query_params.get('token')                              # Get token from request
        password_reset = PasswordReset.objects.filter(token=token).first()          # Retrieve PasswordReset instance

        if not password_reset or password_reset.expires_at < timezone.now():
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Have new_password field in the front-end/request
        new_password = self.request.data.get('new_password')

        user = password_reset.user
        user.set_password(new_password)
        user.save()

        password_reset.delete()                                                     # Delete the PasswordReset instance to invalidate the token

        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)