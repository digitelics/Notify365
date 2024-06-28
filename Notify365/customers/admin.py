from django.contrib import admin
from .models import Customer, Note, CustomerService, AdditionalContact, Attachment, CustomerDocument



admin.site.register(Customer)
admin.site.register(Note)
admin.site.register(CustomerService)
admin.site.register(AdditionalContact)
admin.site.register(Attachment)
admin.site.register(CustomerDocument)

