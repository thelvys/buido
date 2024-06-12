import uuid
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import Permission

from config import settings
from groups.models import Department, Category, Currency, Position


class Attachment(models.Model):
    """Modèle pour stocker les pièces jointes aux demandes."""
    file = models.FileField(upload_to='attachments/')
    description = models.CharField(max_length=255, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    

class Requisition(models.Model):
    """Modèle représentant une demande de fonds."""

    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = (
        (STATUS_DRAFT, _("Brouillon")),
        (STATUS_SUBMITTED, _("Soumise")),
        (STATUS_APPROVED, _("Approuvée")),
        (STATUS_REJECTED, _("Rejetée")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, verbose_name="Demandeur")
    narration = models.CharField(max_length=250, verbose_name="Description")
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default=Currency.objects.get_or_create(is_default=True)[0])
    exchange_rate = models.DecimalField(max_digits=11, decimal_places=4, default=1, verbose_name="Taux de change")
    amount_local = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    cost_center = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, verbose_name="Centre de coût") 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Categorie") 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT, verbose_name="Statut")
    attachments = models.ManyToManyField(Attachment, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        ordering = ('-modified_at',)
        constraints = [
            models.UniqueConstraint(fields=['requester', 'narration'], name='unique_request_per_user') 
        ]
        verbose_name = "Demande de fonds"
        verbose_name_plural = "Demandes de fonds"
        permissions = [
            ("can_approve_requisition", "Peut approuver une demande"),
            ("can_reject_requisition", "Peut rejeter une demande"),
        ]

    def __str__(self):
        return self.narration

    def save(self, *args, **kwargs):
        if self.status == self.STATUS_SUBMITTED and not self.amount_local:
            self.amount_local = self.amount * self.exchange_rate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("requisition:detail", args=[str(self.id)])
    

class RequisitionShare(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name='shares', verbose_name="Demande")
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Partagé avec")
    can_approve = models.BooleanField(default=False, verbose_name="Peut approuver")

    class Meta:
        unique_together = ('requisition', 'shared_with')
        verbose_name = "Partage de demande"
        verbose_name_plural = "Partages de demande"

    def __str__(self):
        return f"Demande {self.requisition} partagée avec {self.shared_with}"
    
    def get_available_approvals(self):
        """Retourne les approbations disponibles pour cet utilisateur sur cette requête."""
        return self.requisition.get_available_approvals(self.shared_with)
    
class RequisitionApproval(models.Model):
    requisition_share = models.ForeignKey(RequisitionShare, on_delete=models.CASCADE, related_name='approvals')  # Modification ici
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('requisition_share', 'approver')  # Un approbateur ne peut approuver un partage qu'une fois
        ordering = ['position']

    def save(self, *args, **kwargs):
        if self.approved and not self.approved_at:
            self.approved_at = timezone.now()

        # Logique pour mettre à jour le statut de la requisition partagée
        all_approved = all(approval.approved for approval in self.requisition_share.approvals.all())  # Modification ici
        if all_approved:
            self.requisition_share.requisition.status = Requisition.STATUS_APPROVED
        else:
            self.requisition_share.requisition.status = Requisition.STATUS_PENDING 
        self.requisition_share.requisition.save()

        super().save(*args, **kwargs)