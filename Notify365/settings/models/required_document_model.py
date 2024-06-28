from django.db import models
from security.models import CustomUser as User
from simple_history.models import HistoricalRecords
from security.models import Suscription

class RequiredDocument(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_required_document')
    suscription = models.ForeignKey(Suscription, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name
