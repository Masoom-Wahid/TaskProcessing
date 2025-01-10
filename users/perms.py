from rest_framework.permissions import BasePermission


class IsVerified(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_verified:
            return True
        return False 
