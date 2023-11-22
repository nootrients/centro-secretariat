from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import CustomUser

class IsAdminOfficer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a "Head Officer"
        return request.user.role == "ADMIN"

class IsHeadOfficer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a "Head Officer"
        return request.user.role == "HEAD"

class IsOfficer(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a "Head Officer"
        return request.user.role == "OFFICER"


class IsScholar(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a "Head Officer"
        return request.user.role == "SCHOLAR"


class IsSelfOrAdminUser(BasePermission):
    """
    Custom permission to allow users to view their own accounts.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is a superuser or is trying to access their own account
        return request.user.is_superuser or request.user.role == "ADMIN" or obj == request.user
    

class IsLinkedUser(BasePermission):
    """
    Custom permission class that enables the User to edit his or her linked profile.
    """

    message = "Editing profile is restricted to the only user linked to it."

    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the author of a post
        return obj.user == request.user
    

class IsLinkedApplicationUser(BasePermission):
    """
    Custom permission class that enables the user to edit his or her linked application.
    """

    message = "Editing application is restricted to the only user linked to it."

    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the application
        return obj.scholar.user_ptr == request.user