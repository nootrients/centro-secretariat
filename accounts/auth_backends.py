from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from .models import CustomUser

from django.contrib.auth import get_user_model


class HeadOfficerBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username, role="head")
        except CustomUser.DoesNotExist:
            return None

        if user.check_password(password):
            return user


"""
class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Authenticate the user based on username and password
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass  # Return None if user not found

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
"""
"""
class ScholarAuthentication(BaseAuthentication):
    # Custom Authentication for Scholar
    
    def authenticate(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return None
        
        try:
            scholar = Scholar.objects.get(username=username)
        except Scholar.DoesNotExist:
            return None
        
        if scholar.check_password(password):
            return (scholar, None)
        else:
            raise exceptions.AuthenticationFailed('Invalid Credentials')

class OfficerAuthentication(BaseAuthentication):
    # Custom Authentication for Officer

    def authenticate(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return None
        
        try:
            officer = Officer.objects.get(username=username)
        except Officer.DoesNotExist:
            return None
        
        if officer.check_password(password):
            return (officer, None)
        else:
            raise exceptions.AuthenticationFailed('Invalid Credentials')
"""
