from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404

from django.contrib.auth.hashers import make_password

from accounts.models import CustomUser, Head, Officer, Scholar
from accounts.models import UserProfile, HeadProfile, OfficerProfile, ScholarProfile

from accounts.serializers import AccountSerializer, AccountDetailSerializer, HeadSerializer, OfficerSerializer, ScholarSerializer
from accounts.serializers import UserProfileSerializer, HeadProfileSerializer, OfficerProfileSerializer, ScholarProfileSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class HeadList(generics.ListAPIView):
    """Retrieves all the registered users who has the role of `HEAD`."""
    queryset = Head.objects.all()
    serializer_class = HeadSerializer


class OfficerList(generics.ListAPIView):
    """Retrieves all the registered users who has the role of `OFFICER`."""
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer


class ScholarList(generics.ListAPIView):
    """Retrieves all the registered users who has the role of `SCHOLAR`."""
    queryset = Scholar.objects.all()
    serializer_class = ScholarSerializer


class AccountViewSet(ModelViewSet):
    """Retrieves all the currently registered users regardless of their roles (Head, Officers, Scholars). Also allows the superuser to `CREATE`, `READ`, `UPDATE`, and `DELETE`."""
    queryset = CustomUser.objects.all()
    serializer_class = AccountSerializer
    
    lookup_field = 'username'

    #permission_classes=[IsAuthenticated]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: self.kwargs['username']}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj
    
    @action(detail=False, methods=['POST'])
    def create_user(self, request):
        """Allows the superuser to manually `CREATE` a user. There is no need to specify an entry for the field `Username` as it is automatically generated and formatted."""
        if request.method == 'POST':
            # Assuming you have a JSON request data with a "password" and "role" field
            password = request.data.get('password')
            role = request.data.get('role')
            email = request.data.get('email')

            # Hash the password
            hashed_password = make_password(password)

            # Create and save the user with the hashed password
            user = CustomUser(username=request.data.get('username'), password=hashed_password, email=email, role=role)
            user.set_password(password)
            user.save()

            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['GET'])
    def get_users_by_role(self, request):
        role = request.query_params.get('role', None)  # Get the 'role' parameter from the request || :8000/accounts/users/get_user_by_role/?role=OFFICER

        if role is not None:
            # Filter users by role
            users = CustomUser.objects.filter(role=role)
            serializer = AccountSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {'detail': 'Please provide a role parameter in the request'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileListView(generics.ListAPIView):
    """A view that lists ALL the User Profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


"""
!!! DEPRECATED !!!

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'user__username'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(UserProfile, user__username=username)
"""


class HeadProfileViewSet(generics.ListAPIView):
    """Retrieves all the profiles of users who has the role `HEAD`."""
    queryset = HeadProfile.objects.all()
    serializer_class = HeadProfileSerializer

    def get_queryset(self):
        # Filter the queryset to only include profiles associated with Head Officers
        return HeadProfile.objects.filter(user__role=CustomUser.Role.HEAD)


class OfficerProfileViewSet(generics.ListAPIView):
    """Retrieves all the profiles of users who has the role `OFFICER`."""
    queryset = OfficerProfile.objects.all()
    serializer_class = OfficerProfileSerializer

    def get_queryset(self):
        # Filter the queryset to only include profiles associated with Officers
        return OfficerProfile.objects.filter(user__role=CustomUser.Role.OFFICER)


class ScholarProfileViewSet(generics.ListAPIView):
    """Retrieves all the profiles of users who has the role `SCHOLAR`."""
    queryset = ScholarProfile.objects.all()
    serializer_class = ScholarProfileSerializer

    def get_queryset(self):
        # Filter the queryset to only include profiles associated with Scholars
        return ScholarProfile.objects.filter(user__role=CustomUser.Role.SCHOLAR)


class HeadProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieves the profile of a specific Head Officer."""
    queryset = HeadProfile.objects.all()
    serializer_class = HeadProfileSerializer
    lookup_field = 'user__username'
    #permission_classes = [IsAuthenticated]

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(HeadProfile, user__username=username)
    

class OfficerProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieves the profile of a specific Head Officer."""
    queryset = OfficerProfile.objects.all()
    serializer_class = OfficerProfileSerializer
    lookup_field = 'user__username'
    #permission_classes = [IsAuthenticated]

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(OfficerProfile, user__username=username)
    

class ScholarProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieves the profile of a specific Head Officer."""
    queryset = ScholarProfile.objects.all()
    serializer_class = ScholarProfileSerializer
    lookup_field = 'user__username'
    #permission_classes = [IsAuthenticated]

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(ScholarProfile, user__username=username)


class AccountDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AccountDetailSerializer
    lookup_field = 'username'
    #permission_classes = [IsAuthenticated]

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(CustomUser, username=username)
    
    def update_user(self, request):
        """Allows the superuser `VIEW` to manually `UPDATE` a user instance. There is no need to specify an entry for the field `Username` as it is automatically generated and formatted."""
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


# One Login module for all types of Users
# POST - UID and Password

def login(request):
    return HttpResponse('<div style="text-align:center"><h1>Login Page</h1></div>')