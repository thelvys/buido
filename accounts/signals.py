from django.utils import timezone 
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile


from config import settings


# Signal pour mettre à jour les dates de début lors d'un changement
@receiver(post_save, sender=Profile)
def update_start_dates(sender, instance, **kwargs):
    if instance.department and instance.department_start_date is None:
        instance.department_start_date = timezone.now()
        instance.save()
    if instance.position and instance.position_start_date is None:
        instance.position_start_date = timezone.now()
        instance.save()

# Signal pour créer le profil lors de la création de l'utilisateur
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)