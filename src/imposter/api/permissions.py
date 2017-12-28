from rest_framework import permissions


class IsObjectEditable(permissions.BasePermission):
    """
    Only permit modifications if object editable.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return obj.editable

        return True
