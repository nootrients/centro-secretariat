from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from .models import CustomUser, Head, Officer, Scholar
from .models import UserProfile, HeadProfile, OfficerProfile, ScholarProfile
from .utils import generate_random_password

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from drf_writable_nested.serializers import WritableNestedModelSerializer


class DisplayAccountListSerializer(serializers.ModelSerializer):
    """Serializer for all the registered accounts in the system."""

    lookup_field = 'username'

    class Meta:
        model = CustomUser
        fields = ("username", "email", "is_active", "role")


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
        read_only_fields = (
            'user',
        )

class CustomUserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'role',
            'is_active',
            'date_joined',
            'profile'
        )
        read_only_fields = (
            'username',
            'role',
            'date_joined',
        )

    def update(self, instance, validated_data):
        nested_serializer = self.fields['profile']
        nested_instance = instance.profile
        # note the data is `pop`ed
        nested_data = validated_data.pop('profile')
        nested_serializer.update(nested_instance, nested_data)
        # this will not throw an exception,
        # as `profile` is not part of `validated_data`
        return super(CustomUserDetailSerializer, self).update(instance, validated_data)


class ScholarDetailSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = ScholarProfile
        fields = (
            'username',
            'email',
            'years_of_residency',
            'scholarship_type',
            'is_graduating',
            'is_active'
        )
        read_only_fields = (
            "user", 
            "district",
            "years_of_residency",
            "scholarship_type",
            "is_graduating",
        )

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def get_is_active(self, obj):
        return obj.user.is_active

    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(data)  # Add this line to print the serialized data for debugging
        return data


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
    

class OfficerCreateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = Officer
        fields = (
            'email', 
            'profile',
        )
        read_only_fields = (
            'is_active',
            'date_joined',
        )
        extra_kwargs = {"password": {'write_only': True}}
        

    def create(self, validated_data):
        nested_serializer = self.fields['profile']
        nested_data = validated_data.pop('profile')

        validated_data['role'] = CustomUser.Role.OFFICER

        generated_password = generate_random_password()
        custom_user_instance = CustomUser.objects.create_user(**validated_data, password=generated_password)
        generated_username = custom_user_instance.username

        nested_data['user'] = custom_user_instance
        nested_serializer.create(nested_data)

        # Send email
        subject_email = 'Your account details'
        context = {
            "username": generated_username,
            "password": generated_password,
        }

        html_message = render_to_string("content/supply_officer_account.html", context=context)
        plain_message = strip_tags(html_message)

        message = EmailMultiAlternatives(
            subject=subject_email,
            body=plain_message,
            from_email=None,
            to=[validated_data['email'], ]
        )

        message.attach_alternative(html_message, "text/html")
        message.send()

        return custom_user_instance