from django.db import models
from security.models import CustomUser as User
from settings.models import State
from simple_history.models import HistoricalRecords

class Customer(models.Model):
    LEAD = 'lead'
    CLIENT = 'client'
    INACTIVE = 'inactive'
    
    STATUS_CHOICES = [
        (LEAD, 'Lead'),
        (CLIENT, 'Client'),
        (INACTIVE, 'Inactive'),
    ]

    MALE = 'male'
    FEMALE = 'female'

    GENDER_CHOICE =[
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='customers_created')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='customers')
    customer_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=LEAD)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, null=True, blank=True)
    do_not_disturb = models.BooleanField(default=False)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def formatted_phone(self):
        if len(self.phone) == 10 and self.phone.isdigit():
            return f'({self.phone[:3]}) {self.phone[3:6]}-{self.phone[6:]}'
        return self.phone
