from django.db import models
from simple_history.models import HistoricalRecords
from django.utils import timezone
from security.models import CustomUser as User  # Ajusta la importación según tu estructura de carpetas
from customers.models import Customer  # Ajusta la importación según tu estructura de carpetas

class AdditionalContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Sibling', 'Sibling'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Cousin', 'Cousin'),
        ('Friend', 'Friend'),
        ('Other', 'Other'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='additional_contacts')
    contact = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='related_contacts')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='additional_contacts_created')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.customer} - {self.contact} ({self.relationship})'

    def save(self, *args, **kwargs):
        # Save the primary relationship
        super().save(*args, **kwargs)

        # Create the inverse relationship if it doesn't already exist
        inverse_relationship, created = AdditionalContact.objects.get_or_create(
            customer=self.contact,
            contact=self.customer,
            defaults={
                'relationship': self.get_inverse_relationship(),
                'created_by': self.created_by,
                'created_at': timezone.now(),
                'deleted_at': None
            }
        )

    def get_inverse_relationship(self):
        # Define inverse relationships if needed
        inverse_map = {
            'father': 'Offspring',
            'mother': 'Offspring',
            'son': 'father/mother',
            'daughter': 'father/mother',
            'husband': 'wife',
            'wife': 'husband',
            'sibling': 'Sibling',
            'uncle': 'niece/nephew',
            'aunt': 'niece/nephew',
            'cousin': 'cousin',
            'friend': 'friend',
            'other': 'other',
        }
        return inverse_map.get(self.relationship, 'other')

    class Meta:
        verbose_name = 'Additional Contact'
        verbose_name_plural = 'Additional Contacts'
