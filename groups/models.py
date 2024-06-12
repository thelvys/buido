from django.utils import timezone
from django.db import models
from treebeard.mp_tree import MP_Node

from config import settings

class Department(MP_Node):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_departments')

    def __str__(self):
        return self.name

    node_order_by = ['name'] # Order nodes by name
    


class DepartmentSupervisorHistory(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.department} - {self.supervisor} ({self.start_date} - {self.end_date})"
    

class DepartmentMember(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('department', 'user', 'end_date')

    def __str__(self):
        return f"{self.user} - {self.department} ({self.start_date} - {self.end_date})"
    

class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.name
    
class Category(MP_Node):
    name = models.CharField(_("Nom"), max_length=255)

    node_order_by = ['name'] 

    def __str__(self):
        return self.name
    


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # Ex: USD, CDF, EUR
    name = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.code