from rest_framework.permissions import BasePermission
from accounts.models import CustomUser


class IsHeadOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "head"


class IsOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "officer"


class IsScholar(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "scholar"
