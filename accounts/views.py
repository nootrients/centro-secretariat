import django_filters

from .custom_mixins import AllowPUTAsCreateMixin

from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404

from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import Group
from django.db.models import Q

from accounts.models import CustomUser, Head, Officer, Scholar
from accounts.models import UserProfile, HeadProfile, OfficerProfile, ScholarProfile

from accounts.serializers import DisplayAccountListSerializer, OfficerCreateSerializer, CustomUserDetailSerializer, RegisterUserSerializer, ChangePasswordSerializer
from accounts.serializers import UserProfileSerializer, ScholarDetailSerializer

from accounts.permissions import IsLinkedUser, IsHeadOfficer, IsAdminOfficer, IsSelfOrAdminUser

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAdminUser, DjangoModelPermissions, IsAuthenticated

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role
        token['isActive'] = user.is_active # new | Add is_active to payload for verifying if the user trying to log in is an active user or not

        return token
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
            

class UserProfileDetail(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Get the role of the user making the request
        user_role = self.request.user.role

        # Choose the serializer based on the user's role
        if user_role == CustomUser.Role.HEAD or user_role == CustomUser.Role.OFFICER:
            return UserProfileSerializer
        elif user_role == CustomUser.Role.SCHOLAR:
            return UserProfileSerializer

    def get_object(self):
        # Get the user profile of the currently logged-in user
        return self.request.user.profile
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=instance, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordAPIView(generics.UpdateAPIView):
    """
    Endpoint for changing the logged in user instance's password.
    """

    permission_classes = [IsAuthenticated, ]
    
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        # Check if old_password's value matches with the current password of the user instance.
        if not request.user.check_password(old_password):
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Change password
        request.user.set_password(new_password)
        request.user.save()

        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)
    

class StaffFilter(django_filters.FilterSet):
    ROLE_CHOICES = [
        (CustomUser.Role.HEAD, 'Head'),
        (CustomUser.Role.OFFICER, 'Officer'),
    ]

    role = django_filters.ChoiceFilter(choices=ROLE_CHOICES, method='filter_role')

    class Meta:
        model = CustomUser
        fields = {
            'is_active': ['exact'],
        }

    def filter_role(self, queryset, name, value):
        if value:
            return queryset.filter(Q(role=value))
        return queryset
    

class ScholarFilter(django_filters.FilterSet):
    SCHOLARSHIP_TYPE_CHOICES = [
        ("BASIC PLUS SUC", "BASIC PLUS SUC"),
        ("SUC_LCU", "SUC/LCU"),
        ("BASIC SCHOLARSHIP", "BASIC SCHOLARSHIP"),
        ("HONORS", "HONORS (FULL)"),
        ("PRIORITY", "PRIORITY"),
        ("PREMIER", "PREMIER")
    ]
    
    scholarship_type = django_filters.ChoiceFilter(choices=SCHOLARSHIP_TYPE_CHOICES, method='filter_scholarship_type')
    
    class Meta:
        model = ScholarProfile
        fields = {
            'scholarship_type': ['exact'],
            'is_graduating': ['exact'],
            'user__is_active': ['exact'],
        }

    def filter_scholarship_type(self, queryset, name, value):
        if value:
            return queryset.filter(Q(scholarship_type=value))
        return queryset
    

class StaffList(generics.ListAPIView):
    """
    Endpoint for LISTING all the Head Officer and Officer accounts/users.
    """
    
    permission_classes = [IsHeadOfficer, ]

    queryset = CustomUser.objects.filter(Q(role=CustomUser.Role.HEAD) | Q(role=CustomUser.Role.OFFICER))
    serializer_class = DisplayAccountListSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = StaffFilter


class ScholarList(generics.ListAPIView):
    """
    Endpoint for LISTING all the Scholars accounts/users.
    """

    permission_classes = [IsHeadOfficer, ]

    queryset = ScholarProfile.objects.all()
    serializer_class = ScholarDetailSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = ScholarFilter
    

class CustomUserDetailView(generics.RetrieveUpdateAPIView):
    """
    Endpoint for retrieving the User instance together with its reference profile.
    """
    
    permission_classes = [IsHeadOfficer, ]

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer
    lookup_field = 'username'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

class CreateOfficer(generics.CreateAPIView):
    """
    Endpoint for creating an Officer instance.
    """
    
    permission_classes = [IsHeadOfficer, ]
    serializer_class = OfficerCreateSerializer


class ScholarDetailView(generics.RetrieveUpdateAPIView):
    """
    Endpoint for retrieving the Scholar instance together with its reference profile.
    """
    
    permission_classes = [IsHeadOfficer, ]

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer
    lookup_field = 'username'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)