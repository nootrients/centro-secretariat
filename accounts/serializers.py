from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from .models import CustomUser, Head, Officer, Scholar
from .models import UserProfile, HeadProfile, OfficerProfile, ScholarProfile



class AccountSerializer(serializers.ModelSerializer):
    """Serializer for all the registered accounts in the system."""

    lookup_field = 'username'
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "role", "date_joined", "is_active", "is_superuser")
    
    def create(self, validated_data):
        # Extract the password from validated_data and hash it
        password = validated_data.get('password')
        hashed_password = make_password(password)

        print(f'Password: {password}')
        print(f'Hashed Password: {hashed_password}')

        # Create the user with the hashed password
        user = CustomUser(**validated_data)
        user.set_password(hashed_password)  # Set the hashed password
        user.save()

        return user


class AccountDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving account details, excluding the password field."""

    lookup_field = 'username'

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "date_joined", "is_active")


class HeadSerializer(serializers.ModelSerializer):
    """Serializer for the Head Officer role user."""

    class Meta:
        model = Head
        fields = ("id", "username", "email", "is_active", "date_joined")


class OfficerSerializer(serializers.ModelSerializer):
    """Serializer for the Officer role user."""

    class Meta:
        model = Officer
        fields = ("id", "username", "email", "is_active", "date_joined")


class ScholarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scholar
        fields = ("id", "username", "email", "is_active", "date_joined")


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        
        def to_representation(self, instance):
            data = super().to_representation(instance)
            
            if "username" in data:
                del data["username"]
            
            return data


# =========================================================================================================================


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "user",
            "firstname",
            "lastname",
            "middlename",
            "contactnumber",
            "house_address",
            "barangay",
            "district",
            "birthdate",
            "age"
        )

    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        return obj.calculate_age()


class HeadProfileSerializer(serializers.ModelSerializer):
    # Serializer for retrieving the personal information of a Head Officer

    class Meta:
        model = HeadProfile
        fields = (
            "user",
            "firstname",
            "lastname",
            "middlename",
            "contactnumber",
            "house_address",
            "barangay",
            "district",
            "birthdate",
            "age"
        )

    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        return obj.calculate_age()

class OfficerProfileSerializer(serializers.ModelSerializer):
    # Serializer for retrieving the personal information of a Head Officer

    class Meta:
        model = OfficerProfile
        fields = (
            "user",
            "firstname",
            "lastname",
            "middlename",
            "contactnumber",
            "house_address",
            "barangay",
            "district",
            "birthdate"
        )


class ScholarProfileSerializer(serializers.ModelSerializer):
    # Serializer for retrieving the personal information of an existing Scholar

    class Meta:
        model = ScholarProfile
        fields = (
            "user",
            "firstname",
            "lastname",
            "middlename",
            "contactnumber",
            "house_address",
            "barangay",
            "district",
            "birthdate",
            "religion",
            "facebook_link",
            "years_of_residency",
            "scholarship_type"
        )


#Authentication Section

"""
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label='User ID', 
        write_only=True
    )
    
    password = serializers.CharField(
        label='Password',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and Password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Authenticate using Django Auth framework
            user = authenticate(request=self.context.get('request'), 
                                username=username, password=password)
            
            if user is not None:
                if user.role == 'Head':
                    # Head Officer
                    pass
                elif user.role == 'Officer':
                    # Officers
                    pass
                elif user.role == 'Scholar':
                    # Scholars
                    pass
            else:
                msg = 'Access denied: Wrong username or Password.'
                raise serializers.ValidationError(msg, code='authorization')
            
        else:
            msg = 'Both "Username" and "Password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs
"""
