from rest_framework import permissions


class PanelAccessPermission(permissions.BasePermission):
    """
    Global permission check for 'myadmin.access_panel' permission.
    """
    message = "You don't have access to admin panel."

    def has_permission(self, request, view):
        return request.user.has_perm('myadmin.access_panel')
