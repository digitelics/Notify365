from django.db import models
from security.models import CustomUser as User
from security.models import Suscription
from settings.models import ProviderType
from simple_history.models import HistoricalRecords

class Provider(models.Model):
    provider = models.CharField(max_length=255)
    suscription = models.ForeignKey(Suscription, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_provider')
    provider_type = models.ForeignKey(ProviderType, on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.provider