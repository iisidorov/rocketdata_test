from rest_framework.permissions import BasePermission


class IsApiAllowed(BasePermission):
    """
    Allows access only to User in "Have API access Group".
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and
                    user.groups.filter(name='Have API access Group').exists())
