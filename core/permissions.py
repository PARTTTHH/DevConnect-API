from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit or delete it.
    Assumes the model instance has an owner, uthor, or user attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        owner = getattr(obj, 'owner', None) or getattr(obj, 'author', None) or getattr(obj, 'user', None)
        if owner is not None:
            return owner == request.user
        return False


class IsDeveloper(permissions.BasePermission):
    """
    Allows access only to authenticated users with the DEVELOPER role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'DEVELOPER' or request.user.is_staff)
        )


class IsRecruiter(permissions.BasePermission):
    """
    Allows access only to authenticated users with the RECRUITER role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'RECRUITER' or request.user.is_staff)
        )


class IsAdminUserOnly(permissions.BasePermission):
    """
    Allows access only to superusers/staff.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
