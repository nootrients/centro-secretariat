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

    username = serializers.CharField(read_only=True)
    lookup_field = 'username'

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "date_joined", "is_active")
        # read_only_fields = ("username", )


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
        fields = '__all__'
        read_only_fields = ['user', 'district']

    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        return obj.calculate_age()


class HeadProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving the personal information of a Head Officer.
    """

    user = serializers.CharField(read_only=True)
    district = serializers.ChoiceField(read_only=True, choices=UserProfile.District)

    class Meta:
        model = HeadProfile
        fields = '__all__'
        read_only_field = ("user", "district")

    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        return obj.calculate_age()

class OfficerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving the personal information of an Officer.
    """

    #user = serializers.CharField(read_only=True)
    district = serializers.ChoiceField(read_only=True, choices=UserProfile.District)

    class Meta:
        model = OfficerProfile
        fields = '__all__'
        read_only_field = ("user", "district")

    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        return obj.calculate_age()


class ScholarProfileSerializer(serializers.ModelSerializer):
    # Serializer for retrieving the personal information of an existing Scholar

    class Meta:
        model = ScholarProfile
        fields = '__all__'
        read_only_fields = (
            "user", 
            "district",
            "years_of_residency",
            "scholarship_type",
            "is_graduating",
        )

    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        return obj.calculate_age()


class RegisterUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ("email", "password", "is_active")
        extra_kwargs = {"password": {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        
        return instance
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password must match.")
        return data