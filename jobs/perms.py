from users.perms import IsVerified

class IsVerifiedAndTaskOwner(IsVerified):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user 
