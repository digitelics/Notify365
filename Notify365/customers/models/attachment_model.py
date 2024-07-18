'''
DEPRECATED DO NOT USE

'''

from django.db import models
from simple_history.models import HistoricalRecords
from customers.models import Customer  # Ajusta la importación según tu estructura de carpetas
from settings.models import RequiredDocument
from security.models import CustomUser as User

class Attachment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='attachments')
    document = models.ForeignKey(RequiredDocument, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='static/files/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='attachments_uploaded')
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    history = HistoricalRecords()

    def __str__(self):
        return f'Attachment for {self.customer} - {self.document} uploaded by {self.uploaded_by}'

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'

