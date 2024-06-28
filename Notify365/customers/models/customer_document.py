from django.db import models
from simple_history.models import HistoricalRecords
from customers.models import Customer
from settings.models import RequiredDocument
from security.models import CustomUser as User


class CustomerDocument(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    document = models.ForeignKey(RequiredDocument, on_delete=models.CASCADE, related_name='customer_documents')
    doc_path = models.FileField(upload_to='static/customer_documents/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_customer_documents')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.customer} - {self.document.name}'
