# myapp/permissions.py

from django.contrib.auth.models import Permission

class CanApproveRequisition(permissions.BasePermission):
    """Permission pour approuver une demande."""

    def has_permission(self, request, view):
        return request.user.has_perm('myapp.can_approve_requisition')

class CanRejectRequisition(permissions.BasePermission):
    """Permission pour rejeter une demande."""

    def has_permission(self, request, view):
        return request.user.has_perm('myapp.can_reject_requisition')
