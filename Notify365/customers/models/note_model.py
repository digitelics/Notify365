from django.db import models
from simple_history.models import HistoricalRecords
from customers.models.customer_model import Customer
from security.models import CustomUser as User

class Note(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notes_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'Note for {self.customer} by {self.created_by} on {self.date}'

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
