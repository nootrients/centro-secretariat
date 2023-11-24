from .custom_mixins import AllowPUTAsCreateMixin

from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404

from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import Group

from accounts.models import CustomUser, Head, Officer, Scholar
from accounts.models import UserProfile, HeadProfile, OfficerProfile, ScholarProfile

from accounts.serializers import AccountSerializer, AccountDetailSerializer, HeadSerializer, OfficerSerializer, ScholarSerializer, RegisterUserSerializer, ChangePasswordSerializer
from accounts.serializers import UserProfileSerializer, HeadProfileSerializer, OfficerProfileSerializer, ScholarProfileSerializer

from accounts.permissions import IsLinkedUser, IsHeadOfficer, IsAdminOfficer, IsSelfOrAdminUser

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import generics

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


class HeadList(generics.ListAPIView):
    """
    Retrieves all the registered users who has the role of `HEAD`.
    """
    
    permission_classes = [IsAdminUser | IsHeadOfficer]
    queryset = Head.objects.all()
    serializer_class = HeadSerializer


class OfficerList(generics.ListAPIView):
    """
    Retrieves all the registered users who has the role of `OFFICER`.
    """

    permission_classes = [IsAdminUser | IsHeadOfficer]
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer


class ScholarList(generics.ListAPIView):
    """
    Retrieves all the registered users who has the role of `SCHOLAR`.
    """

    permission_classes = [IsAdminUser | IsHeadOfficer]
    queryset = Scholar.objects.all()
    serializer_class = ScholarSerializer


class AccountList(generics.ListAPIView):
    """
    Retrieves all the currently registered users regardless of their roles (`HEAD`, `OFFICER`, `SCHOLAR`).
    Only the superuser shall be able to see the list.
    """

    permission_classes=[IsAdminUser | IsHeadOfficer]
    queryset = CustomUser.objects.all()
    serializer_class = AccountSerializer
    
    lookup_field = 'username'

    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: self.kwargs['username']}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj
            

class CreateOfficer(generics.CreateAPIView):
    """
    A view that enables the Administrator to create an `OFFICER` account.
    """

    permission_classes = [IsAdminUser]
    serializer_class = RegisterUserSerializer

    def post(self, request):
        reg_serializer = RegisterUserSerializer(data=request.data)

        if reg_serializer.is_valid():
            reg_serializer.validated_data['role'] = 'OFFICER'
            newuser = reg_serializer.save()

            if newuser:
                return Response(status=status.HTTP_201_CREATED)
        
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetail(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Get the role of the user making the request
        user_role = self.request.user.role

        # Choose the serializer based on the user's role
        if user_role == CustomUser.Role.HEAD or user_role == CustomUser.Role.OFFICER:
            return UserProfileSerializer
        elif user_role == CustomUser.Role.SCHOLAR:
            return ScholarProfileSerializer

    def get_object(self):
        # Get the user profile of the currently logged-in user
        return self.request.user.profile
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class HeadProfileDetail(AllowPUTAsCreateMixin, generics.RetrieveUpdateAPIView):
    """
    Retrieves the profile of a specific Head Officer.
    """

    permission_classes = [IsAuthenticated, ]
    queryset = HeadProfile.objects.all()
    serializer_class = HeadProfileSerializer
    lookup_field = 'user__username'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(HeadProfile, user__username=username)
    

class OfficerProfileDetail(AllowPUTAsCreateMixin, generics.RetrieveUpdateAPIView):
    """
    Retrieves the profile of a specific Officer.
    """

    permission_classes = [IsAuthenticated, IsAdminUser | IsHeadOfficer]
    queryset = OfficerProfile.objects.all()
    serializer_class = OfficerProfileSerializer
    lookup_field = 'user__username'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(OfficerProfile, user__username=username)
    

class ScholarProfileDetail(generics.RetrieveAPIView):
    """
    Retrieves the profile of a specific Scholar.
    """

    permission_classes = [IsAuthenticated, ]
    queryset = ScholarProfile.objects.all()
    serializer_class = ScholarProfileSerializer
    lookup_field = 'user__username'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(ScholarProfile, user__username=username)


class AccountDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieves the necessary details of the account.
    """

    permission_classes = [IsSelfOrAdminUser, IsAdminUser | IsHeadOfficer]
    queryset = CustomUser.objects.all()
    serializer_class = AccountDetailSerializer
    lookup_field = 'username'
    
    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(CustomUser, username=username)
    
    def update_user(self, request):
        """
        Allows the superuser `VIEW` to manually `UPDATE` a user instance. 
        There is no need to specify an entry for the field `Username` as it is automatically generated and formatted.
        """
        user = self.get_object()

        # Get the new password from the request
        new_password = request.data.get('password')

        # Hash the new password
        hashed_password = make_password(new_password)

        # Set the new hashed password
        user.set_password(hashed_password)

        # Save the user instance
        user.save()

        return Response({'message': 'User updated successfully.'}, status=status.HTTP_200_OK)


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