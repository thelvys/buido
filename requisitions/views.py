from django.shortcuts import render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .permissions import CanApproveRequisition, CanRejectRequisition
from .models import Requisition

class RequisitionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Requisition
    template_name = 'requisition_detail.html'
    permission_classes = [CanApproveRequisition | CanRejectRequisition]  

    def post(self, request, *args, **kwargs):
        requisition = self.get_object()
        if 'approve' in request.POST and request.user.has_perm('myapp.can_approve_requisition'):
            requisition.approve(request.user)
        elif 'reject' in request.POST and request.user.has_perm('myapp.can_reject_requisition'):
            requisition.reject(request.user)
        return redirect(requisition.get_absolute_url())
